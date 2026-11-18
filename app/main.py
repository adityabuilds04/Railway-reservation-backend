from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import APP_NAME, CORS_ORIGINS
from app.database import create_db_and_tables
from app.routers import auth, journeys, bookings

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title=APP_NAME,
    description="A learning project demonstrating authentication, inventory management, booking transactions, and concurrency-safe seat allocation.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(journeys.router)
app.include_router(bookings.router)

@app.get("/", tags=["Health"])
def root():
    return {"message": "Railway Reservation API is running.", "docs": "/docs"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
