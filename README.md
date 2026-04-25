# Treatment Finder and Appointment Platform

Course project for discovering treatments, comparing clinics, booking appointments, and rating completed visits.

## System Architecture

- **Frontend:** React + Vite + Tailwind CSS
- **Backend:** FastAPI + SQLModel + SQLite
- **Communication:** Frontend consumes backend REST APIs via `/api`.

Backend structure:
- `backend/app/api` - route layer
- `backend/app/services` - business logic
- `backend/app/repositories` - data access
- `backend/app/schemas` - request/response contracts
- `backend/app/core` + `backend/app/database.py` - DB engine/session exports

## Frontend Overview

- Uses React Hooks (`useState`, `useEffect`, `useMemo`, `useCallback`) for state and UI flow.
- Separation of concerns:
  - `frontend/src/pages` = route-level orchestration
  - `frontend/src/components` = reusable UI components
- Main libraries:
  - React
  - Vite
  - Tailwind CSS
  - React Router
  - Fetch API (`frontend/src/services/api.js`)

## Environment Variables

Create a root `.env` file from `.env.example`.

Minimum required:

```bash
DATABASE_URL=sqlite:///./treatment_finder.db
```

Optional AI keys:

```bash
GROQ_API_KEY=
GROQ_MODEL=llama-3.1-8b-instant
GEMINI_API_KEY=
```

Optional frontend local override:

```bash
VITE_API_BASE_URL=/api
```

## Local Run

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r ../requirements.txt
python -m app.init_db
uvicorn app.main:app --reload
```

Backend docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend (local dev): [http://localhost:5173](http://localhost:5173)

## Docker Deployment

Run from repository root:

```bash
docker-compose up --build
```

Access:
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Notes:
- `docker-compose.yml` loads root `.env` (`env_file: .env`).
- Backend receives: `DATABASE_URL`, `GROQ_API_KEY`, `GEMINI_API_KEY`, `GROQ_MODEL`.
- Backend startup command in Docker seeds DB automatically before starting Uvicorn.
- Frontend container runs Vite in dev mode for EX2 demo.

Stop containers:

```bash
docker-compose down
```

## Troubleshooting Docker

- **Database not found / unable to open database file**
  1. Verify root `.env` exists.
  2. Verify `DATABASE_URL` is present and valid:
     ```bash
     DATABASE_URL=sqlite:///./treatment_finder.db
     ```
  3. Rebuild:
     ```bash
     docker-compose up --build
     ```

- **Frontend cannot reach backend**
  - Ensure both services are running in Compose.
  - Frontend proxy target for Docker is `http://backend:8000`.

## Quick Verification Checklist

- `docker-compose up --build` runs without errors
- Backend docs open at `http://localhost:8000/docs`
- Frontend opens at `http://localhost:3000`
- `My Appointments` and `Past Visits` show seeded data
- Rating submission updates clinic aggregate score and reviews count
# Treatment Finder and Appointment Platform

Course project for discovering treatments, comparing clinics, booking appointments, and rating completed visits.

## System Architecture

- **Frontend:** React + Vite + Tailwind CSS
- **Backend:** FastAPI + SQLModel + SQLite
- **Communication:** Frontend calls backend APIs through `/api`.

Backend app layout:
- `backend/app/api` - route layer
- `backend/app/services` - business logic
- `backend/app/repositories` - data access
- `backend/app/schemas` - API contracts
- `backend/app/core` + `backend/app/database.py` - DB engine/session exports

## Local Setup

### Backend (local)

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r ../requirements.txt
python -m app.init_db
uvicorn app.main:app --reload
```

Backend docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Frontend (local)

```bash
cd frontend
npm install
npm run dev
```

Frontend local URL: [http://localhost:5173](http://localhost:5173)

## Environment Variables

Create a root `.env` (copy from `.env.example`).

Minimum required:

```bash
DATABASE_URL=sqlite:///./treatment_finder.db
```

Optional AI keys:

```bash
GROQ_API_KEY=
GROQ_MODEL=llama-3.1-8b-instant
GEMINI_API_KEY=
```

## Docker Deployment

Run from repository root:

```bash
docker-compose up --build
```

Access:
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Docker notes
- `docker-compose.yml` loads root `.env` via:
  - `env_file: .env`
- Backend container gets:
  - `DATABASE_URL`
  - `GROQ_API_KEY`
  - `GEMINI_API_KEY`
  - `GROQ_MODEL`
- Backend startup command in Docker seeds DB automatically before starting server:
  - `python -m app.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Frontend container runs Vite in dev mode for EX2 demo:
  - `npm run dev -- --host 0.0.0.0 --port 3000`

