from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models import Category
from app.models.user import User
from app.routers.permission import only_admin_permission
from app.schemas import CreateCategory, GetCategory
from slugify import slugify

from app.service import get_object_or_404

router = APIRouter(prefix="/categories", tags=["category"])


@router.get("/", response_model=list[GetCategory])
async def get_all_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    categories = await db.scalars(select(Category).where(Category.is_active == True))
    return categories


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GetCategory)
async def create_category(db: Annotated[AsyncSession, Depends(get_db)],
                          _: Annotated[User, Depends(only_admin_permission)],
                          category_create: CreateCategory):
    category = Category(
            name=category_create.name,
            parent_id=category_create.parent_id,
            slug=slugify(category_create.name),
        )
    db.add(category)
    await db.commit()
    await db.refresh(category)

    return category


@router.put("/{category_slug}", status_code=status.HTTP_200_OK, response_model=GetCategory)
async def update_category(
        db: Annotated[AsyncSession, Depends(get_db)],
        _: Annotated[User, Depends(only_admin_permission)],
        category_update: CreateCategory,
        category_slug: str):
    category = await get_object_or_404(db, Category, Category.slug == category_slug)

    category.name = category_update.name
    category.parent_id = category_update.parent_id
    category.slug = slugify(category_update.name)
    await db.commit()
    await db.refresh(category)

    return category


@router.delete("/{category_slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(db: Annotated[AsyncSession, Depends(get_db)],
                          _: Annotated[User, Depends(only_admin_permission)],
                          category_slug: str) -> None:
    category = await get_object_or_404(db, Category, Category.slug == category_slug)

    category.is_active = False
    await db.commit()
    await db.refresh(category)
