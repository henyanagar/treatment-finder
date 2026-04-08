# Treatment Finder Backend (Ex1)

Backend API for a treatment discovery and appointment booking platform.

## Stack

- FastAPI
- SQLModel + SQLite
- Pytest

## Project Layout

```text
backend/
  app/
    api/
      appointments.py
      services.py
      clinics.py
    repositories/
      appointment_repository.py
      service_repository.py
      clinic_repository.py
    services/
      appointment_service.py
    schemas/
      appointment.py
      service.py
      clinic.py
    core/
      database.py
    db.py
    init_db.py
    main.py
    models.py
  tests/
    test_appointments_api.py
    test_supporting_resources_api.py
  requests/
    appointment_crud.http
  Dockerfile
  docker-compose.yml
  entrypoint.sh
  README.md
  requirements.txt
```

## File Responsibilities

- `app/api/appointments.py` - HTTP endpoints for appointments CRUD.
- `app/api/services.py` - read endpoints for services.
- `app/api/clinics.py` - read endpoints for clinics.
- `app/services/appointment_service.py` - appointment business rules (validation + orchestration).
- `app/repositories/appointment_repository.py` - appointment DB CRUD operations.
- `app/repositories/service_repository.py` - service DB read operations.
- `app/repositories/clinic_repository.py` - clinic DB read operations.
- `app/schemas/appointment.py` - appointment API request/response shapes.
- `app/schemas/service.py` - service response shape.
- `app/schemas/clinic.py` - clinic response shape.
- `app/core/database.py` - shared engine/session module for future service extraction.

## Setup

```bash
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

## Run API

```bash
uvicorn app.main:app --reload
```

API will be available at `http://127.0.0.1:8000` and docs at `http://127.0.0.1:8000/docs`.

## Initialize Seed Data

Run once to create tables and insert sample `services` and `clinics`:

```bash
python -m app.init_db
```

## Run Tests

```bash
pytest -q
```

## Docker

Build and run from the repository root (project-wide compose):

```bash
docker compose up --build
```

The container startup process:
- installs dependencies from `requirements.txt`
- runs `python -m app.init_db`
- starts `uvicorn app.main:app --host 0.0.0.0 --port 8000`

SQLite persistence is configured with a named Docker volume:
- volume: `treatment_finder_db`
- mounted file: `/app/treatment_finder.db`

To stop:

```bash
docker compose down
```

`docker-compose.yml` is located at the project root (`treatment-finder-platform/docker-compose.yml`).

## Main Endpoints

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

## Minimal Test Plan

- Health check returns `200` with `{ "status": "ok" }`.
- Services endpoints: list returns data, get by id works, missing id returns `404`.
- Clinics endpoints: list returns data, get by id works, missing id returns `404`.
- Appointments CRUD: create, list, get, patch, delete, then get returns `404`.
- Appointment create with non-existing `service_id` or `clinic_id` returns `400`.

## Manual HTTP Requests

Use `requests/appointment_crud.http` in Cursor REST client.
The file contains a full demo flow:
1. health check
2. list/get services and clinics
3. create appointment
4. list/get/update/delete appointment
5. verify missing appointment returns `404`

## Notes

- Ex1 currently includes full CRUD for `appointments`.
- `services` and `clinics` are supporting resources in the data model and used for appointment validation.
- Use `GET /services` and `GET /clinics` to fetch valid IDs before creating appointments.

## Microservices Readiness

Current codebase is still a single service, but it now has clearer boundaries for future extraction:
- shared DB/session code moved to `app/core/database.py`
- `app/db.py` remains as a compatibility layer
- appointments logic is already isolated across:
  - `app/api/appointments.py`
  - `app/services/appointment_service.py`
  - `app/repositories/appointment_repository.py`

Recommended next extraction path (no breaking redesign):
1. move appointments module to a separate repo/service with its own DB
2. keep `services` and `clinics` in a catalog service
3. replace direct FK validation with service-to-service calls (or async events)
4. keep API contracts stable (`schemas`) to reduce migration risk
