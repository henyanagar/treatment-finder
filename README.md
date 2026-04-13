# Treatment Finder and Appointment Platform

Course project for discovering treatments and booking appointments.

## Overview

This platform helps users:
- search for a treatment
- view matching clinics
- compare clinic rating and location
- book appointments

The project is built in stages across the course:
- **Ex1:** Backend only (implemented foundation)
- **Ex2:** Backend + Frontend (planned/next stage)
- **Ex3:** Backend + Frontend + additional microservice (planned/final stage)

## Main User Flow

1. User searches for a treatment.
2. System shows relevant clinics that provide this service.
3. User compares clinics by rating and location.
4. User books an appointment at the selected clinic.

## Architecture Overview

### Backend (Ex1 foundation)
- Technology: FastAPI + SQLModel + SQLite
- Pattern: layered architecture
  - `api` (routes/controllers)
  - `services` (business logic)
  - `repositories` (data access)
  - `schemas` (request/response contracts)
- **Dynamic context injection (AI):** The AI consultation service loads the current service catalog from the database on each request and passes it to the model, so recommendations stay aligned with live data without maintaining separate keyword maps or manual re-mapping when the catalog changes.
- **Resilience:** AI consultation returns a structured response (with an explanatory `reason`) when the database or model pipeline fails unexpectedly, instead of surfacing a generic **500**. Appointment mutations that hit database errors surface **503** with a clear message.

### Frontend (Ex2 target)
- Planned role:
  - treatment search UI
  - clinic comparison UI (rating + location)
  - appointment booking form
- Will consume backend REST APIs.

### Additional Microservice (Ex3 target)
- Planned role:
  - extract one domain capability (for example: notifications, recommendations, or clinic catalog sync)
- Will communicate with backend via HTTP/events and run as an independent process/container.

## Exercises Scope

### Ex1 - Backend Only (Current)
- FastAPI REST API
- SQLite + SQLModel persistence
- Full CRUD for `appointments`
- Supporting resources: `services`, `clinics`
- **Input validation:** Pydantic/SQLModel `Field` constraints on request/response schemas reject bad payloads early (for example non-empty names, phone format, positive IDs, bounded strings). Invalid input returns **HTTP 422** with validation detail instead of opaque server errors.
- Automated tests (`pytest`)
- Manual HTTP demo file

### Ex2 - Backend + Frontend (Planned)
- Add frontend app
- Connect frontend flows to backend APIs
- Demonstrate full user journey in UI

### Ex3 - Backend + Frontend + Microservice (Planned)
- Add one extra microservice
- Run all services via Docker Compose
- Show service boundaries and communication

## Main Entities / Resources

- **services**: treatment/service catalog entries.
- **clinics**: clinics offering services, with location and rating fields.
- **clinic_services**: clinic-to-service mapping table (which clinic offers which treatment).
- **appointments**: booking records linking user + service + clinic + datetime.

## Project Structure

Repository **root** holds container/dependency config and environment templates; all **application code** lives under **`backend/app/`**.

```text
treatment-finder-platform/          # repository root
  Dockerfile                        # image build (copies backend + root requirements)
  docker-compose.yml
  requirements.txt                  # Python dependencies (used by Docker and local install)
  .env.example                      # copy to .env here for local + Compose
  README.md
  .gitignore
  backend/
    app/                            # FastAPI application package
      api/                          # route modules
      services/                     # business logic (incl. ai_service)
      repositories/
      schemas/                      # SQLModel request/response models + Field validation
      core/                         # database engine / session
      init_db.py
      main.py
      models.py
    tests/
    requests/
      appointment_crud.http
    entrypoint.sh                   # Docker container start (init_db + uvicorn)
    treatment_finder.db             # SQLite file (created locally after init_db)
```

## Setup and Run

### Prerequisites
- Python 3.12+ (project currently tested on Python 3.13)
- Docker Desktop (optional, recommended for full run)

