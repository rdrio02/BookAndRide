from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime

class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=200)
    stock: int = Field(ge=0)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=200)
    stock: int | None = Field(default=None, ge=0)


class BookOut(BookBase):
    id: int
    model_config = {"from_attributes": True}


class RentalStartIn(BaseModel):
    bike_id: str = Field(min_length=3, max_length=64)
    user_id: int | None = None

class RentalStartOut(BaseModel):
    rental_id: int
    started_at: datetime
    model_config = {"from_attributes": True}

class RentalStopIn(BaseModel):
    rental_id: int

class RentalStopOut(BaseModel):
    duration_min: int
    price_eur: float
