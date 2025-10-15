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
from .serialization import parse_body, negotiate, render  # <─ your helper functions

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
RENTAL_SCHEMA = json.load(open(Path(__file__).parent / "schemas" / "rental.schema.json"))


# ─────────────────────────────────────────────
# Books endpoints (JSON + XML support)
# ─────────────────────────────────────────────

@app.get("/books", response_model=None)
def list_books(
    request: Request,
    db: Session = Depends(get_db),
    q: str | None = Query(default=None, description="Search in title or author"),
):
    """Return list of books — JSON or XML depending on Accept header."""
    if q:
        results = search_books(q)
    else:
        stmt = select(models.Book).order_by(models.Book.id.asc())
        results = db.execute(stmt).scalars().all()

    books_data = [schemas.BookOut.model_validate(b).model_dump() for b in results]
    accept = negotiate(request.headers.get("Accept"))

    if accept == "application/xml":
        xml = xmltodict.unparse({"books": {"book": books_data}}, pretty=True)
        return Response(content=xml, media_type="application/xml")

    return JSONResponse(content=books_data)



@app.get("/books/{book_id}", response_model=None)
def get_book(book_id: int, request: Request, db: Session = Depends(get_db)):
    """Return one book by ID, supports JSON/XML."""
    book = db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    accept = negotiate(request.headers.get("Accept"))
    return render(schemas.BookOut.model_validate(book).model_dump(), accept)


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
    return render(schemas.BookOut.model_validate(book).model_dump(), accept)


@app.put("/books/{book_id}", response_model=schemas.BookOut)
def update_book(book_id: int, payload: schemas.BookUpdate, db: Session = Depends(get_db)):
    """Update a book (JSON only)."""
    book = db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(book, k, v)

    db.commit()
    db.refresh(book)
    return book


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete a book."""
    book = db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()
    return None

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
    return min(minutes * PRICE_PER_MIN, DAILY_CAP)

@app.post("/rentals/start", response_model=schemas.RentalStartOut, status_code=status.HTTP_201_CREATED)
def start_rental(
    payload: schemas.RentalStartIn,
    user = Depends(verify_api_key),
    db: Session = Depends(get_db),
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
):
    user_id = x_user_id or payload.user_id or 1
    now = datetime.now(timezone.utc)

    rental = models.Rental(
        user_id=user_id,
        bike_id=payload.bike_id.strip(),
        started_at=now,
        stopped_at=None,
        total_minutes=0,
        price_eur=0.0,
    )
    db.add(rental)
    db.commit()
    db.refresh(rental)

    # Index in Elasticsearch
    index_rental({
        "rental_id": rental.id,
        "user_id": rental.user_id,
        "bike_id": rental.bike_id,
        "started_at": rental.started_at.isoformat(),
        "stopped_at": None,
        "total_minutes": 0,
        "price_eur": 0.0
    })

    return schemas.RentalStartOut(rental_id=rental.id, started_at=rental.started_at)


def _to_aware_utc(dt: datetime) -> datetime:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

@app.post("/rentals/stop", response_model=schemas.RentalStopOut)
def stop_rental(payload: schemas.RentalStopIn, user = Depends(verify_api_key), db: Session = Depends(get_db)):
    r = db.get(models.Rental, payload.rental_id)
    if not r:
        raise HTTPException(status_code=404, detail="Rental not found")
    if r.stopped_at is not None:
        return {"duration_min": r.total_minutes, "price_eur": r.price_eur}

    now = datetime.now(timezone.utc)
    start = _to_aware_utc(r.started_at)
    minutes = max(0, int((now - start).total_seconds() // 60))
    price = calculate_price(minutes)

    r.stopped_at = now
    r.total_minutes = minutes
    r.price_eur = price
    db.commit()
    db.refresh(r)

    index_rental({
        "rental_id": r.id,
        "user_id": r.user_id,
        "bike_id": r.bike_id,
        "started_at": r.started_at.isoformat(),
        "stopped_at": r.stopped_at.isoformat(),
        "total_minutes": r.total_minutes,
        "price_eur": r.price_eur
    })

    return {"duration_min": minutes, "price_eur": price}
