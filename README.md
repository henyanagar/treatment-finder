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
      db.py
      init_db.py
      main.py
      models.py
    tests/
    requests/
      appointment_crud.http
    Dockerfile
    entrypoint.sh
    requirements.txt
    README.md
  docker-compose.yml
  README.md
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
- Automated tests are in `backend/tests/`.
- Manual REST checks are in `backend/requests/appointment_crud.http`.
- Ex1 is the implemented foundation; Ex2/Ex3 sections describe planned extensions and expected structure.
