from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models import Product
from app.models.review import Review
from app.schemas import ReviewRead
from app.service import get_object_or_404


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ReviewRead])
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))

    return reviews


@router.get("/pro/iduct_id}", response_model=list[ReviewRead])
async def products_reviews():
    pass