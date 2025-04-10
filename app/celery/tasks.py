import time

from celery import shared_task


@shared_task()
def call_background_task(message):
    print(f"Background Task called: {message}")


@shared_task(queue='high_priority')
def high_priority_task(message):
    print(f"Выполнение задачи высокого приоритета: {message}")


@shared_task(queue='low_priority')
def low_priority_task():
    print("Выполнение задачи низкого приоритета")