from celery import Celery

from app.config import settings

celery_app = Celery("task_tracker", broker=settings.rabbitmq_url, include=['app.email_sender.tasks'])
