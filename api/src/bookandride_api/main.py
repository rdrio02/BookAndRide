# ─────────────────────────────────────────────────────────────────────────────
# File: app/main.py
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations
from fastapi import FastAPI, Request, Depends, HTTPException, Query, status, Header
from fastapi.responses import Response, JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone
from pathlib import Path
import json
import xmltodict

from .auth import verify_api_key  
from .database import engine, Base, get_db
from . import models, schemas
from .search import index_book, search_books, index_rental
from .serialization import parse_body, negotiate, render_book, render_rental
from .logging_config import logger

# ─────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────
app = FastAPI(title="Book&Ride API", version="0.2.0")

# ─────────────────────────────────────────────
# Metrics
# ─────────────────────────────────────────────
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency (seconds)", ["path"])

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    path = request.url.path
    with REQUEST_LATENCY.labels(path).time():
        response = await call_next(request)
    REQUEST_COUNT.labels(request.method, path, str(response.status_code)).inc()
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ─────────────────────────────────────────────
# Database initialization
# ─────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─────────────────────────────────────────────
# Health endpoint
# ─────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "version": app.version}

# ─────────────────────────────────────────────
# Load JSON Schema for validation
# ─────────────────────────────────────────────
BOOK_SCHEMA = json.load(open(Path(__file__).parent / "schemas" / "book.schema.json"))
BOOK_UPDATE_SCHEMA = json.load(open(Path(__file__).parent / "schemas" / "book.update.schema.json"))

RENTAL_START_SCHEMA = json.load(open(Path(__file__).parent / "schemas" / "rental.start.schema.json"))
RENTAL_STOP_SCHEMA = json.load(open(Path(__file__).parent / "schemas" / "rental.stop.schema.json"))

# ─────────────────────────────────────────────
# Books endpoints (JSON + XML support)
# ─────────────────────────────────────────────

@app.get("/books", response_model=None)
def list_books(request: Request, db: Session = Depends(get_db), q: str | None = Query(default=None)):
    if q:
        results = search_books(q)
    else:
        stmt = select(models.Book).order_by(models.Book.id.asc())
        results = db.execute(stmt).scalars().all()

    books_data = [schemas.BookOut.model_validate(b).model_dump() for b in results]
    accept = negotiate(request.headers.get("Accept"))
    return render_book(books_data, accept)


@app.get("/books/{book_id}", response_model=None)
def get_book(book_id: int, request: Request, db: Session = Depends(get_db)):
    """Return one book by ID, supports JSON/XML."""
    book = db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    accept = negotiate(request.headers.get("Accept"))
    return render_book(schemas.BookOut.model_validate(book).model_dump(), accept)


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(request: Request, db: Session = Depends(get_db)):
    """Create a new book — supports JSON and XML input."""
    content_type = request.headers.get("Content-Type", "").split(";")[0]
    body = await request.body()

    # Deserialize & validate
    data = parse_body(body, content_type, BOOK_SCHEMA, schemas.BookCreate)

    # Store in DB
    book = models.Book(**data)
    db.add(book)
    db.commit()
    db.refresh(book)

    # Index in Elasticsearch
    index_book(book)

    # Serialize response
    accept = negotiate(request.headers.get("Accept"))
    return render_book(schemas.BookOut.model_validate(book).model_dump(), accept)


