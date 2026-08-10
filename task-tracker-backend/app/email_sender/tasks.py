from app.celery_app import celery_app


@celery_app.task
def send_welcome_email(email: str) -> None:
    print(f"Sending welcome email to {email}")