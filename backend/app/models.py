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
    reviews_count: int = Field(default=0, ge=0)
    opening_hours: Optional[str] = Field(default="09:00 - 19:00", max_length=50)
    image_url: Optional[str] = None

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


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = Field(index=True, min_length=1, max_length=120)
    email: str = Field(index=True, unique=True, min_length=3, max_length=255)
    phone: str = Field(min_length=7, max_length=20, regex=r"^\+?\d{7,20}$")

    appointments: List["Appointment"] = Relationship(back_populates="user")


class Appointment(SQLModel, table=True):
    __tablename__ = "appointments"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, gt=0)
    notes: Optional[str] = Field(default=None, max_length=1000)
    appointment_datetime: datetime = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
    status: Optional[str] = Field(default=None, index=True, max_length=20)
    rating_id: Optional[int] = Field(default=None, foreign_key="ratings.id", index=True)

    service_id: int = Field(foreign_key="services.id", index=True)
    clinic_id: int = Field(foreign_key="clinics.id", index=True)

    service: Optional[Service] = Relationship(back_populates="appointments")
    clinic: Optional[Clinic] = Relationship(back_populates="appointments")
    user: Optional[User] = Relationship(back_populates="appointments")


class Rating(SQLModel, table=True):
    __tablename__ = "ratings"

    id: Optional[int] = Field(default=None, primary_key=True)
    appointment_id: int = Field(foreign_key="appointments.id", index=True, unique=True)
    clinic_id: int = Field(foreign_key="clinics.id", index=True)
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = Field(default=None, max_length=120)
    review: Optional[str] = Field(default=None, max_length=2000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
