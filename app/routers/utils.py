from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category


async def get_all_category_ids(db: AsyncSession, root_category_id: int):
    category_cte = (
        select(Category.id)
        .where(Category.id == root_category_id)
        .cte(name="category_cte", recursive=True)
    )
    subquery = select(Category.id).where(Category.parent_id == category_cte.c.id)
    category_cte = category_cte.union_all(subquery)
    category_ids = await db.scalars(select(category_cte.c.id))

    return category_ids.all()
