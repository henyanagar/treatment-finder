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

```text
treatment-finder-platform/
  backend/
    app/
      api/
      services/
      repositories/
      schemas/
      core/
      init_db.py
      main.py
      models.py
    tests/
    requests/
      appointment_crud.http
    entrypoint.sh
    README.md
  Dockerfile
  docker-compose.yml
  requirements.txt
  README.md
  .env.example
  .gitignore
```

## Setup and Run

### Prerequisites
- Python 3.12+ (project currently tested on Python 3.13)
- Docker Desktop (optional, recommended for full run)

### A) Run Backend Locally (Ex1)

From repository root:

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
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

From repository root:

```bash
cd backend
pytest -q
```

### C) Run Entire System with Docker Compose (root)

From repository root:

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
- `GET /services`
- `GET /services/{service_id}`
- `GET /clinics`
- `GET /clinics/{clinic_id}`
- `POST /appointments`
- `GET /appointments`
- `GET /appointments/{appointment_id}`
- `PATCH /appointments/{appointment_id}`
- `DELETE /appointments/{appointment_id}`
- `GET /search?query=...`
- `POST /ai/consult`

## Smart AI Semantic Consultant

The backend exposes **`POST /ai/consult`**, a semantic consultant that maps free-text goals and symptoms to entries in your **current** treatment catalog and returns matching clinics.

### Dual-engine support

- **Primary:** [Groq](https://groq.com/) runs **Llama 3.1** (default model `llama-3.1-8b-instant`, overridable via `GROQ_MODEL`).
- **Failover:** If Groq errors or is misconfigured, the same prompt is sent to **Google Gemini** automatically.
- If both providers are unavailable, a **local keyword fallback** still returns plausible services (no hard crash).

### Semantic intelligence

The model interprets **Hebrew**, **slang**, and **medical intent** using general language understanding—**not** hardcoded synonym tables. For example, a user describing **back pain** can be routed toward **Physiotherapy** (or whatever matching services exist in your seeded catalog) based on the live list of service names and descriptions.

### Broad query support

Open-ended requests (e.g. **“Facial treatment”**) receive a **short curated set** of distinct, relevant services across categories (typically several top matches), not a single arbitrary pick or the entire catalog.

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

```json
{
  "query": "I want a facial refresh — something for skin texture and glow"
}
```

Example response shape (multi-match; single-match responses still populate `matched_service_id` / `matched_service_name` for the primary item):

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

- SQLite is used for Ex1 (`treatment_finder.db`) for simple local persistence.
- `python -m app.init_db` now seeds realistic `services`, `clinics`, and `clinic_services` data for local search proof of concept.
- To reseed from scratch, delete `backend/treatment_finder.db` and run `python -m app.init_db` again.
- Automated tests are in `backend/tests/`.
- Manual REST checks are in `backend/requests/appointment_crud.http`.
- Ex1 is the implemented foundation; Ex2/Ex3 sections describe planned extensions and expected structure.