Stop containers:

```bash
docker-compose down
```

## Troubleshooting Docker

- **Database not found / unable to open database file**
  1. Ensure root `.env` exists.
  2. Ensure it contains a valid `DATABASE_URL`, for example:
     ```bash
     DATABASE_URL=sqlite:///./treatment_finder.db
     ```
  3. Rebuild and rerun:
     ```bash
     docker-compose up --build
     ```

- **Frontend cannot reach backend**
  - Ensure both services are up in `docker-compose`.
  - Frontend proxy target is configured for Docker service networking (`http://backend:8000`).
# Treatment Finder and Appointment Platform

Course project for discovering treatments, comparing clinics, booking appointments, and rating completed visits.

## System Architecture

- **Frontend:** React + Vite + Tailwind CSS
- **Backend:** FastAPI + SQLModel + SQLite
- **Flow:** Frontend consumes backend REST APIs (`/api`).

Backend structure:
- `backend/app/api` - routes/controllers
- `backend/app/services` - business logic
- `backend/app/repositories` - DB queries
- `backend/app/schemas` - request/response models
- `backend/app/core` + `backend/app/database.py` - engine/session exports

## Backend Setup (Local)

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
pip install -r ../requirements.txt
```

Create root `.env` from `.env.example` and set at minimum:

```bash
DATABASE_URL=sqlite:///./treatment_finder.db
```

Optional AI keys:

```bash
GROQ_API_KEY=
GROQ_MODEL=llama-3.1-8b-instant
GEMINI_API_KEY=
```

Seed DB and run backend:

```bash
python -m app.init_db
uvicorn app.main:app --reload
```

Backend docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Frontend Setup (Local)

From repository root:

```bash
cd frontend
npm install
npm run dev
```

Frontend local URL (dev): [http://localhost:5173](http://localhost:5173)

## Docker Deployment

Run from repository root:

```bash
docker-compose up --build
```

Access:
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Notes:
- `docker-compose.yml` loads env from root `.env` and (optionally) `backend/.env`.
- Backend container receives `DATABASE_URL`, `GROQ_API_KEY`, `GEMINI_API_KEY`, and `GROQ_MODEL`.
- Backend image entrypoint runs `python -m app.init_db` automatically before starting Uvicorn.

Stop containers:

```bash
docker-compose down
```
# Treatment Finder and Appointment Platform

Course project for discovering treatments, comparing clinics, and managing appointments.

## System Architecture

### High-Level
- **Frontend:** React + Vite + Tailwind CSS
- **Backend:** FastAPI + SQLModel + SQLite
- **Communication:** Frontend calls backend REST APIs (`/api` via Vite proxy in local development)

### Backend Layers
- `api/` - route handlers and HTTP contracts
- `services/` - business rules
- `repositories/` - database query layer
- `schemas/` - request/response validation models
- `core/` - low-level DB engine/session logic
- `database.py` - app-level DB exports (`engine`, `get_session`, `create_db_and_tables`)

### Core Resources
- `services` - treatment catalog
- `clinics` - clinic profile and location/rating data
- `clinic_services` - clinic-to-service offerings
- `appointments` - booking records
- `ratings` - appointment reviews

## Frontend Overview

### State Management Approach
- Uses **React Hooks** extensively:
  - `useState` for local UI state (forms, loading, modals, filters)
  - `useEffect` for lifecycle data fetches and side effects
  - `useMemo` / `useCallback` for derived state and stable handlers

### Component Organization
- `frontend/src/pages/` holds route-level screens and orchestration logic.
- `frontend/src/components/` holds reusable UI building blocks.
- This keeps business flow in pages while reusing components across screens.

### Main Frontend Libraries
- **React**
- **Vite**
- **Tailwind CSS**
- **React Router**
- **Fetch API** via `frontend/src/services/api.js`

> Note: The project does **not** currently use Material-UI or Axios.

## Backend Setup

### Prerequisites
- Python 3.12+ (tested on Python 3.13)

### 1) Create and activate virtual environment
From repository root:

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
From `backend/`:

```bash
pip install -r ../requirements.txt
```

### 3) Configure environment
Create `.env` at repository root (copy from `.env.example`).

Required:

```bash
DATABASE_URL=sqlite:///./treatment_finder.db
```

Optional AI provider keys:

```bash
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.1-8b-instant
GEMINI_API_KEY=your_gemini_key
```

### Database URL behavior (important)
- `DATABASE_URL` is loaded via `backend/app/config.py` (`pydantic-settings`).
- It is **required** (app fails fast if missing).
- For SQLite, relative DB paths are resolved to an absolute path inside `backend/`, so the DB file is created consistently at:
  - `backend/treatment_finder.db`
  - regardless of where the command is launched from.

### 4) Initialize database with seed data
From `backend/`:

```bash
python -m app.init_db
```

### 5) Run backend API
From `backend/`:

```bash
uvicorn app.main:app --reload
```

Backend URLs:
- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

### 6) Run backend tests
From `backend/`:

```bash
pytest -q
```

### Backend troubleshooting
- **`ModuleNotFoundError: No module named 'app'`**
  - Run backend commands from `backend/`.
- **`unable to open database file`**
  - Ensure root `.env` contains:
  ```bash
  DATABASE_URL=sqlite:///./treatment_finder.db
  ```
  - Rerun:
  ```bash
  cd backend
  python -m app.init_db
  ```
- **Stale local DB**
  - Delete `backend/treatment_finder.db`, then reseed:
  ```bash
  cd backend
  python -m app.init_db
  ```

## Frontend Setup

### Prerequisites
- Node.js (LTS recommended)
- npm

### 1) Install dependencies
From repository root:

```bash
cd frontend
npm install
```

### 2) Run frontend dev server
From `frontend/`:

```bash
npm run dev
```

Frontend URL: `http://localhost:5173`

