# Treatment Finder and Appointment Platform

Treatment Finder is a full-stack course project for discovering treatments, matching clinics, booking appointments, and rating completed visits.

## Project Overview

The platform supports:
- treatment discovery (keyword search and AI semantic consultation),
- clinic comparison,
- appointment booking and management,
- post-visit rating and clinic score updates.

## System Architecture

### High-Level
- **Frontend:** React + Vite + Tailwind CSS
- **Backend:** FastAPI + SQLModel + SQLite
- **Communication:** Frontend consumes backend REST APIs (`/api`).

### Backend Layers
- **`api/`** - HTTP routes/controllers and response wiring
- **`services/`** - business rules and orchestration
- **`repositories/`** - SQLModel/SQLAlchemy data access
- **`schemas/`** - request/response contracts and validation
- **`core/` + `database.py`** - DB engine/session lifecycle and compatibility helpers

### Smart AI Semantic Consultant (`POST /ai/consult`)
- Uses a **dynamic DB-backed service catalog** as prompt context (no hardcoded treatment mapping for matching).
- Model strategy:
  - Primary: **Groq** (Llama 3.1 family)
  - Failover: **Gemini**
  - Fallback: local keyword-style matching when providers are unavailable.
- Returns structured output with:
  - `matched_service_ids`, `matched_service_names`,
  - clinic recommendations,
  - `reason`, `explanation`, and `confidence_score`.

## Environment Variables

Create root `.env` from `.env.example`.

Required:

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

## Quick Start (Recommended for Grading)

Open **two terminals** from repository root.

### Terminal A - Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r ../requirements.txt
python -m app.init_db
uvicorn app.main:app --reload
```

### Terminal B - Frontend

```bash
cd frontend
npm install
npm run dev
```

Access:
- Frontend (local dev): [http://localhost:5173](http://localhost:5173)
- Backend docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r ../requirements.txt
python -m app.init_db
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest -q
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Run lint:

```bash
npm run lint
```

## Docker Deployment

Run from repository root:

```bash
docker-compose up --build
```

Access:
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Notes:
- `docker-compose.yml` loads root `.env` using `env_file: .env`.
- Backend receives `DATABASE_URL`, `GROQ_API_KEY`, `GEMINI_API_KEY`, and `GROQ_MODEL`.
- Backend container seeds DB automatically on startup before launching Uvicorn.

Stop:

```bash
docker-compose down
```

## Verification Checklist

- [ ] `docker-compose up --build` starts both services
- [ ] Backend docs open at [http://localhost:8000/docs](http://localhost:8000/docs)
- [ ] Frontend opens at [http://localhost:3000](http://localhost:3000) (Docker) or [http://localhost:5173](http://localhost:5173) (local)
- [ ] Search works and returns expected clinics
- [ ] Booking allows valid future slots
- [ ] Upcoming / Past visits separation is correct
- [ ] Cancel sets status to `CANCELLED` and moves appointment to Past
- [ ] Rating is single-submit per appointment
- [ ] Clinic `rating` and `reviews_count` update after review
