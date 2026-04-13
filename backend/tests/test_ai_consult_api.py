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


def test_ai_consult_fallback_returns_service_and_clinics(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    client, session = _build_client()

    dermatology = Service(name="Dermatology Consultation", description="Skin and acne consultation")
    clinic = Clinic(name="City Clinic", address="1 Main St", city="Tel Aviv", rating=4.7)
    session.add(dermatology)
    session.add(clinic)
    session.commit()
    session.refresh(dermatology)
    session.refresh(clinic)

    link = ClinicServiceLink(
        clinic_id=clinic.id,
        service_id=dermatology.id,
        is_available=True,
        price=320.0,
    )
    session.add(link)
    session.commit()

    response = client.post(
        "/ai/consult",
        json={"query": "I have very dry skin lately and need calming treatment"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["matched_service_name"] == "Dermatology Consultation"
    assert "keyword" in data["reason"].lower() or "fallback" in data["reason"].lower()
    assert data["explanation"]
    assert 0.0 <= data["confidence_score"] <= 1.0
    assert len(data["clinics"]) == 1
    assert data["clinics"][0]["clinic_name"] == "City Clinic"

    app.dependency_overrides.clear()
    session.close()


def test_ai_consult_out_of_scope_returns_null_match(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    client, session = _build_client()
    session.add(Service(name="Botox Injection", description="Aesthetic injection"))
    session.commit()

    response = client.post("/ai/consult", json={"query": "asdfgh"})
    assert response.status_code == 200
    data = response.json()
    assert data["matched_service_id"] is None
    assert data["matched_service_name"] is None
    assert "gibberish" in data["reason"].lower()
    assert data["explanation"]
    assert data["confidence_score"] == 0.0
    assert data["clinics"] == []

    app.dependency_overrides.clear()
    session.close()


def test_ai_consult_hebrew_treatment_word_is_not_flagged_gibberish(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    client, session = _build_client()
    session.add(Service(name="Botox Injection", description="Injectable for dynamic wrinkles"))
    session.commit()

    response = client.post("/ai/consult", json={"query": "בוטוקס"})
    assert response.status_code == 200
    data = response.json()
    assert "gibberish" not in data["reason"].lower()

    app.dependency_overrides.clear()
    session.close()


def test_ai_consult_pain_prioritizes_rehabilitation(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    client, session = _build_client()
    physio = Service(name="Physiotherapy", description="Musculoskeletal rehabilitation")
    rehab = Service(name="Sports Injury Rehabilitation", description="Injury rehab program")
    session.add(physio)
    session.add(rehab)
    session.commit()

    response = client.post(
        "/ai/consult",
        json={"query": "I have shoulder pain and movement limitation after injury"},
    )
    assert response.status_code == 200
    data = response.json()
    names = data.get("matched_service_names") or []
    primary = data.get("matched_service_name")
    assert primary is not None or len(names) >= 1
    assert any(
        n in ("Physiotherapy", "Sports Injury Rehabilitation")
        for n in ([primary] if primary else []) + names
    )
    assert 0.0 <= data["confidence_score"] <= 1.0

    app.dependency_overrides.clear()
    session.close()


def test_ai_consult_location_filter_and_city_fallback(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    client, session = _build_client()
    service = Service(name="Botox Injection", description="Injectable for dynamic wrinkles")
    clinic_tlv = Clinic(name="Tel Aviv Clinic", address="1 Main St", city="Tel Aviv", rating=4.7)
    clinic_hfa = Clinic(name="Haifa Clinic", address="2 Oak Rd", city="Haifa", rating=4.6)
    session.add(service)
    session.add(clinic_tlv)
    session.add(clinic_hfa)
    session.commit()
    session.refresh(service)
    session.refresh(clinic_tlv)
    session.refresh(clinic_hfa)

    session.add(
        ClinicServiceLink(clinic_id=clinic_tlv.id, service_id=service.id, is_available=True, price=900.0)
    )
    session.add(
        ClinicServiceLink(clinic_id=clinic_hfa.id, service_id=service.id, is_available=True, price=920.0)
    )
    session.commit()

    res_city_match = client.post("/ai/consult", json={"query": "Botox in Haifa"})
    assert res_city_match.status_code == 200
    data_city = res_city_match.json()
    assert data_city["location"] == "Haifa"
    assert len(data_city["clinics"]) == 1
    assert data_city["clinics"][0]["city"] == "Haifa"

    res_city_miss = client.post("/ai/consult", json={"query": "Botox in Jerusalem"})
    assert res_city_miss.status_code == 200
    data_miss = res_city_miss.json()
    assert data_miss["location"] == "Jerusalem"
    assert len(data_miss["clinics"]) == 2
    assert "currently provide clinics in Israel only" in data_miss["reason"]

    app.dependency_overrides.clear()
    session.close()
