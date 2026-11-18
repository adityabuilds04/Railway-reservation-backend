from datetime import datetime, timedelta
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import get_session
from app.models import User, Journey
from app.security import hash_password

@pytest.fixture()
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)

    def override_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    with Session(test_engine) as session:
        session.add(User(email="admin@example.com", full_name="Test Admin", password_hash=hash_password("AdminPass123!"), role="admin"))
        session.add(User(email="user@example.com", full_name="Test User", password_hash=hash_password("UserPass123!"), role="user"))
        departure = datetime.now() + timedelta(days=2)
        session.add(Journey(
            train_number="T100", train_name="Test Express", source="Delhi", destination="Agra",
            departure_at=departure, arrival_at=departure + timedelta(hours=3),
            total_seats=1, available_seats=1,
        ))
        session.commit()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(test_engine)
    test_engine.dispose()

def login(client, email, password):
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_login_and_me(client):
    token = login(client, "user@example.com", "UserPass123!")
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
    assert "password_hash" not in response.json()

def test_user_cannot_create_journey(client):
    token = login(client, "user@example.com", "UserPass123!")
    departure = (datetime.now() + timedelta(days=4)).isoformat()
    arrival = (datetime.now() + timedelta(days=4, hours=2)).isoformat()
    response = client.post("/journeys", headers={"Authorization": f"Bearer {token}"}, json={
        "train_number": "T200", "train_name": "Another Express", "source": "Delhi", "destination": "Agra",
        "departure_at": departure, "arrival_at": arrival, "total_seats": 20
    })
    assert response.status_code == 403

def test_booking_decrements_inventory_and_cancellation_restores_it(client):
    token = login(client, "user@example.com", "UserPass123!")
    headers = {"Authorization": f"Bearer {token}"}
    booking = client.post("/bookings", headers=headers, json={"journey_id": 1, "seats": 1})
    assert booking.status_code == 201
    assert booking.json()["status"] == "confirmed"

    unavailable = client.post("/bookings", headers=headers, json={"journey_id": 1, "seats": 1})
    assert unavailable.status_code == 409

    cancelled = client.post(f"/bookings/{booking.json()['id']}/cancel", headers=headers)
    assert cancelled.status_code == 200

    booked_again = client.post("/bookings", headers=headers, json={"journey_id": 1, "seats": 1})
    assert booked_again.status_code == 201
