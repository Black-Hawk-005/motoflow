from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.dependencies import get_current_user
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
                detail="Details given are already registered",
            )
        if existing_user.phone == user_details.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Details given are already registered",
            )

    new_user = models.User(
        role=UserRole.CUSTOMER,
        full_name=user_details.full_name,
        email=user_details.email,
        phone=user_details.phone,
        password_hash=hash_password(user_details.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login")
async def login(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.User).where((models.User.email) == request_form.username)
    )
    existing_user = result.scalar_one_or_none()
    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Check your request and try again",
        )

    # Password verification
    if not verify_password(request_form.password, existing_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Check your request and try again",
        )

    token = create_access_token(
        {
            "sub": str(existing_user.id),
            "role": existing_user.role.value,
        }
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: Annotated[models.User, Depends(get_current_user)]):
    return current_user
