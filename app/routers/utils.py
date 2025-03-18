from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category


def get_all_category_ids(db: Session, root_category_id: int) -> list[int]:
    category_cte = select(Category.id).where(Category.id == root_category_id).cte(name="category_cte", recursive=True)
    subquery = select(Category.id).where(Category.parent_id == category_cte.c.id)
    category_cte = category_cte.union_all(subquery)
    category_ids = db.scalars(select(category_cte.c.id)).all()

    return category_ids