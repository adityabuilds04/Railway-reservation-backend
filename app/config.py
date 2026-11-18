import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

APP_NAME = os.getenv("APP_NAME", "Railway Reservation API")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(PROJECT_ROOT / 'railway.db').as_posix()}")
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_DEVELOPMENT_SECRET_KEY_BEFORE_DEPLOYMENT")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:5500").split(",") if origin.strip()]

if len(SECRET_KEY) < 32 and SECRET_KEY != "CHANGE_THIS_DEVELOPMENT_SECRET_KEY_BEFORE_DEPLOYMENT":
    raise RuntimeError("SECRET_KEY must be at least 32 characters long.")
