from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "task_tracker", broker=settings.rabbitmq_url, include=["app.email_sender.tasks", "app.scheduler.tasks"]
)
BEAT_SCHEDULE = {
    "send-daily-reports": {
        "task": "app.scheduler.tasks.send_daily_reports",
        "schedule": crontab(minute=0, hour=0),
    },
}
celery_app.conf.update(
    task_serializer="json",
    timezone="Europe/Moscow",
    beat_schedule=BEAT_SCHEDULE,
    task_routes={
        "app.scheduler.tasks.send_daily_reports": {
            "queue": "reports",
        }
    },
)
