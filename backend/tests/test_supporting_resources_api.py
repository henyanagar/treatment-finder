from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db import get_session
from app.main import app
from app.models import Clinic, Service


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


def test_list_and_get_services() -> None:
    client, session = _build_client()
    service = Service(name="Dermatology", description="Skin consultation")
    session.add(service)
    session.commit()
    session.refresh(service)

    list_res = client.get("/services")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    get_res = client.get(f"/services/{service.id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Dermatology"

    not_found_res = client.get("/services/9999")
    assert not_found_res.status_code == 404

    app.dependency_overrides.clear()
    session.close()


def test_list_and_get_clinics() -> None:
    client, session = _build_client()
    clinic = Clinic(name="North Clinic", address="10 Oak Rd", city="Haifa", rating=4.5)
    session.add(clinic)
    session.commit()
    session.refresh(clinic)

    list_res = client.get("/clinics")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    get_res = client.get(f"/clinics/{clinic.id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "North Clinic"

    not_found_res = client.get("/clinics/9999")
    assert not_found_res.status_code == 404

    app.dependency_overrides.clear()
    session.close()


def test_services_pagination() -> None:
    client, session = _build_client()
    session.add_all(
        [
            Service(name="A", description="A"),
            Service(name="B", description="B"),
            Service(name="C", description="C"),
        ]
    )
    session.commit()

    response = client.get("/services?offset=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    app.dependency_overrides.clear()
    session.close()


def test_clinics_pagination() -> None:
    client, session = _build_client()
    session.add_all(
        [
            Clinic(name="C1", address="1 A St", city="Tel Aviv", rating=4.0),
            Clinic(name="C2", address="2 B St", city="Haifa", rating=4.1),
            Clinic(name="C3", address="3 C St", city="Jerusalem", rating=4.2),
        ]
    )
    session.commit()

    response = client.get("/clinics?offset=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    app.dependency_overrides.clear()
    session.close()
