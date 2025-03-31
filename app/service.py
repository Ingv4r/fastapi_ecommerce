from typing import Union, Tuple, Any, Annotated

from fastapi import HTTPException, Depends
from sqlalchemy import select, BinaryExpression, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.backend.db_depends import get_db
from app.models import Product
from app.models.review import Review


async def get_object_or_404(
        db: Annotated[AsyncSession, Depends(get_db)],
        model: type,
        *expressions: Union[BinaryExpression, Tuple[BinaryExpression, ...]]
) -> Any:
    query = select(model)

    if expressions:
        if len(expressions) == 1 and isinstance(expressions[0], (tuple, list)):
            query = query.where(*expressions[0])
        else:
            query = query.where(*expressions)

    instance = await db.scalar(query)

    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} not found"
        )

    return instance


async def update_product_rating(db: Annotated[AsyncSession, Depends(get_db)], product_id: int):
    avg_rating = await db.scalar(
        select(func.avg(Review.grade).filter(Review.product_id == product_id, Review.is_active == True))
    )
    await db.execute(
        update(Product)
        .where(Product.id == product_id)
        .values(rating=round(avg_rating or 0.0, 1))
    )
    await db.commit()
