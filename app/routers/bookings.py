from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import update
from sqlmodel import Session, select
from app.database import get_session
from app.dependencies import get_current_user
from app.models import Booking, Journey, User
from app.schemas import BookingCreate, BookingPublic, MessageResponse

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("", response_model=BookingPublic, status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    journey = session.get(Journey, data.journey_id)
    if journey is None:
        raise HTTPException(status_code=404, detail="Journey not found.")

    # Atomic conditional update: only one request can claim the same remaining inventory.
    # The WHERE clause and decrement execute as one database statement.
    result = session.execute(
        update(Journey)
        .where(Journey.id == data.journey_id, Journey.available_seats >= data.seats)
        .values(available_seats=Journey.available_seats - data.seats)
    )
    if result.rowcount != 1:
        session.rollback()
        raise HTTPException(status_code=409, detail="Not enough seats are available.")

    booking = Booking(user_id=current_user.id, journey_id=data.journey_id, seats=data.seats, status="confirmed")
    session.add(booking)
    try:
        session.commit()
        session.refresh(booking)
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Booking could not be completed. Please retry.")
    return booking

@router.get("/mine", response_model=list[BookingPublic])
def my_bookings(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    statement = select(Booking).where(Booking.user_id == current_user.id).order_by(Booking.created_at.desc())
    return list(session.exec(statement).all())

@router.post("/{booking_id}/cancel", response_model=MessageResponse)
def cancel_booking(
    booking_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    booking = session.get(Booking, booking_id)
    if booking is None or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found.")

    # Conditional status transition prevents two concurrent cancellation requests
    # from releasing the same seats twice.
    result = session.execute(
        update(Booking)
        .where(Booking.id == booking_id, Booking.user_id == current_user.id, Booking.status == "confirmed")
        .values(status="cancelled")
    )
    if result.rowcount != 1:
        session.rollback()
        raise HTTPException(status_code=409, detail="This booking has already been cancelled.")

    session.execute(
        update(Journey)
        .where(Journey.id == booking.journey_id)
        .values(available_seats=Journey.available_seats + booking.seats)
    )
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Cancellation could not be completed. Please retry.")
    return MessageResponse(message="Booking cancelled successfully.", reference=booking.reference)
