from datetime import datetime, timezone, timedelta

from fastapi import APIRouter
from app.celery.tasks import call_background_task
from app.schemas import CeleryMessage

router = APIRouter(prefix="/celery", tags=["celery"])


@router.post("/countdown", response_model=CeleryMessage)
async def countdown(countdown: int, celery_args: CeleryMessage):
    """Отсроченная на 5 сек задача"""
    call_background_task.apply_async(args=[celery_args.message], countdown=countdown)
    return celery_args


@router.post("/eta/{time_delta}",  response_model=CeleryMessage)
async def eta(time_delta: int, celery_args: CeleryMessage):
    """Задача выполнится в определенное время"""
    task_datetime = datetime.now(timezone.utc) + timedelta(seconds=time_delta)
    call_background_task.apply_async(args=[celery_args.message], eta=task_datetime)
    return celery_args


@router.post("/schedule")
async def schedule(celery_args: CeleryMessage):
    """Выполнение в определенное время. Указано в настройках celery_beat в main.py"""
    call_background_task.apply_async(args=[celery_args.message], expires=3600)
    return celery_args
