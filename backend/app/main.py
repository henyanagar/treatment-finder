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

# Load secrets from disk in a fixed order (never commit .env). Compose uses the same root `.env`.
_main = Path(__file__).resolve()
for _env_path in (_main.parents[2] / ".env", _main.parents[1] / ".env"):
    if _env_path.is_file():
        load_dotenv(_env_path)
        break
else:
    load_dotenv()


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
