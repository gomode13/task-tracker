import smtplib

from app.celery_app import celery_app
from app.email_sender.email_client import send_email
from app.email_sender.templates import render_template


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, email: str) -> None:
    subject = "Добро пожаловать в Task Tracker"
    body = (
        "Здравствуйте!\n\n"
        "Ваш аккаунт в Task Tracker успешно создан. "
        "Теперь вы можете войти и начать добавлять задачи.\n\n"
        "С уважением,\n"
        "Task Tracker"
    )
    html = render_template("welcome.html")
    try:
        send_email(email, subject, body, html)
    except (smtplib.SMTPException, OSError) as exc:
        raise self.retry(exc=exc) from None
