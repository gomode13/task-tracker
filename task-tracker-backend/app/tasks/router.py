from fastapi import APIRouter, HTTPException, status

from app.dependencies import SessionDep
from app.tasks.exceptions import TaskNotFoundError
from app.tasks.schemas import TaskCreate, TaskRead, TaskUpdate
from app.tasks.service import create_user_task, delete_user_task, get_user_tasks, update_user_task
from app.users.dependencies import CurrentUserDep

router = APIRouter(tags=["tasks"])


@router.get("/tasks", response_model=list[TaskRead])
async def get_tasks(session: SessionDep, user: CurrentUserDep):
    return await get_user_tasks(session, user.id)


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(session: SessionDep, user: CurrentUserDep, data: TaskCreate):
    return await create_user_task(session, user.id, data)


@router.patch("/tasks/{task_id}", response_model=TaskRead)
async def update_task(session: SessionDep, task_id: int, user: CurrentUserDep, data: TaskUpdate):
    try:
        return await update_user_task(session, task_id, data, user.id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from None


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(session: SessionDep, task_id: int, user: CurrentUserDep):
    try:
        await delete_user_task(session, task_id, user.id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from None
