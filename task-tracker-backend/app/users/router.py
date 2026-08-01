from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.users.exceptions import EmailAlreadyTakenError
from app.users.schemas import UserCreate, UserRead
from app.users.service import create_user

router = APIRouter(tags=["users"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/user", response_model=UserRead)
async def register(data: UserCreate, session: SessionDep):
    try:
        user = await create_user(session, data)
    except EmailAlreadyTakenError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from None

    return user


@router.get("/user", response_model=UserRead)
async def get_current_user():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
