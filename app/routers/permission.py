from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas import GetUser, UserStatusUpdate
from app.service import get_object_or_404

router = APIRouter(prefix="/permission", tags=["permission"])


async def only_admin_permission(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not user.is_admin:
        raise HTTPException(
            detail="You must be admin user for this",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return user


@router.patch("/user_status/{user_id}", response_model=GetUser, status_code=status.HTTP_200_OK)
async def change_user_status_by_admin(
    user_id: int,
    user_data: UserStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(only_admin_permission)],
):
    target_user = await get_object_or_404(db, User, User.id == user_id)
    target_user.is_admin = user_data.is_admin
    target_user.is_supplier = user_data.is_supplier
    target_user.is_customer = user_data.is_customer
    await db.commit()
    await db.refresh(target_user)
    return target_user
