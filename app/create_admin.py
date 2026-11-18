import os
from getpass import getpass
from sqlmodel import Session, select
from app.database import create_db_and_tables, engine
from app.models import User
from app.security import hash_password

def main():
    create_db_and_tables()
    email = os.getenv("ADMIN_EMAIL") or input("Admin email: ").strip().lower()
    password = os.getenv("ADMIN_PASSWORD") or getpass("Admin password (minimum 8 characters): ")
    full_name = os.getenv("ADMIN_NAME", "System Administrator")
    if len(password) < 8:
        raise SystemExit("Password must contain at least 8 characters.")
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            print("A user with that email already exists. No changes made.")
            return
        session.add(User(email=email.lower(), full_name=full_name, password_hash=hash_password(password), role="admin"))
        session.commit()
    print("Admin account created. Keep its password private.")

if __name__ == "__main__":
    main()
