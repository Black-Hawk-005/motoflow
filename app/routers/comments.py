from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import (
    CommentAuthor,
    CommentCreate,
    CommentRead,
    UserRole,
)

router = APIRouter()


@router.post(
    "/",
    response_model=CommentRead,
    status_code=http_status.HTTP_201_CREATED,
)
async def post_comment(
    comment_details: CommentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    results = await db.execute(
        select(models.ServiceRequest).where(
            (models.ServiceRequest.id) == comment_details.service_request_id
        )
    )
    service_request = results.scalar_one_or_none()
    if not service_request:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="No service request found",
        )

    if (
        current_user.role == UserRole.CUSTOMER
        and service_request.customer_id != current_user.id
    ) or (
        current_user.role == UserRole.MECHANIC
        and service_request.mechanic_id != current_user.id
    ):
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="No service request found",
        )

    comment_author = CommentAuthor.model_validate(current_user)
    comment = models.Comment(
        service_request_id=service_request.id,
        author_id=comment_author.id,
        message=comment_details.message,
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return CommentRead(
        id=comment.id,
        service_request_id=service_request.id,
        author=comment_author,
        message=comment.message,
        created_at=comment.created_at,
    )


@router.get("/", response_model=List[CommentRead])
async def list_comments(
    service_request_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    results = await db.execute(
        select(models.ServiceRequest).where(
            (models.ServiceRequest.id) == service_request_id
        )
    )
    service_request = results.scalar_one_or_none()
    if not service_request:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="No service request found",
        )

    if (
        current_user.role == UserRole.CUSTOMER
        and service_request.customer_id != current_user.id
    ) or (
        current_user.role == UserRole.MECHANIC
        and service_request.mechanic_id != current_user.id
    ):
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="No service request found",
        )

    results = await db.execute(
        select(models.Comment).where(
            (models.Comment.service_request_id) == service_request_id
        )
    )
    comments = results.scalars().all()
    author_ids = {c.author_id for c in comments}
    authors = await db.execute(
        select(models.User).where(models.User.id.in_(author_ids))
    )
    users_by_id = {u.id: u for u in authors.scalars().all()}
    return [
        CommentRead(
            id=c.id,
            service_request_id=c.service_request_id,
            author=CommentAuthor.model_validate(users_by_id[c.author_id]),
            message=c.message,
            created_at=c.created_at,
        )
        for c in comments
    ]
