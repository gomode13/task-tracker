import logging
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.tasks.exceptions import TaskNotFoundError
from app.tasks.models import Task
from app.tasks.schemas import TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)


async def get_user_tasks(session: AsyncSession, user_id: int) -> Sequence[Task]:
    query = select(Task).where(Task.user_id == user_id).order_by(Task.id.desc())
    result = await session.execute(query)
    return result.scalars().all()


async def get_user_task_by_id(session: AsyncSession, task_id: int, user_id: int) -> Task:
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        logger.warning("Task not found: task_id=%s, user_id=%s", task_id, user_id)
        raise TaskNotFoundError()

    return task


async def create_user_task(session: AsyncSession, user_id: int, data: TaskCreate) -> Task:
    task = Task(user_id=user_id, title=data.title)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    logger.info("Task created: id=%s, user_id=%s", task.id, task.user_id)
    return task


async def update_user_task(session: AsyncSession, task_id: int, data: TaskUpdate, user_id: int) -> Task:
    task = await get_user_task_by_id(session, task_id, user_id)
    data_for_update = data.model_dump(exclude_unset=True)

    if "is_done" in data_for_update and data_for_update["is_done"] != task.is_done:
        if data_for_update["is_done"]:
            task.completed_at = datetime.now(UTC)
        else:
            task.completed_at = None

    for attr, value in data_for_update.items():
        setattr(task, attr, value)

    await session.commit()
    await session.refresh(task)
    logger.info("Task updated: id=%s, user_id=%s", task.id, task.user_id)
    return task


async def delete_user_task(session: AsyncSession, task_id: int, user_id: int) -> None:
    task = await get_user_task_by_id(session, task_id, user_id)
    await session.delete(task)
    logger.info("Task deleted: id=%s, user_id=%s", task.id, task.user_id)
    await session.commit()