### 3) Lint frontend
From `frontend/`:

```bash
npm run lint
```

## Quick Grader Run

Use two terminals from repository root.

### Terminal A (Backend)
```bash
cd backend
.venv\Scripts\Activate.ps1
python -m app.init_db
uvicorn app.main:app --reload
```

### Terminal B (Frontend)
```bash
cd frontend
npm install
npm run dev
```

Verify:
- Frontend: `http://localhost:5173`
- Backend docs: `http://127.0.0.1:8000/docs`

## Optional Docker

From repository root:

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```
# Treatment Finder and Appointment Platform

Course project for discovering treatments, comparing clinics, and booking appointments.

## System Architecture

### High-Level Design
- **Frontend:** React + Vite + Tailwind CSS
- **Backend:** FastAPI + SQLModel + SQLite
- **Communication:** Frontend calls backend REST APIs (`/api` via Vite proxy in local development)

### Backend Layering
- `api/` - route handlers and HTTP contracts
- `services/` - business rules
- `repositories/` - database query layer
- `schemas/` - request/response validation models
- `core/` - DB engine/session setup

### Core Resources
- `services` - treatment catalog
- `clinics` - clinic profile and location/rating data
- `clinic_services` - clinic-to-service offerings
- `appointments` - booking records
- `ratings` - appointment reviews

## Frontend Overview

### State Management Approach
- Uses **React Hooks** extensively:
  - `useState` for local UI state (forms, loading, modals, filters)
  - `useEffect` for lifecycle data fetches and side effects
  - `useMemo` / `useCallback` for derived data and stable handlers in heavier pages

### Component Organization
- `frontend/src/pages/` contains **page-level containers** (route screens, orchestration, data-loading).
- `frontend/src/components/` contains **reusable UI building blocks** (cards, forms, navbar, modals, search widgets).
- This separation keeps feature logic in pages while reusing presentational/interactive components.

### Main Frontend Libraries
- **React** (UI and hooks)
- **Vite** (dev server + build tooling)
- **Tailwind CSS** (styling)
- **React Router** (navigation)
- **Fetch API** for HTTP calls (through `src/services/api.js`)
- Note: this project does **not** currently use Material-UI or Axios.

## Backend Setup

### Prerequisites
- Python 3.12+ (tested on Python 3.13)

### 1) Create and activate a virtual environment
From repository root:

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
From `backend/`:

```bash
pip install -r ../requirements.txt
```

### 3) Configure environment
Create a root `.env` (copy from `.env.example`), then set keys if using AI consult:

```bash
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
GROQ_MODEL=llama-3.1-8b-instant
```

### 4) Initialize database with seed data
From `backend/`:

```bash
python -m app.init_db
```

### 5) Run backend API
From `backend/`:

```bash
uvicorn app.main:app --reload
```

Backend URLs:
- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

### 6) Run backend tests
From `backend/`:

```bash
pytest -q
```

### Common troubleshooting
- **`ModuleNotFoundError: No module named 'app'`**
  - Run backend commands from `backend/`.
- **Stale local data**
  - Delete `backend/treatment_finder.db`, then reseed:
  ```bash
  python -m app.init_db
  ```

## Frontend Setup

### Prerequisites
- Node.js (LTS recommended)
- npm

### 1) Install frontend dependencies
From repository root:

```bash
cd frontend
npm install
```

### 2) Run frontend dev server
From `frontend/`:

```bash
npm run dev
```

Frontend URL: `http://localhost:5173`

