# Railway Reservation Backend

An individual learning project inspired by railway reservation systems. It demonstrates REST API design, authentication, role-based access, relational data, inventory updates, booking/cancellation workflows, and automated tests.

> This is an educational project, not an official IRCTC integration or a production-ready railway system. It does not process payments, issue real tickets, or connect to railway inventory.

## Features

- User registration and login
- Password hashing using Python's `hashlib.scrypt`
- JWT bearer-token authentication
- Admin-only journey creation
- Journey search by source, destination, and departure time
- Booking and cancellation
- Atomic conditional inventory decrement to reduce double-booking risk
- Conditional booking status transition to prevent double seat release
- OpenAPI documentation at `/docs`
- Pytest API tests
- SQLite for a simple local start; PostgreSQL support through `DATABASE_URL`
- Docker and Docker Compose examples

## 1. Run locally on Windows

Open this project folder in VS Code. In the VS Code terminal, run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

Open `.env` and replace `SECRET_KEY` with a long random secret (at least 32 characters). The included SQLite URL is suitable for local learning.

Start the API:

```powershell
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to try the endpoints. The database and tables are created automatically on startup.

## 2. Add sample journeys

In a second terminal with the virtual environment activated:

```powershell
python -m app.seed_demo
```

Then use `GET /journeys` in Swagger UI.

## 3. Create an administrator

```powershell
python -m app.create_admin
```

Enter the admin email and password when prompted. Never commit admin credentials or `.env` to Git.

Use `POST /auth/login` with that account, copy the returned `access_token`, then click **Authorize** in `/docs` and enter:

`Bearer YOUR_ACCESS_TOKEN`

The admin can now call `POST /journeys`.

## 4. Main endpoints

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/` | Public | API welcome |
| GET | `/health` | Public | Health check |
| POST | `/auth/register` | Public | Create a user |
| POST | `/auth/login` | Public | Get JWT token |
| GET | `/auth/me` | Authenticated | Current user |
| POST | `/journeys` | Admin | Create a journey |
| GET | `/journeys` | Public | Search journeys |
| GET | `/journeys/{journey_id}` | Public | Journey details |
| POST | `/bookings` | Authenticated | Book seats |
| GET | `/bookings/mine` | Authenticated | List your bookings |
| POST | `/bookings/{booking_id}/cancel` | Booking owner | Cancel a booking |

### Example: register

```json
{
  "email": "student@example.com",
  "full_name": "Student User",
  "password": "StrongPass123!"
}
```

### Example: login

```json
{
  "email": "student@example.com",
  "password": "StrongPass123!"
}
```

### Example: create a journey (admin token required)

```json
{
  "train_number": "12951",
  "train_name": "Example Express",
  "source": "New Delhi",
  "destination": "Mumbai Central",
  "departure_at": "2026-11-05T16:30:00",
  "arrival_at": "2026-11-06T09:00:00",
  "total_seats": 120
}
```

### Example: book seats

```json
{
  "journey_id": 1,
  "seats": 2
}
```

Search supports query parameters, for example:

`GET /journeys?source=New%20Delhi&destination=Jaipur`

Search text currently uses case-insensitive exact matching. `travel_date` is an optional ISO date-time lower bound.

## 5. Run tests

```powershell
python -m pytest -q
```

Tests use a temporary in-memory SQLite database and do not use the local `railway.db`.

## 6. PostgreSQL with Docker

Docker Desktop must be installed and running. For a local containerized run:

```powershell
docker compose up --build
```

This starts PostgreSQL and the API. The sample credentials in `docker-compose.yml` are for local development only. Change the database password and secret before using this beyond a local demo.

## 7. Suggested folder structure

```text
railway_reservation_backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── create_admin.py
│   ├── seed_demo.py
│   └── routers/
│       ├── __init__.py
│       ├── auth.py
│       ├── journeys.py
│       └── bookings.py
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 8. Important engineering notes / limitations

- The booking endpoint uses a conditional SQL `UPDATE` so inventory is decremented only if enough seats remain. The inventory change and booking insert are committed in one transaction.
- Cancellation uses a conditional status transition before returning seats, preventing the same booking from releasing seats twice when requests race.
- Run concurrency tests against PostgreSQL before making claims about production behavior. SQLite has different locking and concurrency behavior.
- This starter does not yet include payment processing, booking expiry, waitlists, seat/coach allocation, rate limiting, refresh tokens, structured audit logs, Alembic migrations, or production monitoring.
- A real production system would require further threat modeling, database migrations, observability, deployment hardening, load testing, and recovery procedures.
- For a formal course submission, compare every feature with the official problem statement and checklist once they are shared.
