from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.celery_app import celery_app
from app.database import sync_session_factory
from app.email_sender.tasks import send_daily_report_email
from app.scheduler.service import get_all_users, get_completed_tasks_for_period, get_pending_tasks

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


@celery_app.task
def send_daily_reports() -> None:
    today_start = datetime.now(MOSCOW_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)

    with sync_session_factory() as session:
        users = get_all_users(session)
        for user in users:
            completed_tasks = get_completed_tasks_for_period(session, user.id, yesterday_start, today_start)
            pending_tasks = get_pending_tasks(session, user.id)
            if not completed_tasks and not pending_tasks:
                continue
            completed_titles = [task.title for task in completed_tasks]
            pending_titles = [task.title for task in pending_tasks]
            send_daily_report_email.delay(user.email, completed_titles, pending_titles)
