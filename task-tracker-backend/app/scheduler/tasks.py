from datetime import datetime, timedelta
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from app.celery_app import celery_app
from app.database import sync_session_factory
from app.kafka.consumer import consume_daily_report_responses
from app.kafka.producer import producer, send_daily_report_request
from app.scheduler.schemas import DailyReportRecipient, DailyReportRequest
from app.scheduler.service import get_all_users, get_completed_tasks_for_period, get_pending_tasks

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


@celery_app.task
def send_daily_reports() -> None:
    today_start = datetime.now(MOSCOW_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)

    users_by_request_id: dict[UUID, DailyReportRecipient] = {}
    with sync_session_factory() as session:
        users = get_all_users(session)
        for user in users:
            completed_tasks = get_completed_tasks_for_period(session, user.id, yesterday_start, today_start)
            pending_tasks = get_pending_tasks(session, user.id)
            if not completed_tasks and not pending_tasks:
                continue
            completed_titles = [task.title for task in completed_tasks]
            pending_titles = [task.title for task in pending_tasks]
            request_id = uuid4()
            users_by_request_id[request_id] = DailyReportRecipient(
                email=user.email, completed_titles=completed_titles, pending_titles=pending_titles
            )
            send_daily_report_request(
                DailyReportRequest(
                    request_id=request_id, completed_titles=completed_titles, pending_titles=pending_titles
                )
            )

    producer.flush()
    consume_daily_report_responses(users_by_request_id)
