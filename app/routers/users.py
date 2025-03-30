from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models.user import User
from app.routers.auth import bcrypt_context, get_current_user
from app.schemas import GetUser, CreateUser
from app.service import get_object_or_404

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GetUser)
async def create_user(db: Annotated[AsyncSession, Depends(get_db)], user: CreateUser):
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        hashed_password=bcrypt_context.hash(user.password)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[GetUser])
async def read_users(db: Annotated[AsyncSession, Depends(get_db)],
                     get_user: Annotated[dict, Depends(get_current_user)]):
    if not get_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")

    users = await db.scalars(select(User).where(User.is_active == True))
    return users


@router.get("/me", response_model=GetUser)
async def read_current_user(current_user: GetUser = Depends(get_current_user)):
    return current_user


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        _: Annotated[dict, Depends(get_current_user)], user_id: int):
    user = await get_object_or_404(db, User, User.id == user_id)
    await db.delete(user)
    await db.commit()


