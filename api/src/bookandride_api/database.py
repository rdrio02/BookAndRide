from __future__ import annotations
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
# sqlite needs check_same_thread=False for single-threaded FastAPI dev server
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}


engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


# Dependency for FastAPI routes
from typing import Generator

def get_db() -> Generator:
     db = SessionLocal()
     try:
         yield db
     finally:
         db.close()