### 3) Lint frontend
From `frontend/`:

```bash
npm run lint
```

## Quick Grader Run

Use two terminals from repository root.

### Terminal A (Backend)
```bash
cd backend
.venv\Scripts\Activate.ps1
python -m app.init_db
uvicorn app.main:app --reload
```

### Terminal B (Frontend)
```bash
cd frontend
npm install
npm run dev
```

Verify:
- Frontend: `http://localhost:5173`
- Backend docs: `http://127.0.0.1:8000/docs`

## Optional Docker Run

From repository root:

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```
# Treatment Finder and Appointment Platform

Course project for discovering treatments, comparing clinics, and managing appointments.

## System Architecture

### High-Level
- **Frontend:** React + Vite + Tailwind CSS
- **Backend:** FastAPI + SQLModel + SQLite
- **Communication:** Frontend calls backend REST endpoints (`/api` via Vite proxy in local dev)

### Backend Layers
- `api/` - HTTP routes and request handling
- `services/` - business logic
- `repositories/` - data access queries
- `schemas/` - request/response models and validation
- `core/` - DB engine/session

### Main Resources
- `services` - treatment catalog
- `clinics` - clinics and metadata (city, rating, address)
- `clinic_services` - clinic-to-service mapping
- `appointments` - user bookings
- `ratings` - post-visit reviews

### Project Structure
```text
treatment-finder-platform/
  README.md
  requirements.txt
  .env.example
  docker-compose.yml
  frontend/
    package.json
    vite.config.js
    src/
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
```

## Backend Setup

### Prerequisites
- Python 3.12+ (tested on Python 3.13)

### 1) Create and activate virtual environment
From repository root:

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
Still in `backend/`:

```bash
pip install -r ../requirements.txt
```

### 3) Configure environment
Create `.env` at repository root (copy from `.env.example`) and set keys if using AI consult:

```bash
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
GROQ_MODEL=llama-3.1-8b-instant
```

### 4) Initialize database with seed data
Run from `backend/`:

```bash
python -m app.init_db
```

### 5) Run backend server
Run from `backend/`:

```bash
uvicorn app.main:app --reload
```

Backend URLs:
- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

### 6) Run backend tests
Run from `backend/`:

```bash
pytest -q
```

### Common Backend Troubleshooting
- **`ModuleNotFoundError: No module named 'app'`**
  - Make sure you run backend commands from `backend/`.
- **Stale or inconsistent data**
  - Delete `backend/treatment_finder.db`, then run:
  ```bash
  python -m app.init_db
  ```

## Frontend Setup

### Prerequisites
- Node.js (LTS recommended)
- npm

### 1) Install dependencies
From repository root:

```bash
cd frontend
npm install
```

### 2) Run frontend dev server
From `frontend/`:

```bash
npm run dev
```

Default URL: `http://localhost:5173`

Notes:
- The frontend expects backend APIs to be available.
- In local dev, Vite proxies `/api` requests to the backend.

