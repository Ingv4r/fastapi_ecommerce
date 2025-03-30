from typing import Annotated

from fastapi import APIRouter, Depends
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models import Product, Category
from app.models.user import User
from app.routers.permission import admin_or_supplier_permission
from app.routers.utils import get_all_category_ids
from app.schemas import CreateProduct, GetProduct
from app.service import get_object_or_404

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[GetProduct])
async def available_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(
        select(Product)
        .join(Category)
        .where(Product.is_active == True, Category.is_active == True, Product.stock > 0)
    )

    return products


@router.get("/{category_slug}", status_code=status.HTTP_200_OK, response_model=list[GetProduct])
async def product_by_category(
        db: Annotated[AsyncSession, Depends(get_db)], category_slug: str):

    category = await get_object_or_404(db, Category, Category.slug == category_slug)
    category_ids = await get_all_category_ids(db, category.id)

    products = await db.scalars(
        select(Product).filter(
            Product.category_id.in_(category_ids),
            Product.is_active == True,
            Product.stock > 0,
        )
    )

    return products.all()


@router.get("/detail/{product_slug}", status_code=status.HTTP_200_OK, response_model=GetProduct)
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await get_object_or_404(
        db, Product, Product.slug == product_slug, Product.is_active == True, Product.stock > 0
    )

    return product


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GetProduct)
async def create_product(
        db: Annotated[AsyncSession, Depends(get_db)],
        _: Annotated[User, Depends(admin_or_supplier_permission)],
        product_create: CreateProduct,
        user_id: int):

    category = await get_object_or_404(db, Category, Category.id == product_create.category)
    user = await get_object_or_404(db, User, User.id == user_id)

    product: Product = Product(
        name=product_create.name,
        slug=slugify(product_create.name),
        description=product_create.description,
        price=product_create.price,
        image_url=product_create.image_url,
        stock=product_create.stock,
        rating=0.0,
        category_id=category.id,
        supplier_id=user.id
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)

    return product


@router.put("/{product_slug}", status_code=status.HTTP_200_OK, response_model=GetProduct)
async def update_product(
        db: Annotated[AsyncSession, Depends(get_db)],
        _: Annotated[User, Depends(admin_or_supplier_permission)],
        update_product: CreateProduct,
        product_slug: str,
):
    product = await get_object_or_404(
        db, Product, Product.slug == product_slug
    )
    category = await get_object_or_404(db, Category, Category.id == update_product.category)

    product.name = update_product.name
    product.description = update_product.description
    product.price = update_product.price
    product.image_url = update_product.image_url
    product.stock = update_product.stock
    product.category_id = category.id

    await db.commit()
    await db.refresh(product)

    return product


@router.delete("/{product_slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[User, Depends(admin_or_supplier_permission)],
        product_slug: str):

    product = await get_object_or_404(
        db, Product, Product.slug == product_slug
    )

    product.is_active = False
    await db.commit()
    await db.refresh(product)
