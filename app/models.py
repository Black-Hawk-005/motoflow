from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database import Base
from app.schemas import ServiceStatus, UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="userrole"),
    )
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    phone: Mapped[str] = mapped_column(String(15), unique=True)
    password_hash: Mapped[str] = mapped_column(String(128))


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    make: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    year: Mapped[int] = mapped_column(Integer)
    license_plate: Mapped[str] = mapped_column(String(20), unique=True)


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    vehicle_id: Mapped[UUID] = mapped_column(
        ForeignKey("vehicles.id"),
        index=True,
    )
    mechanic_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    initial_complaint: Mapped[str] = mapped_column(Text)
    status: Mapped[ServiceStatus] = mapped_column(
        SAEnum(ServiceStatus, name="servicestatus"),
        default=ServiceStatus.PENDING,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class ServiceLineItem(Base):
    __tablename__ = "service_line_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    service_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("service_requests.id", ondelete="CASCADE"), index=True
    )
    description: Mapped[str] = mapped_column(
        Text,
    )
    cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
    )
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    service_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("service_requests.id", ondelete="CASCADE"),
        index=True,
    )
    author_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
