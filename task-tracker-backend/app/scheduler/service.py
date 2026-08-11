from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.tasks.models import Task
from app.users.models import User


def get_all_users(session: Session) -> Sequence[User]:
    query = select(User)
    result = session.execute(query)
    return result.scalars().all()


def get_completed_tasks_for_period(
    session: Session, user_id: int, period_start: datetime, period_end: datetime
) -> Sequence[Task]:
    query = select(Task).where(
        Task.user_id == user_id,
        Task.is_done.is_(True),
        Task.completed_at >= period_start,
        Task.completed_at < period_end,
    )
    result = session.execute(query)
    return result.scalars().all()


def get_pending_tasks(session: Session, user_id: int) -> Sequence[Task]:
    query = select(Task).where(Task.user_id == user_id, Task.is_done.is_(False))
    result = session.execute(query)
    return result.scalars().all()
