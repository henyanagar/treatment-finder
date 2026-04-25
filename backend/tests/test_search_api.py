from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.database import get_session
from app.main import app
from app.models import Clinic, ClinicServiceLink, Service


def _build_client() -> tuple[TestClient, Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    session = Session(engine)

    def _override_get_session():
        yield session

    app.dependency_overrides[get_session] = _override_get_session
    return TestClient(app), session


def test_search_returns_matching_clinics() -> None:
    client, session = _build_client()

    service = Service(name="Physiotherapy", description="Treatment")
    clinic = Clinic(name="City Clinic", address="1 Main St", city="Tel Aviv", rating=4.7)
    session.add(service)
    session.add(clinic)
    session.commit()
    session.refresh(service)
    session.refresh(clinic)

    clinic_service = ClinicServiceLink(
        service_id=service.id,
        clinic_id=clinic.id,
        price=250.0,
        is_available=True,
    )
    session.add(clinic_service)
    session.commit()

    response = client.get("/search?query=physio")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["clinic_name"] == "City Clinic"
    assert data[0]["matched_service_name"] == "Physiotherapy"

    app.dependency_overrides.clear()
    session.close()


def test_search_returns_empty_for_blank_or_missing_matches() -> None:
    client, session = _build_client()

    blank_response = client.get("/search?query=   ")
    assert blank_response.status_code == 200
    assert blank_response.json() == []

    no_match_response = client.get("/search?query=cardio")
    assert no_match_response.status_code == 200
    assert no_match_response.json() == []

    app.dependency_overrides.clear()
    session.close()


def test_search_is_case_insensitive_and_matches_clinic_fields() -> None:
    client, session = _build_client()

    service = Service(name="Laser Facial", description="Skin rejuvenation")
    clinic = Clinic(name="City Clinic", address="15 Herzl Street", city="Tel Aviv", rating=4.8)
    session.add(service)
    session.add(clinic)
    session.commit()
    session.refresh(service)
    session.refresh(clinic)

    clinic_service = ClinicServiceLink(
        service_id=service.id,
        clinic_id=clinic.id,
        price=300.0,
        is_available=True,
    )
    session.add(clinic_service)
    session.commit()

    name_response = client.get("/search?query=  city clinic  ")
    assert name_response.status_code == 200
    assert len(name_response.json()) == 1
    assert name_response.json()[0]["clinic_name"] == "City Clinic"

    upper_response = client.get("/search?query=CITY")
    assert upper_response.status_code == 200
    assert len(upper_response.json()) == 1

    address_response = client.get("/search?query=herzl")
    assert address_response.status_code == 200
    assert len(address_response.json()) == 1

    description_response = client.get("/search?query=rejuvenation")
    assert description_response.status_code == 200
    assert len(description_response.json()) == 1

    app.dependency_overrides.clear()
    session.close()
