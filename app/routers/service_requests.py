from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import get_db
from app.dependencies import get_current_user, require_customer, require_roles
from app.schemas import (
    ServiceRequestCreate,
    ServiceRequestRead,
    ServiceRequestReject,
    ServiceRequestUpdate,
    ServiceStatus,
    UserRole,
)

router = APIRouter()
VALID_TRANSITIONS = {
    ServiceStatus.PENDING: {ServiceStatus.ASSIGNED},
    ServiceStatus.ASSIGNED: {ServiceStatus.IN_PROGRESS},
    ServiceStatus.IN_PROGRESS: {ServiceStatus.ACTION_REQUIRED},
    ServiceStatus.APPROVED: {
        ServiceStatus.COMPLETED,
        ServiceStatus.IN_PROGRESS,
    },
    ServiceStatus.COMPLETED: {ServiceStatus.CLOSED},
}


@router.post(
    "/", status_code=http_status.HTTP_201_CREATED, response_model=ServiceRequestRead
)
async def create_service_request(
    request_details: ServiceRequestCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(require_customer)],
):
    result = await db.execute(
        select(models.Vehicle).where((models.Vehicle.id) == request_details.vehicle_id)
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Vehicle not found."
        )
    if vehicle.customer_id != current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Vehicle not found."
        )

    request = models.ServiceRequest(
        customer_id=current_user.id,
        vehicle_id=vehicle.id,
        initial_complaint=request_details.initial_complaint,
    )
    db.add(request)

    await db.commit()
    await db.refresh(request)

    return request


@router.get("/", response_model=List[ServiceRequestRead])
async def list_service_requests(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    if current_user.role == UserRole.CUSTOMER:
        result = await db.execute(
            select(models.ServiceRequest).where(
                (models.ServiceRequest.customer_id) == current_user.id
            )
        )
        requests = result.scalars().all()
        return requests

    if current_user.role == UserRole.MECHANIC:
        result = await db.execute(
            select(models.ServiceRequest).where(
                (models.ServiceRequest.mechanic_id) == current_user.id
            )
        )
        requests = result.scalars().all()
        return requests

    result = await db.execute(select(models.ServiceRequest))
    requests = result.scalars().all()
    return requests


@router.get("/{request_id}", response_model=ServiceRequestRead)
async def get_service_request(
    request_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    result = await db.execute(
        select(models.ServiceRequest).where((models.ServiceRequest.id) == request_id)
    )
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )

    if (
        current_user.role == UserRole.CUSTOMER
        and request.customer_id != current_user.id
    ):
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Request not found"
        )

    return request


@router.patch(
    "/{request_id}",
    response_model=ServiceRequestRead,
)
async def update_request(
    request_id: UUID,
    update_details: ServiceRequestUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        models.User,
        Depends(
            require_roles(
                UserRole.MECHANIC,
                UserRole.ADMIN,
            )
        ),
    ],
):
    update_data = update_details.model_dump(exclude_unset=True)
    result = await db.execute(
        select(models.ServiceRequest).where((models.ServiceRequest.id) == request_id)
    )
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )

    if "mechanic_id" in update_data:
        if current_user.role == UserRole.MECHANIC:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Admin only operation performed",
            )
        if not update_data.get("mechanic_id") or (
            request.status == ServiceStatus.PENDING
            and update_data.get("status") != ServiceStatus.ASSIGNED
        ):
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Invalid request",
            )

        result = await db.execute(
            select(models.User).where(
                models.User.id == update_data["mechanic_id"],
                models.User.role == UserRole.MECHANIC,
            )
        )
        mechanic = result.scalar_one_or_none()
        if mechanic is None:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Invalid request",
            )

    if "status" in update_data and update_data.get(
        "status"
    ) not in VALID_TRANSITIONS.get(request.status, set()):
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Invalid status change",
        )

    for field, value in update_data.items():
        setattr(request, field, value)

    await db.commit()
    await db.refresh(request)

    return request


@router.patch(
    "/{request_id}/approve",
    response_model=ServiceRequestRead,
)
async def approve_request(
    request_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        models.User,
        Depends(require_customer),
    ],
):
    result = await db.execute(
        select(models.ServiceRequest).where((models.ServiceRequest.id) == request_id)
    )
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )

    if request.customer_id != current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )

    if request.status != ServiceStatus.ACTION_REQUIRED:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Invalid status change",
        )

    result = await db.execute(
        select(models.ServiceLineItem).where(
            (models.ServiceLineItem.service_request_id) == request_id
        )
    )
    line_items = result.scalars().all()

    for line_item in line_items:
        if line_item.is_approved == False:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="All line items are not approved"
            )

    request.status = ServiceStatus.APPROVED

    await db.commit()
    await db.refresh(request)

    return request


@router.patch(
    "/{request_id}/reject",
    response_model=ServiceRequestRead,
)
async def reject_request(
    reject_details: ServiceRequestReject,
    request_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        models.User,
        Depends(require_customer),
    ],
):
    result = await db.execute(
        select(models.ServiceRequest).where((models.ServiceRequest.id) == request_id)
    )
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )

    if request.customer_id != current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )

    if request.status != ServiceStatus.ACTION_REQUIRED:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Invalid status change",
        )

    request.status = ServiceStatus.IN_PROGRESS
    reject_comment = models.Comment(
        service_request_id=request_id,
        author_id=current_user.id,
        message=reject_details.message,
    )

    db.add(reject_comment)
    await db.commit()
    await db.refresh(request)

    return request
