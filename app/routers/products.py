from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from slugify import slugify
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models import Product, Category
from app.routers.utils import get_all_category_ids
from app.schemas import CreateProduct, GetProduct

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[GetProduct])
async def available_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(
        select(Product)
        .join(Category)
        .where(Product.is_active == True, Category.is_active == True, Product.stock > 0)
    )

    return products


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GetProduct)
async def create_product(
        db: Annotated[AsyncSession, Depends(get_db)], create_product: CreateProduct
):
    category = await db.scalar(select(Category).where(Category.id == create_product.category))

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no category found"
        )

    await db.execute(
        insert(Product).values(
            name=create_product.name,
            slug=slugify(create_product.name),
            description=create_product.description,
            price=create_product.price,
            image_url=create_product.image_url,
            stock=create_product.stock,
            rating=0.0,
            category_id=create_product.category,
        )
    )

    await db.commit()

    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.get("/{category_slug}", status_code=status.HTTP_200_OK)
async def product_by_category(
        db: Annotated[AsyncSession, Depends(get_db)], category_slug: str
):
    category = await db.scalar(select(Category).where(Category.slug == category_slug))
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    category_ids = await get_all_category_ids(db, category.id)

    products = await db.scalars(
        select(Product).filter(
            Product.category_id.in_(category_ids),
            Product.is_active == True,
            Product.stock > 0,
        )
    )

    return products.all()


@router.get("/detail/{product_slug}", status_code=status.HTTP_200_OK)
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(
        select(Product).where(
            Product.slug == product_slug, Product.is_active == True, Product.stock > 0
        )
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no product found"
        )
    return product


@router.put("/{product_slug}")
async def update_product(
        db: Annotated[AsyncSession, Depends(get_db)],
        update_product: CreateProduct,
        product_slug: str,
):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no product found"
        )

    category = await db.scalar(select(Category).where(Category.id == update_product.category))
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    product.name = update_product.name
    product.description = update_product.description
    product.price = update_product.price
    product.image_url = update_product.image_url
    product.stock = update_product.stock
    product.category_id = update_product.category

    await db.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Category update is successful",
    }


@router.delete("/{product_slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="There is no product found"
        )
    product.is_active = False
    await db.commit()
    return {
        "status_code": status.HTTP_204_NO_CONTENT,
        "transaction": "Product delete is successful",
    }
