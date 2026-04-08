from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.appointments import router as appointments_router
from app.api.clinics import router as clinics_router
from app.api.services import router as services_router
from app.db import create_db_and_tables


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Treatment Finder Platform API", lifespan=lifespan)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(appointments_router)
app.include_router(services_router)
app.include_router(clinics_router)