@app.put("/books/{book_id}", response_model=None)
async def update_book(book_id: int, request: Request, db: Session = Depends(get_db)):
    """Update a book — supports partial updates and JSON/XML/YAML input/output."""
    
    content_type = request.headers.get("Content-Type", "").split(";")[0]
    body = await request.body()

    # Parse using the partial update schema
    data = parse_body(body, content_type, BOOK_UPDATE_SCHEMA, schemas.BookUpdate)

    book = db.get(models.Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")

    # Only update fields that are present in the request
    for k, v in data.items():
        if v is not None:
            setattr(book, k, v)

    db.commit()
    db.refresh(book)

    accept = negotiate(request.headers.get("Accept"))
    return render_book(schemas.BookOut.model_validate(book).model_dump(), accept)



@app.delete("/books/{book_id}", response_model=None)
async def delete_book(book_id: int, request: Request, db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)
    if not book:
        raise HTTPException(404, "Book not found")

    db.delete(book)
    db.commit()

    accept = negotiate(request.headers.get("Accept"))
    return render_book({"detail": f"Book {book_id} deleted"}, accept)

@app.delete("/books", response_model=None)
async def delete_all_books(
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(verify_api_key),  # Require valid API key
):
    """Delete all books — supports JSON, XML, YAML output."""
    
    num_deleted = db.query(models.Book).delete()
    db.commit()

    accept = negotiate(request.headers.get("Accept"))
    return render_book({"detail": f"Deleted {num_deleted} books"}, accept)


# ─────────────────────────────────────────────
# Converter endpoint (JSON ⇄ XML)
# ─────────────────────────────────────────────
@app.post("/convert")
async def convert(request: Request, to: str):
    """
    Convert between JSON and XML.
    Usage:
      POST /convert?to=json  or  /convert?to=xml
    """
    content_type = request.headers.get("Content-Type", "").split(";")[0]
    body = await request.body()
    data = parse_body(body, content_type, BOOK_SCHEMA, schemas.BookCreate)

    if to == "json":
        return JSONResponse(content=data)
    elif to == "xml":
        xml = xmltodict.unparse({"book": data}, pretty=True)
        return Response(content=xml, media_type="application/xml")
    raise HTTPException(400, detail="Query param ?to=json|xml required")

# ─────────────────────────────────────────────
# Rentals endpoints
# ─────────────────────────────────────────────
PRICE_PER_MIN = 0.25
DAILY_CAP = 12.0

def calculate_price(minutes: int) -> float:
    """€0.25/min with €12/day cap."""
    price = min(minutes * PRICE_PER_MIN, DAILY_CAP)
    logger.info(f"Calculated price for {minutes} minutes: {price}")
    return price


@app.post("/rentals/start", response_model=None)
async def start_rental(
    request: Request,
    db: Session = Depends(get_db),
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
    user = Depends(verify_api_key),
):
    content_type = request.headers.get("Content-Type", "").split(";")[0]
    body = await request.body()

    # Parse XML or JSON
    data = parse_body(body, content_type, RENTAL_START_SCHEMA, schemas.RentalStartIn)

    logger.info(f"Received rental start data: {data}")

    bike_id = data["bike_id"].strip()
    user_id = data.get("user_id")

    now = datetime.now(timezone.utc)

    rental = models.Rental(
        user_id=data.get("user_id"),
        bike_id=data["bike_id"].strip(),
        started_at=now,
        stopped_at=None,
        total_minutes=0,
        price_eur=0.0,
    )
    db.add(rental)
    db.commit()
    db.refresh(rental)

    index_rental({
        "rental_id": rental.id,
        "user_id": rental.user_id,
        "bike_id": rental.bike_id,
        "started_at": rental.started_at.isoformat(),
        "stopped_at": None,
        "total_minutes": 0,
        "price_eur": 0.0
    })

    logger.info(f"Rental started (rental_id={rental.id}, user_id={user_id}, bike_id={bike_id})")

    accept = request.headers.get("Accept")
    return render_rental(
        data={"rental_id": rental.id, "started_at": rental.started_at.isoformat()},
        accept=accept
    )





def _to_aware_utc(dt: datetime) -> datetime:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

@app.post("/rentals/stop", response_model=None)
async def stop_rental(request: Request, db: Session = Depends(get_db), user=Depends(verify_api_key)):
    content_type = request.headers.get("Content-Type", "").split(";")[0]
    body = await request.body()
    data = parse_body(body, content_type, RENTAL_STOP_SCHEMA, schemas.RentalStopIn)

    logger.info(f"Received rental stop data: {data}")

    r = db.get(models.Rental, data["rental_id"])
    if not r:
        logger.warning(f"Rental not found: {data['rental_id']}")
        raise HTTPException(status_code=404, detail="Rental not found")
    if r.stopped_at is not None:
        logger.info(f"Rental {r.id} already stopped — returning cached values.")
        response_data = {"duration_min": r.total_minutes, "price_eur": r.price_eur}
        accept = request.headers.get("Accept")
        return render_rental(response_data, accept)

    now = datetime.now(timezone.utc)
    start = _to_aware_utc(r.started_at)
    minutes = max(0, int((now - start).total_seconds() // 60))
    price = calculate_price(minutes)

    r.stopped_at = now
    r.total_minutes = minutes
    r.price_eur = price
    db.commit()
    db.refresh(r)

    logger.info(f"Rental stopped (rental_id={r.id}, minutes={minutes}, price={price})")

    index_rental({
        "rental_id": r.id,
        "user_id": r.user_id,
        "bike_id": r.bike_id,
        "started_at": r.started_at.isoformat(),
        "stopped_at": r.stopped_at.isoformat(),
        "total_minutes": r.total_minutes,
        "price_eur": r.price_eur
    })

    accept = request.headers.get("Accept")
    return render_rental({"duration_min": minutes, "price_eur": price}, accept)
