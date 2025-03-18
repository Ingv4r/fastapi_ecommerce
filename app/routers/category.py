from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models import Category
from app.schemas import CreateCategory
from slugify import slugify

router = APIRouter(prefix="/categories", tags=["category"])


@router.get("/")
async def get_all_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    categories = await db.scalars(select(Category).where(Category.is_active == True))
    return categories.all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(db: Annotated[AsyncSession, Depends(get_db)], create_category: CreateCategory):
    await db.execute(
        insert(Category).values(
            name=create_category.name,
            parent_id=create_category.parent_id,
            slug=slugify(create_category.name),
        )
    )
    await db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.put("/{category_slug}", status_code=status.HTTP_200_OK)
async def update_category(
        db: Annotated[AsyncSession, Depends(get_db)],
        update_category: CreateCategory,
        category_slug: str):
    category = await db.scalar(select(Category).where(Category.slug == category_slug))

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no category found"
        )

    category.name = update_category.name
    category.parent_id = update_category.parent_id
    category.slug = slugify(update_category.name)
    await db.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Product update is successful",
    }


@router.delete("/{category_slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(db: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    category = await db.scalar(
        select(Category).where(Category.slug == category_slug, Category.is_active == True)
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no category found"
        )

    category.is_active = False
    await db.commit()

    return {
        "status_code": status.HTTP_204_NO_CONTENT,
        "transaction": "Product delete is successful",
    }