**Environment file:** Create `.env` in the **repository root** (next to `docker-compose.yml`). Copy from `.env.example` and add API keys as needed for AI. `app.main` loads `<root>/.env` first, then falls back to `backend/.env`, then python-dotenv’s default search—so it stays aligned with Docker Compose while still allowing a backend-only `.env` if you prefer.

### A) Run Backend Locally (Ex1)

All **runtime commands** (`python -m app.init_db`, `uvicorn`, `pytest`) assume your **current working directory is `backend/`**, so Python can import the `app` package.

From repository root:

```bash
cd backend
python -m venv .venv
```

Windows PowerShell (still inside `backend/`):

```bash
.venv\Scripts\Activate.ps1
```

Install dependencies using the **root** `requirements.txt`:

```bash
pip install -r ../requirements.txt
```

Initialize DB with seed data:

```bash
python -m app.init_db
```

Run backend:

```bash
uvicorn app.main:app --reload
```

Backend URLs:
- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

### B) Run Tests (Backend)

From **`backend/`** (with the venv activated):

```bash
pytest -q
```

### C) Run Entire System with Docker Compose (root)

From **repository root**:

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```

## Frontend and Microservice Commands (Ex2/Ex3)

These folders are planned for next stages. When added, run commands from root:

```bash
cd frontend
# install + run commands (to be added in Ex2)
```

```bash
cd services/<service-name>
# install + run commands (to be added in Ex3)
```

## Ex1 Main API Endpoints

- `GET /health`
- `GET /services`, `POST /services`
- `GET /services/{service_id}`, `GET /services/{service_id}/clinics`
- `GET /clinics`, `POST /clinics`
- `GET /clinics/{clinic_id}`
- `POST /clinics/{clinic_id}/services/{service_id}`, `GET /clinics/{clinic_id}/services`
- `POST /appointments`, `GET /appointments`, `GET /appointments/{appointment_id}`, `PATCH /appointments/{appointment_id}`, `DELETE /appointments/{appointment_id}`
- `GET /search?query=...`
- `POST /ai/consult` (body: `{ "query": "..." }`, see Smart AI Semantic Consultant below)

Full request/response shapes and validation rules are in `backend/app/schemas/` and in OpenAPI at `/docs`.

## Smart AI Semantic Consultant

**`POST /ai/consult`** implements a semantic consultant with **dual-engine support**: **[Groq](https://groq.com/)** runs **Llama 3.1** as the **primary** model, and **Google Gemini** is used as **automatic failover** if Groq fails or is not configured. The handler (`backend/app/services/ai_service.py`) tries Groq first, then Gemini, then a **local keyword fallback** so the API does not hard-crash when providers are down.

The service maps free-text goals and symptoms to rows in your **live** `services` table and returns clinics that offer those treatments. For **broad** queries (for example **“facial treatment”**), the model is instructed to return several distinct catalog names; the API surfaces them as **`matched_service_names`** / **`matched_service_ids`** and aggregates clinics linked to **any** of those services. When only one service is appropriate, **`matched_service_id`** and **`matched_service_name`** are set to that primary match and the plural lists still contain the full set.

### Dual-engine support (details)

- **Primary:** Groq + **Llama 3.1** (default `GROQ_MODEL=llama-3.1-8b-instant`).
- **Failover:** Same structured JSON prompt is sent to **Gemini** if Groq does not succeed.
- **Fallback:** Keyword-style matching over catalog text if neither cloud provider returns usable JSON aligned to catalog names.

### Semantic intelligence

The model interprets **Hebrew**, **slang**, and **medical intent** using general language understanding—**not** hardcoded synonym tables. For example, **back pain** can map to **Physiotherapy** when that service exists in the catalog, using the injected list of names and descriptions only.

### Broad query support

Open-ended requests receive a **short curated set** of distinct services (typically on the order of **three to four** matches), not the entire catalog. Results are reflected in **`matched_service_names`** (and parallel IDs), matching the response model in `backend/app/schemas/ai.py`.

### API keys and environment

Copy `.env.example` to `.env` at the **repository root** and set:

```bash
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.1-8b-instant
GEMINI_API_KEY=your_gemini_key
```

- Groq: [Groq Console](https://console.groq.com/) API keys.
- Gemini: [Google AI Studio](https://aistudio.google.com/app/apikey).

### Docker environment

`docker-compose.yml` loads the root `.env` via `env_file` and **explicitly** passes `GROQ_API_KEY`, `GEMINI_API_KEY`, and `GROQ_MODEL` into the backend container. The image uses `backend/entrypoint.sh`, which starts Uvicorn with those variables already in the process environment.

### Sample request (`POST /ai/consult`)

Request body uses **`AIConsultRequest`**: `query` is required, non-empty, max **4000** characters.

```json
{
  "query": "I want a facial refresh — something for skin texture and glow"
}
```

Example **`AIConsultResponse`** shape (illustrative IDs and copy; your DB IDs and clinic rows will differ). Field names match the implementation:

- **`reason`:** Typically `"Matched via Groq."`, `"Matched via Gemini."`, or a fallback / location-adjustment message from `recommend_treatment`.
- **`confidence_score`:** Roughly **0.86** (Groq) or **0.82** (Gemini) on success, lower when fallback or catalog mismatch logic runs; always between **0** and **1**.

```json
{
  "matched_service_id": null,
  "matched_service_name": null,
  "matched_service_ids": [3, 7, 12],
  "matched_service_names": [
    "Hyaluronic Acid Filler",
    "CO2 Laser Resurfacing",
    "Botox Injection"
  ],
  "location": null,
  "reason": "Matched via Groq.",
  "explanation": "These address facial rejuvenation: fillers for volume, laser for texture, neuromodulator for dynamic lines.",
  "confidence_score": 0.86,
  "clinics": [
    {
      "clinic_id": 4,
      "clinic_name": "Nova Medical Aesthetic Center",
      "city": "Tel Aviv",
      "rating": 4.8
    }
  ]
}
```

## Seed Data Catalog (Demo)

After running `python -m app.init_db`, the DB includes a richer demo dataset:

- Categories represented in service descriptions:
  - `Injections`
  - `Surgical`
  - `Advanced Technology`
- Example advanced services:
  - `Botox Injection`
  - `Hyaluronic Acid Filler`
  - `Rhinoplasty`
  - `CO2 Laser Resurfacing`
  - `CoolSculpting`
- Example specialized clinics:
  - `Nova Medical Aesthetic Center`
  - `Elite Laser & Aesthetics Institute`

This data is linked through `clinic_services` so both local search and AI consult can return meaningful treatment-to-clinic matches in demos.

## Manual Demo Flow (for Grading)

Use `backend/requests/appointment_crud.http`.

Recommended live demo order:
1. `GET /health`
2. `GET /services`
3. `GET /clinics`
4. `POST /appointments`
5. `GET /appointments`
6. `GET /appointments/{id}`
7. `PATCH /appointments/{id}`
8. `DELETE /appointments/{id}`
9. `GET /appointments/{id}` (expect `404`)

## Notes

- **Git hygiene:** `.gitignore` excludes `.venv/`, `__pycache__/`, `*.db`, and `.env`. If any of those were committed by mistake, stop tracking without deleting local files, then commit, for example: `git rm -r --cached backend/.venv` and `git rm --cached backend/treatment_finder.db` (adjust paths to match what was tracked).
- **Secrets:** Keep real API keys only in root `.env` (ignored by git). Docker Compose passes them into the container at runtime; they are not copied into the image layers.
- SQLite is used for Ex1 (`backend/treatment_finder.db`) for simple local persistence.
- `python -m app.init_db` (from **`backend/`**) seeds realistic `services`, `clinics`, and `clinic_services` data for local search proof of concept.
- To reseed from scratch, delete `backend/treatment_finder.db` and run `python -m app.init_db` again from **`backend/`**.
- Automated tests are in `backend/tests/`.
- Manual REST checks are in `backend/requests/appointment_crud.http`.
- Ex1 is the implemented foundation; Ex2/Ex3 sections describe planned extensions and expected structure.
