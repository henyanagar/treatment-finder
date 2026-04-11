from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.ai import router as ai_router
from app.api.appointments import router as appointments_router
from app.api.clinics import router as clinics_router
from app.api.search import router as search_router
from app.api.services import router as services_router
from app.core.database import create_db_and_tables
from app.init_db import seed_initial_data

# Repository root .env (same file docker-compose uses); fallback to CWD for a local backend/.env
_root_env = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_root_env if _root_env.is_file() else None)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    seed_initial_data()
    yield


app = FastAPI(title="Treatment Finder Platform API", lifespan=lifespan)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(appointments_router)
app.include_router(services_router)
app.include_router(clinics_router)
app.include_router(search_router)
app.include_router(ai_router)
