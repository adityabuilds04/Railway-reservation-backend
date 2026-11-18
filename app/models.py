from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from sqlmodel import SQLModel, Field

def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    full_name: str = Field(max_length=120)
    password_hash: str
    role: str = Field(default="user", max_length=20)
    created_at: datetime = Field(default_factory=utc_now)

class Journey(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    train_number: str = Field(index=True, max_length=20)
    train_name: str = Field(max_length=120)
    source: str = Field(index=True, max_length=100)
    destination: str = Field(index=True, max_length=100)
    departure_at: datetime = Field(index=True)
    arrival_at: datetime
    total_seats: int
    available_seats: int
    created_at: datetime = Field(default_factory=utc_now)

class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reference: str = Field(default_factory=lambda: uuid4().hex[:12].upper(), index=True, unique=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    journey_id: int = Field(foreign_key="journey.id", index=True)
    seats: int
    status: str = Field(default="confirmed", index=True, max_length=20)
    created_at: datetime = Field(default_factory=utc_now)