### 3) Lint frontend
From `frontend/`:

```bash
npm run lint
```

## Quick Grader Run (Recommended)

Open two terminals from repository root.

Terminal A (backend):
```bash
cd backend
.venv\Scripts\Activate.ps1
python -m app.init_db
uvicorn app.main:app --reload
```

Terminal B (frontend):
```bash
cd frontend
npm install
npm run dev
```

Then verify:
- Frontend opens at `http://localhost:5173`
- Backend docs open at `http://127.0.0.1:8000/docs`

## Optional: Docker

From repository root:

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```
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
- **Ex2:** Backend + Frontend (**implemented** — friendly interface)
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

### Frontend (Ex2 — implemented)
- **Stack:** React, **Vite**, and **Tailwind CSS**.
- **Design:** Minimalist, **Apple-style** UI—soft borders, calm typography, and generous spacing for a premium feel.
- Consumes the backend REST APIs (via the Vite dev proxy to `http://localhost:8000` on `/api`).
- Covers treatment discovery, clinic browsing, booking, and appointment management in the browser.

### Additional Microservice (Ex3 target)
- Planned role:
  - extract one domain capability (for example: notifications, recommendations, or clinic catalog sync)
- Will communicate with backend via HTTP/events and run as an independent process/container.

## Exercises Scope

### Ex1 - Backend Only (Foundation)
- FastAPI REST API
- SQLite + SQLModel persistence
- Full CRUD for `appointments`
- Supporting resources: `services`, `clinics`
- **Input validation:** Pydantic/SQLModel `Field` constraints on request/response schemas reject bad payloads early (for example non-empty names, phone format, positive IDs, bounded strings). Invalid input returns **HTTP 422** with validation detail instead of opaque server errors.
- Automated tests (`pytest`)
- Manual HTTP demo file

### Ex2 - Backend + Frontend (Implemented)
- React + Vite + Tailwind CSS SPA with a clean, **Apple-style** visual language.
- **Treatment search** (including AI-assisted discovery on the home experience).
- **Clinic comparison** via featured cards (rating, city, imagery).
- **Appointment booking** with clinic-specific services, availability-aware time slots, and datetime handling aligned with the API.
- **My Appointments:** list, cancel, and reschedule flows.
- **My Favorites (extra):** favorite control on clinic cards and a **My Favorites** entry in the navbar (foundation for a dedicated favorites view in a later iteration).

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
  backend/Dockerfile                # backend image build (Python API)
  docker-compose.yml
  requirements.txt                  # Python dependencies (used by Docker and local install)
  .env.example                      # copy to .env here for local + Compose
  README.md
  .gitignore
  frontend/                         # React + Vite + Tailwind (Ex2 UI)
    package.json
    vite.config.js
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
- **Node.js** + **npm** (for the Ex2 frontend; LTS recommended)
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

### B) Run Frontend Locally (Ex2)

From **repository root**:

```bash
cd frontend
npm install
npm run dev
```

By default the dev server listens on **`http://localhost:5173`**. The Vite config proxies **`/api`** to the backend, so keep the API running locally (section **A**) or adjust `VITE_API_BASE_URL` if you point the UI at another host.

### C) Run Tests (Backend)

From **`backend/`** (with the venv activated):

```bash
pytest -q
```

### D) Run Entire System with Docker Compose (root)

From **repository root**:

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```

## Troubleshooting

- **`ModuleNotFoundError: No module named 'app'` (Python):** All backend commands (`python -m app.init_db`, `uvicorn`, `pytest`, and one-off scripts) must be run with the **current working directory set to `backend/`**, so Python can resolve the `app` package. Alternatively, set `PYTHONPATH` to the `backend` directory—but using `cd backend` is the simplest approach.
- **No clinics or empty lists in the UI:** Seed the database from **`backend/`** with `python -m app.init_db`. If the SQLite file is stale or corrupt, delete `backend/treatment_finder.db` and run `python -m app.init_db` again.

## Microservice Commands (Ex3)

The optional extra service folder is planned for Ex3. When added, run install and start commands from that service’s directory (for example under `services/<service-name>/`).

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
- **Ex1** is the implemented backend foundation; **Ex2** adds the React frontend; **Ex3** will add the optional microservice and Compose orchestration as described above.
