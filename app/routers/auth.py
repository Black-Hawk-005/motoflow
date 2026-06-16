from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.auth import hash_password
from app.database import get_db
from app.schemas import UserCreate, UserRead, UserRole

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_details: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]
):

    result = await db.execute(
        select(models.Users).where(
            or_(
                models.Users.email == user_details.email,
                models.Users.phone_number == user_details.phone,
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
        if existing_user.phone_number == user_details.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered",
            )

    new_user = models.Users(
        role=user_details.role,
        full_name=user_details.full_name,
        email=user_details.email,
        phone_number=user_details.phone,
        password_hash=hash_password(user_details.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
