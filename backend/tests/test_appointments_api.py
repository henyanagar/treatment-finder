from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.database import get_session
from app.main import app
from app.models import Appointment, Clinic, Service, User


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


def _seed_user(session: Session, user_id: int = 1) -> int:
    user = User(
        id=user_id,
        full_name=f"User {user_id}",
        email=f"user{user_id}@example.com",
        phone="0521234567",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user.id


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
    client: TestClient,
    service_id: int,
    clinic_id: int,
    user_name: str = "Dana Levi",
    hour_offset: int = 0,
) -> dict:
    rounded_future = (datetime.now(UTC) + timedelta(days=1)).replace(
        minute=0, second=0, microsecond=0
    )
    rounded_future = rounded_future + timedelta(hours=hour_offset)
    payload = {
        "user_id": 1,
        "notes": "Prefers morning",
        "appointment_datetime": rounded_future.isoformat(),
        "service_id": service_id,
        "clinic_id": clinic_id,
    }
    response = client.post("/appointments", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_appointment_with_empty_user_name_returns_422() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    _seed_user(session, user_id=1)
    payload = {
        "user_id": 1,
        "notes": "Any",
        "appointment_datetime": (
            datetime.now(UTC) + timedelta(days=1)
        ).replace(minute=0, second=0, microsecond=0).isoformat(),
        "service_id": service_id,
        "clinic_id": clinic_id,
    }
    response = client.post("/appointments", json=payload)
    assert response.status_code == 201

    app.dependency_overrides.clear()
    session.close()


def test_create_appointment() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    _seed_user(session, user_id=1)
    created = _create_appointment(client, service_id, clinic_id)
    assert created["id"] > 0
    assert created["user_full_name"] == "User 1"
    assert created["service_name"] == "Physiotherapy"
    assert created["clinic_name"] == "City Clinic"

    app.dependency_overrides.clear()
    session.close()


def test_list_appointments() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    _seed_user(session, user_id=1)
    _create_appointment(client, service_id, clinic_id, user_name="User One")
    _create_appointment(client, service_id, clinic_id, user_name="User Two", hour_offset=1)

    response = client.get("/appointments")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert all(item["service_name"] == "Physiotherapy" for item in body)
    assert all(item["clinic_name"] == "City Clinic" for item in body)

    app.dependency_overrides.clear()
    session.close()


def test_get_appointment_by_id() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    _seed_user(session, user_id=1)
    created = _create_appointment(client, service_id, clinic_id)

    response = client.get(f"/appointments/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]

    app.dependency_overrides.clear()
    session.close()


def test_update_appointment() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    _seed_user(session, user_id=1)
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
    _seed_user(session, user_id=1)
    created = _create_appointment(client, service_id, clinic_id)

    delete_response = client.delete(f"/appointments/{created['id']}")
    assert delete_response.status_code == 204
    updated = session.get(Appointment, created["id"])
    assert updated is not None
    assert updated.status == "CANCELLED"

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
    _seed_user(session, user_id=1)
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
    _seed_user(session, user_id=1)
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


def test_appointments_occupancy_for_empty_range() -> None:
    client, session = _build_client()
    _, clinic_id = _seed_dependencies(session)
    range_start = datetime.now(UTC) + timedelta(days=5)
    range_end = range_start + timedelta(days=1)
    response = client.get(
        "/appointments/occupancy",
        params={
            "clinic_id": clinic_id,
            "range_start": range_start.isoformat(),
            "range_end": range_end.isoformat(),
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["occupied_datetimes"] == []

    app.dependency_overrides.clear()
    session.close()


def test_create_duplicate_slot_returns_409() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    _seed_user(session, user_id=1)
    at = (datetime.now(UTC) + timedelta(days=3)).replace(microsecond=0)
    at = at.replace(minute=0, second=0)
    payload = {
        "user_id": 1,
        "notes": None,
        "appointment_datetime": at.isoformat(),
        "service_id": service_id,
        "clinic_id": clinic_id,
    }
    first = client.post("/appointments", json=payload)
    duplicate = client.post("/appointments", json=payload)
    assert first.status_code == 201
    assert duplicate.status_code == 409

    app.dependency_overrides.clear()
    session.close()


def test_create_appointment_with_missing_supporting_entities_returns_400() -> None:
    client, session = _build_client()
    _seed_user(session, user_id=1)
    payload = {
        "user_id": 1,
        "notes": "Any",
        "appointment_datetime": (
            datetime.now(UTC) + timedelta(days=1)
        ).replace(minute=0, second=0, microsecond=0).isoformat(),
        "service_id": 9999,
        "clinic_id": 9999,
    }
    response = client.post("/appointments", json=payload)
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]

    app.dependency_overrides.clear()
    session.close()


def test_create_appointment_with_non_round_time_returns_400() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    _seed_user(session, user_id=1)
    payload = {
        "user_id": 1,
        "notes": "Any",
        "appointment_datetime": (
            datetime.now(UTC) + timedelta(days=1)
        ).replace(minute=20, second=0, microsecond=0).isoformat(),
        "service_id": service_id,
        "clinic_id": clinic_id,
    }
    response = client.post("/appointments", json=payload)
    assert response.status_code == 400
    assert "on the hour" in response.json()["detail"].lower()

    app.dependency_overrides.clear()
    session.close()


def test_create_review_for_completed_appointment() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    _seed_user(session, user_id=1)
    created = _create_appointment(client, service_id, clinic_id)

    appointment = session.get(Appointment, created["id"])
    assert appointment is not None
    appointment.appointment_datetime = (datetime.now(UTC) - timedelta(days=1)).replace(tzinfo=None)
    session.add(appointment)
    session.commit()

    response = client.post(
        f"/appointments/{created['id']}/reviews",
        json={
            "appointment_id": created["id"],
            "clinic_id": clinic_id,
            "rating": 5,
            "title": "Great visit",
            "review": "Very professional and smooth process.",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["appointment_id"] == created["id"]
    assert body["clinic_id"] == clinic_id
    assert body["rating"] == 5

    updated = session.get(Appointment, created["id"])
    assert updated is not None
    assert updated.rating_id is not None
    clinic = session.get(Clinic, clinic_id)
    assert clinic is not None
    assert clinic.reviews_count == 1
    assert clinic.rating == 5.0

    app.dependency_overrides.clear()
    session.close()


def test_create_review_preserves_legacy_clinic_average_with_rounding() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    _seed_user(session, user_id=1)

    clinic = session.get(Clinic, clinic_id)
    assert clinic is not None
    clinic.rating = 4.7
    clinic.reviews_count = 10
    session.add(clinic)
    session.commit()

    created = _create_appointment(client, service_id, clinic_id)
    appointment = session.get(Appointment, created["id"])
    assert appointment is not None
    appointment.appointment_datetime = (datetime.now(UTC) - timedelta(days=1)).replace(tzinfo=None)
    session.add(appointment)
    session.commit()

    response = client.post(
        f"/appointments/{created['id']}/reviews",
        json={
            "appointment_id": created["id"],
            "clinic_id": clinic_id,
            "rating": 5,
            "title": "Great visit",
            "review": "Very professional and smooth process.",
        },
    )
    assert response.status_code == 201

    updated_clinic = session.get(Clinic, clinic_id)
    assert updated_clinic is not None
    assert updated_clinic.reviews_count == 11
    assert updated_clinic.rating == 4.7

    app.dependency_overrides.clear()
    session.close()


def test_create_review_for_same_appointment_twice_returns_400() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    _seed_user(session, user_id=1)
    created = _create_appointment(client, service_id, clinic_id)

    appointment = session.get(Appointment, created["id"])
    assert appointment is not None
    appointment.appointment_datetime = (datetime.now(UTC) - timedelta(days=1)).replace(tzinfo=None)
    session.add(appointment)
    session.commit()

    first_response = client.post(
        f"/appointments/{created['id']}/reviews",
        json={
            "appointment_id": created["id"],
            "clinic_id": clinic_id,
            "rating": 5,
            "title": "Great visit",
            "review": "Very professional and smooth process.",
        },
    )
    second_response = client.post(
        f"/appointments/{created['id']}/reviews",
        json={
            "appointment_id": created["id"],
            "clinic_id": clinic_id,
            "rating": 4,
            "title": "Second attempt",
            "review": "Should be blocked.",
        },
    )
    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Appointment already rated"

    app.dependency_overrides.clear()
    session.close()


def test_create_review_for_upcoming_appointment_returns_400() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    _seed_user(session, user_id=1)
    created = _create_appointment(client, service_id, clinic_id)

    response = client.post(
        f"/appointments/{created['id']}/reviews",
        json={
            "appointment_id": created["id"],
            "clinic_id": clinic_id,
            "rating": 4,
            "title": "",
            "review": "Too early to rate.",
        },
    )
    assert response.status_code == 400
    assert "completed" in response.json()["detail"].lower()

    app.dependency_overrides.clear()
    session.close()


def test_create_review_with_clinic_mismatch_returns_400() -> None:
    client, session = _build_client()
    service_id, clinic_id = _seed_dependencies(session)
    _seed_user(session, user_id=1)
    _, other_clinic_id = _seed_second_dependencies(session)
    created = _create_appointment(client, service_id, clinic_id)

    appointment = session.get(Appointment, created["id"])
    assert appointment is not None
    appointment.appointment_datetime = (datetime.now(UTC) - timedelta(days=1)).replace(tzinfo=None)
    session.add(appointment)
    session.commit()

    response = client.post(
        f"/appointments/{created['id']}/reviews",
        json={
            "appointment_id": created["id"],
            "clinic_id": other_clinic_id,
            "rating": 4,
            "title": "Mismatch",
            "review": "Should fail.",
        },
    )
    assert response.status_code == 400
    assert "clinic_id" in response.json()["detail"]

    app.dependency_overrides.clear()
    session.close()
