# ─────────────────────────────────────────────────────────────────────────────
# File: app/main.py
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations
from fastapi import FastAPI, Request, Depends, HTTPException, Query, status, Header
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from .auth import verify_api_key  
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone
from .database import engine, Base, get_db
from . import models, schemas


app = FastAPI(title="Book&Ride API", version="0.1.0")

# define metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency (seconds)",
    ["path"],
)

# simple metrics middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    path = request.url.path

    with REQUEST_LATENCY.labels(path).time():
        response = await call_next(request)

    REQUEST_COUNT.labels(request.method, path, str(response.status_code)).inc()
    return response

# expose /metrics in Prometheus text format
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Create tables automatically for the lab (for production use Alembic)
Base.metadata.create_all(bind=engine)

# Health & Info
@app.get("/health")
def health():
    return {"status": "ok", "version": app.version}

# Books — list/search
@app.get("/books", response_model=list[schemas.BookOut])
def list_books(
    q: str | None = Query(default=None, description="Search in title or author"),
    db: Session = Depends(get_db),
):
    stmt = select(models.Book)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            (models.Book.title.ilike(like)) | (models.Book.author.ilike(like))
        )
    stmt = stmt.order_by(models.Book.id.asc())
    rows = db.execute(stmt).scalars().all()
    return rows


# Create book
@app.post("/books", response_model=schemas.BookOut, status_code=status.HTTP_201_CREATED)
def create_book(payload: schemas.BookCreate, db: Session = Depends(get_db)):
    book = models.Book(**payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

# --- Update book ---
@app.put("/books/{book_id}", response_model=schemas.BookOut)
def update_book(
    book_id: int,
    payload: schemas.BookUpdate,
    db: Session = Depends(get_db),
):
    book = db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(book, k, v)

    db.add(book)
    db.commit()
    db.refresh(book)
    return book


# --- Delete book ---
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return None

# ---------- Rentals ----------

PRICE_PER_MIN = 0.25
DAILY_CAP = 12.0

def calculate_price(minutes: int) -> float:
    """€0.25/min with €12/day cap."""
    base = minutes * PRICE_PER_MIN
    return min(base, DAILY_CAP)

@app.post("/rentals/start", response_model=schemas.RentalStartOut, status_code=status.HTTP_201_CREATED)
def start_rental(
    payload: schemas.RentalStartIn,
    user = Depends(verify_api_key),     # <-- protect with API key
    db: Session = Depends(get_db),
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
):
    """
    Start a rental.
    - user_id is taken from header `X-User-Id` if present; otherwise from body; otherwise defaults to 1 (lab).
    """
    user_id = x_user_id or payload.user_id or 1  # simple lab-friendly fallback
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

    return schemas.RentalStartOut(rental_id=rental.id, started_at=rental.started_at)

def _to_aware_utc(dt: datetime) -> datetime:
    if dt is None:
        return None
    # If naive (no tzinfo), assume it was UTC and attach tz
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    # If tz-aware, convert to UTC
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
    db.add(r); db.commit(); db.refresh(r)

    return {"duration_min": minutes, "price_eur": price}
