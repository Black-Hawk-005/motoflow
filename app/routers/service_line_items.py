from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import get_db
from app.dependencies import get_current_user, require_customer, require_mechanic
from app.schemas import (
    ServiceLineItemCreate,
    ServiceLineItemRead,
    ServiceStatus,
    UserRole,
)

router = APIRouter()


@router.post(
    "/",
    status_code=http_status.HTTP_201_CREATED,
    response_model=ServiceLineItemRead,
)
async def create_line_item(
    line_item_details: ServiceLineItemCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(require_mechanic)],
):
    result = await db.execute(
        select(models.ServiceRequest).where(
            (models.ServiceRequest.id) == line_item_details.service_request_id
        )
    )

    service_request = result.scalar_one_or_none()
    if not service_request:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Service request doesn't exist",
        )

    if service_request.status in (ServiceStatus.PENDING, ServiceStatus.CLOSED):
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Invalid service request status",
        )

    line_item = models.ServiceLineItem(
        service_request_id=service_request.id,
        description=line_item_details.description,
        cost=line_item_details.cost,
    )

    db.add(line_item)
    await db.commit()
    await db.refresh(line_item)

    return line_item


@router.patch("/{line_item_id}/approve", response_model=ServiceLineItemRead)
async def approve_line_item(
    line_item_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(require_customer)],
):
    result = await db.execute(
        select(models.ServiceLineItem).where(
            (models.ServiceLineItem.id) == line_item_id
        )
    )
    line_item = result.scalar_one_or_none()
    if not line_item:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Invalid request",
        )

    result = await db.execute(
        select(models.ServiceRequest).where(
            (models.ServiceRequest.id) == line_item.service_request_id
        )
    )
    service_request = result.scalar_one_or_none()
    if not service_request:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Service request doesn't exist",
        )

    if service_request.customer_id != current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Service request doesn't exist",
        )

    line_item.is_approved = True
    await db.commit()
    await db.refresh(line_item)

    return line_item


@router.get("/", response_model=List[ServiceLineItemRead])
async def list_line_items(
    service_request_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    result = await db.execute(
        select(models.ServiceRequest).where(
            (models.ServiceRequest.id) == service_request_id
        )
    )
    service_request = result.scalar_one_or_none()
    if not service_request:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Service request doesn't exist",
        )

    if (
        current_user.role == UserRole.CUSTOMER
        and service_request.customer_id != current_user.id
    ):
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Service request doesn't exist",
        )

    result = await db.execute(
        select(models.ServiceLineItem).where(
            (models.ServiceLineItem.service_request_id) == service_request_id
        )
    )
    line_items = result.scalars().all()
    return line_items
