from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field as PydanticField, model_validator
from sqlmodel import SQLModel

class RegisterRequest(SQLModel):
    email: EmailStr
    full_name: str = PydanticField(min_length=2, max_length=120)
    password: str = PydanticField(min_length=8, max_length=128)

class LoginRequest(SQLModel):
    email: EmailStr
    password: str = PydanticField(min_length=1, max_length=128)

class UserPublic(SQLModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    created_at: datetime

class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int

class JourneyCreate(SQLModel):
    train_number: str = PydanticField(min_length=1, max_length=20)
    train_name: str = PydanticField(min_length=2, max_length=120)
    source: str = PydanticField(min_length=2, max_length=100)
    destination: str = PydanticField(min_length=2, max_length=100)
    departure_at: datetime
    arrival_at: datetime
    total_seats: int = PydanticField(gt=0, le=10000)

    @model_validator(mode="after")
    def validate_journey(self):
        if self.source.strip().casefold() == self.destination.strip().casefold():
            raise ValueError("Source and destination must be different.")
        if self.arrival_at <= self.departure_at:
            raise ValueError("Arrival time must be after departure time.")
        return self

class JourneyPublic(SQLModel):
    id: int
    train_number: str
    train_name: str
    source: str
    destination: str
    departure_at: datetime
    arrival_at: datetime
    total_seats: int
    available_seats: int

class BookingCreate(SQLModel):
    journey_id: int
    seats: int = PydanticField(gt=0, le=6)

class BookingPublic(SQLModel):
    id: int
    reference: str
    user_id: int
    journey_id: int
    seats: int
    status: str
    created_at: datetime

class MessageResponse(SQLModel):
    message: str
    reference: Optional[str] = None
