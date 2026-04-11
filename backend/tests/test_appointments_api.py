from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.database import get_session
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


def _seed_dependencies(session: Session) -> tuple[int, int]:
    service = Service(name="Physiotherapy", description="Back pain treatment")
    clinic = Clinic(
        name="City Clinic",
        address="1 Main St",
        city="Tel Aviv",
        rating=4.7,
    )
    session.add(service)
    session.add(clinic)
    session.commit()
    session.refresh(service)
    session.refresh(clinic)
    return service.id, clinic.id


def _seed_second_dependencies(session: Session) -> tuple[int, int]:
    service = Service(name="Dermatology", description="Skin treatment")
    clinic = Clinic(
        name="North Care",
        address="10 Oak Rd",
        city="Haifa",
        rating=4.5,
    )
    session.add(service)
    session.add(clinic)
    session.commit()
    session.refresh(service)
    session.refresh(clinic)
    return service.id, clinic.id


def _create_appointment(
    client: TestClient, service_id: int, clinic_id: int, user_name: str = "Dana Levi"
) -> dict:
    payload = {
        "user_full_name": user_name,
        "user_phone": "0521234567",
        "notes": "Prefers morning",
        "appointment_datetime": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "service_id": service_id,
        "clinic_id": clinic_id,
    }
    response = client.post("/appointments", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_appointment() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    created = _create_appointment(client, service_id, clinic_id)
    assert created["id"] > 0
    assert created["user_full_name"] == "Dana Levi"

    app.dependency_overrides.clear()
    session.close()


def test_list_appointments() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    _create_appointment(client, service_id, clinic_id, user_name="User One")
    _create_appointment(client, service_id, clinic_id, user_name="User Two")

    response = client.get("/appointments")
    assert response.status_code == 200
    assert len(response.json()) == 2

    app.dependency_overrides.clear()
    session.close()


def test_get_appointment_by_id() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    created = _create_appointment(client, service_id, clinic_id)

    response = client.get(f"/appointments/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]

    app.dependency_overrides.clear()
    session.close()


def test_update_appointment() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    created = _create_appointment(client, service_id, clinic_id)

    response = client.patch(
        f"/appointments/{created['id']}",
        json={"notes": "Updated note"},
    )
    assert response.status_code == 200
    assert response.json()["notes"] == "Updated note"

    app.dependency_overrides.clear()
    session.close()


def test_delete_appointment() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    created = _create_appointment(client, service_id, clinic_id)

    delete_response = client.delete(f"/appointments/{created['id']}")
    assert delete_response.status_code == 204

    app.dependency_overrides.clear()
    session.close()


def test_missing_appointment_returns_404() -> None:
    client, session = _build_client()
    response = client.get("/appointments/9999")
    assert response.status_code == 404

    app.dependency_overrides.clear()
    session.close()


def test_update_appointment_partial_service_id_only() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    new_service_id, _ = _seed_second_dependencies(session)
    created = _create_appointment(client, service_id, clinic_id)

    response = client.patch(
        f"/appointments/{created['id']}",
        json={"service_id": new_service_id},
    )
    assert response.status_code == 200
    assert response.json()["service_id"] == new_service_id
    assert response.json()["clinic_id"] == clinic_id

    app.dependency_overrides.clear()
    session.close()


def test_update_appointment_partial_clinic_id_only() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    _, new_clinic_id = _seed_second_dependencies(session)
    created = _create_appointment(client, service_id, clinic_id)

    response = client.patch(
        f"/appointments/{created['id']}",
        json={"clinic_id": new_clinic_id},
    )
    assert response.status_code == 200
    assert response.json()["service_id"] == service_id
    assert response.json()["clinic_id"] == new_clinic_id

    app.dependency_overrides.clear()
    session.close()


def test_create_appointment_with_missing_supporting_entities_returns_400() -> None:
    client, session = _build_client()
    payload = {
        "user_full_name": "Noa Cohen",
        "user_phone": "0537654321",
        "notes": "Any",
        "appointment_datetime": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "service_id": 9999,
        "clinic_id": 9999,
    }
    response = client.post("/appointments", json=payload)
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]

    app.dependency_overrides.clear()
    session.close()
