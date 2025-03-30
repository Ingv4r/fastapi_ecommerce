from typing import Union, Tuple, Any

from fastapi import HTTPException
from sqlalchemy import select, BinaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


async def get_object_or_404(
        db_session: AsyncSession,
        model: type,
        *expressions: Union[BinaryExpression, Tuple[BinaryExpression, ...]]
) -> Any:
    """
    Получает объект из БД или возвращает 404 ошибку.

    Args:
        db_session: Асинхронная сессия SQLAlchemy
        model: Модель SQLAlchemy
        *expressions: Одно или несколько условий фильтрации

    Returns:
        Найденный объект модели

    Raises:
        HTTPException: 404 если объект не найден
    """
    query = select(model)

    if expressions:
        if len(expressions) == 1 and isinstance(expressions[0], (tuple, list)):
            query = query.where(*expressions[0])
        else:
            query = query.where(*expressions)

    instance = await db_session.scalar(query)

    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} not found"
        )

    return instance
