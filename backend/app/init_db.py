from app.db import create_db_and_tables
from sqlmodel import Session, select

from app.db import engine
from app.models import Clinic, Service


def init() -> None:
    create_db_and_tables()
    with Session(engine) as session:
        has_service = session.exec(select(Service.id).limit(1)).first()
        if not has_service:
            session.add_all(
                [
                    Service(name="Physiotherapy", description="Muscle and joint treatment"),
                    Service(name="Dermatology", description="Skin consultation"),
                    Service(name="Dental Cleaning", description="Routine dental cleaning"),
                ]
            )

        has_clinic = session.exec(select(Clinic.id).limit(1)).first()
        if not has_clinic:
            session.add_all(
                [
                    Clinic(
                        name="City Clinic",
                        address="1 Main St",
                        city="Tel Aviv",
                        rating=4.7,
                    ),
                    Clinic(
                        name="North Care Center",
                        address="10 Oak Rd",
                        city="Haifa",
                        rating=4.5,
                    ),
                ]
            )

        session.commit()


if __name__ == "__main__":
    init()
