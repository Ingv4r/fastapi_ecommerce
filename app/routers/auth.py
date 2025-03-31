from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPBasic, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models.user import User
from app.service import get_object_or_404

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
security = HTTPBasic()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")


async def authenticate_user(db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str):
    user: User = await db.scalar(select(User).where(User.username == username))
    if not user or not bcrypt_context.verify(password, user.hashed_password) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


async def create_access_token(
        username: str,
        first_name: str,
        last_name: str,
        email: str,
        user_id: int,
        is_active: bool,
        is_admin: bool,
        is_supplier: bool,
        is_customer: bool,
        expires_delta: timedelta):

    exp = datetime.now(timezone.utc) + expires_delta
    exp = int(exp.timestamp())

    payload = {
        "username": username,
        "id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "is_active": is_active,
        "is_admin": is_admin,
        "is_supplier": is_supplier,
        "is_customer": is_customer,
        "exp": exp
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[AsyncSession, Depends(get_db)]) -> User:
    """Декодирование токена, получение дынных из payload -> `User`."""
    try:
        payload: dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user = await get_object_or_404(db, User, User.id == payload.get("id"))
        return user
    except jwt.PyJWTError:
        raise HTTPException(
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


@router.post("/token", status_code=status.HTTP_200_OK)
async def login(
        db: Annotated[AsyncSession, Depends(get_db)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    user = await authenticate_user(db, form_data.username, form_data.password)
    token = await create_access_token(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        user_id=user.id,
        is_active=user.is_active,
        is_admin=user.is_admin,
        is_supplier=user.is_supplier,
        is_customer=user.is_customer,
        expires_delta=timedelta(minutes=30)
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
