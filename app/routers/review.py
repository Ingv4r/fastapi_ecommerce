from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models import Product
from app.models.review import Review
from app.models.user import User
from app.routers.auth import get_current_user
from app.routers.permission import only_admin_permission
from app.schemas import ReviewRead, ReviewCreate
from app.service import get_object_or_404, update_product_rating

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ReviewRead])
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))

    return reviews


@router.get("/{product_slug}", status_code=status.HTTP_200_OK, response_model=list[ReviewRead])
async def products_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await get_object_or_404(db, Product, Product.slug == product_slug, Product.is_active == True)
    reviews = await db.scalars(select(Review).where(Review.product_id == product.id))

    return reviews


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReviewRead)
async def add_review(db: Annotated[AsyncSession, Depends(get_db)],
                     user: Annotated[User, Depends(get_current_user)],
                     create_review: ReviewCreate):
    product = await get_object_or_404(db, Product, Product.id == create_review.product_id)
    review = Review(
        comment=create_review.comment,
        comment_date=datetime.now(),
        grade=create_review.grade,
        user_id=user.id,
        product_id=product.id
    )

    db.add(review)
    await db.commit()
    await db.refresh(review)

    await update_product_rating(db, product.id)

    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reviews(db: Annotated[AsyncSession, Depends(get_db)],
                         _: Annotated[User, Depends(only_admin_permission)],
                         review_id: int) -> None:
    review = await get_object_or_404(db, Review, Review.id == review_id)

    product_id = review.product_id

    review.is_active = False
    await db.commit()
    await db.refresh(review)

    await update_product_rating(db, product_id)
