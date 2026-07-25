from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.auth import hash_password
from app.database import get_db
from app.dependencies import require_admin
from app.schemas import AdminUserCreate, UserRead, UserRole

router = APIRouter()


@router.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_details: AdminUserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(require_admin)],
):
    result = await db.execute(
        select(models.User).where(
            or_(
                models.User.email == user_details.email,
                models.User.phone == user_details.phone,
            )
        )
    )
    existing_user = result.scalars().first()

    if existing_user:
        if existing_user.email == user_details.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        if existing_user.phone == user_details.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered",
            )

    new_user = models.User(
        role=user_details.role,
        full_name=user_details.full_name,
        email=user_details.email,
        phone=user_details.phone,
        password_hash=hash_password(user_details.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.get("/users", response_model=List[UserRead])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(require_admin)],
    approval_state: Optional[bool] = None,
    role: Optional[UserRole] = None,
):
    if role is not None and approval_state is not None:
        result = await db.execute(
            select(models.User).where(
                (models.User.role) == role,
                (models.User.is_approved == approval_state),
            )
        )
    elif role is not None:
        result = await db.execute(
            select(models.User).where(
                (models.User.role) == role,
            )
        )
    elif approval_state is not None:
        result = await db.execute(
            select(models.User).where(
                (models.User.is_approved == approval_state),
            )
        )
    else:
        result = await db.execute(select(models.User))

    users = result.scalars().all()
    return users


@router.patch("/users/{user_id}/approve", response_model=UserRead)
async def approve_new_user(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(require_admin)],
):
    result = await db.execute(select(models.User).where((models.User.id) == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.is_approved = True
    await db.commit()
    await db.refresh(user)
    return user
