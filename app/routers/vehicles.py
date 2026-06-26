from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import get_db
from app.dependencies import get_current_user, require_customer
from app.schemas import UserRead, UserRole, VehicleCreate, VehicleRead, VehicleUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=VehicleRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_vehicle(
    vehicle_details: VehicleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(require_customer)],
):
    results = await db.execute(
        select(models.Vehicle).where(
            (models.Vehicle.license_plate) == vehicle_details.license_plate
        )
    )
    existing_vehicle = results.scalar_one_or_none()
    if existing_vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle already registered",
        )

    new_vehicle = models.Vehicle(
        customer_id=current_user.id,
        make=vehicle_details.make,
        model=vehicle_details.model,
        year=vehicle_details.year,
        license_plate=vehicle_details.license_plate,
    )
    db.add(new_vehicle)
    await db.commit()
    await db.refresh(new_vehicle)
    return new_vehicle


@router.get(
    "/",
    response_model=List[VehicleRead],
)
async def list_vehicles(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    if current_user.role == UserRole.CUSTOMER:
        result = await db.execute(
            select(models.Vehicle).where(
                (models.Vehicle).customer_id == current_user.id
            )
        )
        user_vehicles = result.scalars().all()
        return user_vehicles

    result = await db.execute(select(models.Vehicle))
    all_vehicles = result.scalars().all()
    return all_vehicles


@router.get("/{vehicle_id}", response_model=VehicleRead)
async def get_vehicle(
    vehicle_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    result = await db.execute(
        select(models.Vehicle).where((models.Vehicle.id) == vehicle_id)
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )
    if (
        current_user.role == UserRole.CUSTOMER
        and vehicle.customer_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )
    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    result = await db.execute(
        select(models.Vehicle).where((models.Vehicle.id) == vehicle_id)
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )

    if (
        current_user.role == UserRole.CUSTOMER
        and vehicle.customer_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )

    await db.execute(delete(models.Vehicle).where(models.Vehicle.id == vehicle_id))
    await db.commit()


@router.patch("/{vehicle_id}", response_model=VehicleRead)
async def update_vehicle(
    vehicle_id: UUID,
    vehicle_details: VehicleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    results = await db.execute(
        select(models.Vehicle).where((models.Vehicle.id == vehicle_id))
    )
    vehicle = results.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    if (
        current_user.role == UserRole.CUSTOMER
        and vehicle.customer_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    update_data = vehicle_details.model_dump(exclude_unset=True)
    if "license_plate" in update_data.keys():
        result = await db.execute(
            select(models.Vehicle).where(
                and_(
                    (models.Vehicle.license_plate) == update_data["license_plate"],
                    (models.Vehicle.id) != vehicle_id,
                )
            )
        )
        existing_vehicle = result.scalar_one_or_none()
        if existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="License plate already registered",
            )

    for field, value in update_data.items():
        setattr(vehicle, field, value)

    await db.commit()
    await db.refresh(
        vehicle, attribute_names=["make", "model", "year", "license_plate"]
    )

    return vehicle
