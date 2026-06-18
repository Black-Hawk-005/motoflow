from typing import Annotated

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
    current_user: Annotated[models.Users, Depends(require_admin)],
):
    result = await db.execute(
        select(models.Users).where(
            or_(
                models.Users.email == user_details.email,
                models.Users.phone == user_details.phone,
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

    new_user = models.Users(
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
