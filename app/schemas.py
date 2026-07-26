from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(str, Enum):
    CUSTOMER = "customer"
    MECHANIC = "mechanic"
    ADMIN = "admin"


class ServiceStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    ACTION_REQUIRED = "action_required"
    APPROVED = "approved"
    COMPLETED = "completed"
    CLOSED = "closed"


class AdminUserCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: str = Field(pattern=r"^\+?[1-9]\d{9,14}$")
    role: UserRole


class UserCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: str = Field(pattern=r"^\+?[1-9]\d{9,14}$")


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    role: UserRole
    phone: str
    is_approved: bool


class VehicleCreate(BaseModel):
    make: str = Field(min_length=4, max_length=50)
    model: str = Field(min_length=4, max_length=50)
    year: int = Field(gt=1885)
    license_plate: str = Field(min_length=8)


class VehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    make: str
    model: str
    year: int
    license_plate: str


class VehicleUpdate(BaseModel):
    make: Optional[str] = Field(default=None, min_length=4, max_length=50)
    model: Optional[str] = Field(default=None, min_length=4, max_length=50)
    year: Optional[int] = Field(default=None, gt=1885)
    license_plate: Optional[str] = Field(default=None, min_length=8)


class ServiceRequestCreate(BaseModel):
    vehicle_id: UUID
    initial_complaint: str = Field(min_length=10)


class AssignedMechanic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str


class CustomerContact(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    phone: str


class ServiceRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    vehicle_id: UUID
    mechanic_id: Optional[UUID]
    mechanic: Optional[AssignedMechanic] = None
    customer: Optional[CustomerContact] = None
    initial_complaint: str
    status: ServiceStatus
    created_at: datetime
    updated_at: datetime


class ServiceRequestUpdate(BaseModel):
    mechanic_id: Optional[UUID] = None
    status: Optional[ServiceStatus] = None


class ServiceRequestReject(BaseModel):
    message: str


class ServiceLineItemCreate(BaseModel):
    service_request_id: UUID
    description: str = Field(min_length=10)
    cost: Decimal = Field(gt=0)


class ServiceLineItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_request_id: UUID
    description: str
    cost: Decimal
    is_approved: bool


class ServiceLineItemUpdate(BaseModel):
    description: Optional[str] = Field(default=None, min_length=10)
    cost: Optional[Decimal] = Field(default=None, gt=0)


class CommentCreate(BaseModel):
    service_request_id: UUID
    message: str = Field(min_length=10)


class CommentAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    role: UserRole


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_request_id: UUID
    author: CommentAuthor
    message: str
    created_at: datetime
