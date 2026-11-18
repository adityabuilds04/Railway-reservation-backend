from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.database import create_db_and_tables, engine
from app.models import Journey

def main():
    create_db_and_tables()
    examples = [
        ("12001", "Demo Express", "New Delhi", "Jaipur", 2, 5),
        ("12002", "City Intercity", "New Delhi", "Agra", 1, 4),
        ("12003", "Northern Link", "Jaipur", "New Delhi", 3, 6),
    ]
    with Session(engine) as session:
        for number, name, source, destination, days, hours in examples:
            existing = session.exec(select(Journey).where(Journey.train_number == number)).first()
            if existing:
                continue
            departure = datetime.now().replace(second=0, microsecond=0) + timedelta(days=days)
            arrival = departure + timedelta(hours=hours)
            session.add(Journey(
                train_number=number,
                train_name=name,
                source=source,
                destination=destination,
                departure_at=departure,
                arrival_at=arrival,
                total_seats=100,
                available_seats=100,
            ))
        session.commit()
    print("Demo journeys added (existing train numbers were skipped).")

if __name__ == "__main__":
    main()
