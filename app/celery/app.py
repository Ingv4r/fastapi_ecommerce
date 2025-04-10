from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    'app',
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0',
    broker_connection_retry_on_startup=True
)

celery_app.conf.beat_schedule = {
    'run-me-background-task': {
        'task': 'app.celery.tasks.high_priority_task',
        'schedule': crontab(hour=7, minute=0),
        'args': ('Test text message',)
    }
}

celery_app.autodiscover_tasks(['app.celery'])