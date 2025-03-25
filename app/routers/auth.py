from __future__ import annotations

import os
import jwt

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPBasic, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, insert
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models.user import User
from app.schemas import CreateUser
from app.backend.db_depends import get_db
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone


load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
security = HTTPBasic()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
print(ALGORITHM)


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
        username: str, user_id: int, is_admin: bool,
        is_superuser: bool, is_customer: bool, expires_delta: timedelta):

    exp = datetime.now(timezone.utc) + expires_delta
    exp = int(exp.timestamp())

    payload = {
        "sub": username,
        "id": user_id,
        "is_admin": is_admin,
        "is_superuser": is_superuser,
        "is_customer": is_customer,
        "exp": exp
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        user_id: int | None = payload.get("id")
        is_admin: bool | None = payload.get("is_admin")
        is_superuser: bool | None = payload.get("is_superuser")
        is_customer: bool | None = payload.get("is_customer")
        expire: int | None = payload.get("exp")

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
        if expire is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No access token supplied")
        if not isinstance(expire, int):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token format")

        current_time = datetime.now(timezone.utc).timestamp()

        if expire < current_time:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired!")

        return {
            "username": username,
            "id": user_id,
            "is_admin": is_admin,
            "is_superuser": is_superuser,
            "is_customer": is_customer,
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired!")

    except jwt.PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: Annotated[AsyncSession, Depends(get_db)], user: CreateUser):
    await db.execute(insert(User).values(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        hashed_password=bcrypt_context.hash(user.password)
    ))
    await db.commit()
    return {
        "status_code": status.HTTP_201_CREATED,
        "transaction": "User created successfully"
    }


@router.post("/token", status_code=status.HTTP_200_OK)
async def login(
        db: Annotated[AsyncSession, Depends(get_db)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    user = await authenticate_user(db, form_data.username, form_data.password)
    token = await create_access_token(
        user.username, user.id, user.is_admin, user.is_supplier,
        user.is_customer, expires_delta=timedelta(minutes=20)
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/read_current_user")
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user
