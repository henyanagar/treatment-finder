"""
AI consultation: semantic routing from user query to catalog services.
All clinical intent is delegated to Groq/Gemini; only basic keyword fallback if APIs fail.
"""

import json
import os
import re

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Clinic, ClinicServiceLink, Service, TreatmentCategory
from app.schemas.ai import AIConsultClinicRead, AIConsultResponse

GEMINI_MODEL_CANDIDATES = (
    "gemini-2.0-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
)


MINIMAL_VALID_HEBREW_HINTS = {
    "בוטוקס",
    "מילוי",
    "ניתוח",
}


def _looks_like_gibberish(query: str, known_terms: set[str] | None = None) -> bool:
    normalized = query.lower().strip()
    compact = "".join(ch for ch in normalized if ch.isalnum() or "\u0590" <= ch <= "\u05ff")
    if not compact:
        return True
    contains_hebrew = bool(re.search(r"[\u0590-\u05ff]", normalized))
    known = known_terms or set()
    if normalized in known or compact in known or compact in MINIMAL_VALID_HEBREW_HINTS:
        return False
    if contains_hebrew and len(compact) >= 3:
        return False
    if len(compact) <= 2:
        return True
    if len(normalized.split()) > 1:
        return False
    return len(compact) >= 6 and sum(ch in "aeiou" for ch in compact) <= 1


