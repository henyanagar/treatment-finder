from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings


def _resolve_database_url(raw_url: str) -> str:
    """Resolve relative SQLite file paths against the backend folder."""
    url = make_url(raw_url)
    if url.drivername != "sqlite":
        return raw_url
    # In SQLAlchemy SQLite URLs, the DB file path is stored in `database`.
    db_path = url.database
    if not db_path or db_path == ":memory:":
        return raw_url
    path_obj = Path(db_path)
    if path_obj.is_absolute():
        return raw_url
    backend_dir = Path(__file__).resolve().parents[2]
    absolute_db_path = (backend_dir / path_obj).resolve()
    return f"sqlite:///{absolute_db_path.as_posix()}"


connect_args = {"check_same_thread": False}
engine = create_engine(
    _resolve_database_url(settings.DATABASE_URL),
    connect_args=connect_args,
    echo=False,
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    # Lightweight compatibility migration for local SQLite DBs created before status support.
    with engine.begin() as connection:
        columns = connection.execute(text("PRAGMA table_info(appointments)")).fetchall()
        column_names = {row[1] for row in columns}
        if "status" not in column_names:
            connection.execute(text("ALTER TABLE appointments ADD COLUMN status VARCHAR(20)"))

        clinic_columns = connection.execute(text("PRAGMA table_info(clinics)")).fetchall()
        clinic_column_names = {row[1] for row in clinic_columns}
        if "opening_hours" not in clinic_column_names:
            connection.execute(text("ALTER TABLE clinics ADD COLUMN opening_hours VARCHAR(50)"))
        connection.execute(
            text(
                "UPDATE clinics SET opening_hours = '09:00 - 19:00' "
                "WHERE opening_hours IS NULL OR TRIM(opening_hours) = ''"
            )
        )


def get_session():
    with Session(engine) as session:
        yield session
