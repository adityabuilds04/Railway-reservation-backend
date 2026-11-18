from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from app.database import get_session
from app.dependencies import require_admin
from app.models import Journey, User
from app.schemas import JourneyCreate, JourneyPublic

router = APIRouter(prefix="/journeys", tags=["Journeys"])

@router.post("", response_model=JourneyPublic, status_code=status.HTTP_201_CREATED)
def create_journey(
    data: JourneyCreate,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    journey = Journey(
        **data.model_dump(),
        available_seats=data.total_seats,
    )
    session.add(journey)
    session.commit()
    session.refresh(journey)
    return journey

@router.get("", response_model=list[JourneyPublic])
def search_journeys(
    source: str | None = Query(default=None, min_length=2, max_length=100),
    destination: str | None = Query(default=None, min_length=2, max_length=100),
    travel_date: datetime | None = Query(default=None, description="Optional date/time lower bound, e.g. 2026-11-01T00:00:00"),
    session: Session = Depends(get_session),
):
    statement = select(Journey)
    if source:
        statement = statement.where(Journey.source.ilike(source.strip()))
    if destination:
        statement = statement.where(Journey.destination.ilike(destination.strip()))
    if travel_date:
        statement = statement.where(Journey.departure_at >= travel_date)
    statement = statement.order_by(Journey.departure_at).limit(100)
    return list(session.exec(statement).all())

@router.get("/{journey_id}", response_model=JourneyPublic)
def get_journey(journey_id: int, session: Session = Depends(get_session)):
    journey = session.get(Journey, journey_id)
    if journey is None:
        raise HTTPException(status_code=404, detail="Journey not found.")
    return journey
