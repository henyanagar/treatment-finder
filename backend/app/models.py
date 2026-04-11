from datetime import UTC, datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class TreatmentCategory(SQLModel, table=True):
    __tablename__ = "treatment_categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None

    services: List["Service"] = Relationship(back_populates="category")


class Service(SQLModel, table=True):
    __tablename__ = "services"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    category_id: Optional[int] = Field(default=None, foreign_key="treatment_categories.id", index=True)
    treatment_type: Optional[str] = Field(default=None, index=True)
    invasiveness_level: Optional[str] = Field(default=None, index=True)
    is_technology_based: bool = Field(default=False, index=True)
    recovery_level: Optional[str] = Field(default=None, index=True)

    category: Optional[TreatmentCategory] = Relationship(back_populates="services")
    clinic_links: List["ClinicServiceLink"] = Relationship(back_populates="service")
    appointments: List["Appointment"] = Relationship(back_populates="service")


class Clinic(SQLModel, table=True):
    __tablename__ = "clinics"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    address: str
    city: str = Field(index=True)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = Field(default=None, ge=0, le=5)

    service_links: List["ClinicServiceLink"] = Relationship(back_populates="clinic")
    appointments: List["Appointment"] = Relationship(back_populates="clinic")


class ClinicServiceLink(SQLModel, table=True):
    __tablename__ = "clinic_services"

    id: Optional[int] = Field(default=None, primary_key=True)
    clinic_id: int = Field(foreign_key="clinics.id", index=True)
    service_id: int = Field(foreign_key="services.id", index=True)
    price: Optional[float] = Field(default=None, ge=0)
    is_available: bool = Field(default=True, index=True)

    clinic: Optional[Clinic] = Relationship(back_populates="service_links")
    service: Optional[Service] = Relationship(back_populates="clinic_links")


# Backward-compatible alias for existing imports.
ClinicService = ClinicServiceLink


class Appointment(SQLModel, table=True):
    __tablename__ = "appointments"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_full_name: str = Field(index=True, min_length=2, max_length=120)
    user_phone: str = Field(min_length=7, max_length=20)
    notes: Optional[str] = Field(default=None, max_length=1000)
    appointment_datetime: datetime = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)

    service_id: int = Field(foreign_key="services.id", index=True)
    clinic_id: int = Field(foreign_key="clinics.id", index=True)

    service: Optional[Service] = Relationship(back_populates="appointments")
    clinic: Optional[Clinic] = Relationship(back_populates="appointments")