def _parse_json_payload(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def _services_context(services: list[Service], categories_by_id: dict[int, str]) -> str:
    return ", ".join(
        f"{idx}. Category: {categories_by_id.get(service.category_id or -1, 'General')}, "
        f"Service: {service.name}, Description: {service.description or 'No description provided'}"
        for idx, service in enumerate(services, start=1)
    )


def _build_prompt(user_query: str, services_context: str, known_cities: list[str]) -> str:
    cities = ", ".join(sorted(set(known_cities))) if known_cities else "Unknown"
    return f"""
You are an expert medical and aesthetic consultant.
Your only source of truth is the provided list of services (names and descriptions).
Understand the user's intent from any language (including Hebrew and slang); use your medical knowledge
to map symptoms and goals to the correct entries in that list (e.g. volume restoration → filler-type
services, dynamic wrinkles → neuromodulator-type services), always choosing EXACT service names from the list.

If the query is specific, return the single best match as a one-element list.
If the query is broad (e.g. general facial treatment, skin improvement without a single clear target),
return the top 3–4 most relevant distinct services from the list—not the entire catalog.

Known clinic cities (for location extraction): {cities}

User query: {user_query}

Services:
{services_context}

Return ONLY JSON:
{{
  "service_names": ["EXACT_NAME_FROM_LIST", "..."],
  "location": "CITY_IN_ENGLISH_OR_NULL",
  "explanation": "Professional, concise explanation for the patient."
}}
"""


def _call_groq(prompt: str) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    from groq import Groq

    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Return only raw JSON. No markdown."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    raw = (completion.choices[0].message.content or "").strip()
    return _parse_json_payload(raw)


def _generate_content_with_model_failover(genai_client, prompt: str) -> str:
    last_error: Exception | None = None
    for model_name in GEMINI_MODEL_CANDIDATES:
        try:
            response = genai_client.models.generate_content(model=model_name, contents=prompt)
            return (response.text or "").strip()
        except Exception as exc:
            last_error = exc
    if last_error:
        raise last_error
    raise RuntimeError("No Gemini models were available")


def _call_gemini(prompt: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    from google import genai

    client = genai.Client(api_key=api_key)
    raw = _generate_content_with_model_failover(client, prompt)
    return _parse_json_payload(raw)


def _resolve_services_by_exact_name(
    service_names: list[str], catalog: list[Service]
) -> list[Service]:
    by_name = {s.name.lower().strip(): s for s in catalog}
    out: list[Service] = []
    seen: set[int] = set()
    for name in service_names:
        if not isinstance(name, str):
            continue
        svc = by_name.get(name.strip().lower())
        if svc and svc.id is not None and svc.id not in seen:
            seen.add(svc.id)
            out.append(svc)
    return out


def _basic_search_fallback(query: str, catalog: list[Service]) -> list[Service]:
    tokens = [t for t in re.split(r"\s+", query.lower().strip()) if t]
    if not tokens:
        return []
    scored: list[tuple[int, Service]] = []
    for svc in catalog:
        hay = f"{svc.name} {svc.description or ''}".lower()
        score = sum(1 for t in tokens if t in hay)
        if score > 0:
            scored.append((score, svc))
    scored.sort(key=lambda x: x[0], reverse=True)
    picked: list[Service] = []
    seen: set[int] = set()
    for _, svc in scored[:4]:
        if svc.id is not None and svc.id not in seen:
            seen.add(svc.id)
            picked.append(svc)
    return picked


def _normalize_location(
    raw: str | None, query: str, known_cities: list[str]
) -> str | None:
    if raw and str(raw).strip():
        v = str(raw).strip()
        for c in known_cities:
            if c.lower() == v.lower():
                return c
        return v
    q = query.lower()
    for c in known_cities:
        if c.lower() in q:
            return c
    m = re.search(r"\bin\s+([A-Za-z][A-Za-z\s-]{1,40})", query)
    return m.group(1).strip() if m else None


def _empty_ai_response(reason: str, explanation: str, *, location: str | None = None) -> AIConsultResponse:
    return AIConsultResponse(
        matched_service_id=None,
        matched_service_name=None,
        matched_service_ids=[],
        matched_service_names=[],
        location=location,
        reason=reason,
        explanation=explanation,
        confidence_score=0.0,
        clinics=[],
    )


def _consult_with_catalog(
    user_query: str, session: Session, catalog: list[Service]
) -> AIConsultResponse:
    known_cities = list(session.exec(select(Clinic.city).distinct()).all())
    categories = list(session.exec(select(TreatmentCategory)).all())
    cat_by_id = {c.id: c.name for c in categories if c.id is not None}
    ctx = _services_context(catalog, cat_by_id)
    prompt = _build_prompt(user_query, ctx, known_cities)

    payload: dict | None = None
    reason = ""
    explanation = ""
    confidence = 0.0

    try:
        payload = _call_groq(prompt)
        reason = "Matched via Groq."
        confidence = 0.86
    except Exception:
        try:
            payload = _call_gemini(prompt)
            reason = "Matched via Gemini."
            confidence = 0.82
        except Exception:
            payload = None

    if payload:
        names = [
            str(n).strip()
            for n in payload.get("service_names", [])
            if isinstance(n, str) and str(n).strip()
        ]
        selected = _resolve_services_by_exact_name(names, catalog)
        location = _normalize_location(payload.get("location"), user_query, known_cities)
        explanation = str(payload.get("explanation", "")).strip() or "Recommendation based on your query."
        if not selected:
            reason = "AI returned names that did not match the catalog; using basic search."
            selected = _basic_search_fallback(user_query, catalog)
            confidence = 0.5 if selected else 0.0
            explanation = "Could not align AI output to catalog services; fallback keyword match was used."
    else:
        selected = _basic_search_fallback(user_query, catalog)
        location = _normalize_location(None, user_query, known_cities)
        reason = "AI providers unavailable; basic keyword search was used."
        explanation = "External AI was not available. Results are from a simple local text match."
        confidence = 0.55 if selected else 0.0

    if not selected:
        return AIConsultResponse(
            matched_service_id=None,
            matched_service_name=None,
            matched_service_ids=[],
            matched_service_names=[],
            location=location,
            reason=reason or "No matching services found.",
            explanation=explanation or "No suitable service in the catalog for this query.",
            confidence_score=0.0,
            clinics=[],
        )

    ids = [s.id for s in selected if s.id is not None]
    names_out = [s.name for s in selected if s.id is not None]
    multiple = len(ids) > 1

    stmt = (
        select(Clinic)
        .join(ClinicServiceLink, ClinicServiceLink.clinic_id == Clinic.id)
        .where(ClinicServiceLink.service_id.in_(ids))
        .where(ClinicServiceLink.is_available.is_(True))
        .distinct()
    )
    if location:
        stmt = stmt.where(func.lower(Clinic.city) == location.lower())
    clinics = list(session.exec(stmt).all())

    known_lower = {c.lower() for c in known_cities}
    if location and not clinics:
        broad = (
            select(Clinic)
            .join(ClinicServiceLink, ClinicServiceLink.clinic_id == Clinic.id)
            .where(ClinicServiceLink.service_id.in_(ids))
            .where(ClinicServiceLink.is_available.is_(True))
            .distinct()
        )
        clinics = list(session.exec(broad).all())
        if clinics:
            if location.lower() in known_lower:
                reason = f"No clinics in {location}; showing other areas."
            else:
                reason = (
                    f"'{location}' is outside our listed cities; "
                    "we currently provide clinics in Israel only, showing available results from supported areas."
                )

    items = [
        AIConsultClinicRead(
            clinic_id=c.id,
            clinic_name=c.name,
            city=c.city,
            rating=c.rating,
        )
        for c in clinics
    ]

    primary = selected[0]
    return AIConsultResponse(
        matched_service_id=None if multiple else primary.id,
        matched_service_name=None if multiple else primary.name,
        matched_service_ids=ids,
        matched_service_names=names_out,
        location=location,
        reason=reason,
        explanation=explanation,
        confidence_score=max(0.0, min(1.0, confidence)),
        clinics=items,
    )


def recommend_treatment(user_query: str, session: Session) -> AIConsultResponse:
    try:
        catalog = list(session.exec(select(Service)).all())
    except Exception:
        return _empty_ai_response(
            "We could not read the treatment catalog.",
            "A database error occurred. Please try again shortly.",
        )

    if not catalog:
        return _empty_ai_response(
            "No services are configured in the database.",
            "Add or seed services before using AI consultation.",
        )

    known_terms: set[str] = set(MINIMAL_VALID_HEBREW_HINTS)
    for service in catalog:
        name = (service.name or "").lower().strip()
        if not name:
            continue
        known_terms.add(name)
        known_terms.update(t for t in re.split(r"\s+", name) if len(t) >= 3)
    if _looks_like_gibberish(user_query, known_terms):
        return _empty_ai_response(
            "The query looks like gibberish and could not be interpreted.",
            "Please describe your concern in clear words (any language).",
        )

    try:
        return _consult_with_catalog(user_query, session, catalog)
    except Exception:
        return _empty_ai_response(
            "We could not complete this consultation.",
            "A temporary error occurred while matching services or loading clinics. Please try again.",
        )
