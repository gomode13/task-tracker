from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.redis_client import get_redis_client
from app.users.exceptions import EmailAlreadyTakenError, InvalidCredentialsError
from app.users.schemas import UserCreate, UserLogin, UserRead
from app.users.security import create_access_token, create_refresh_token
from app.users.service import authenticate_user, create_user
from app.users.token_storage import save_refresh_token

router = APIRouter(tags=["users"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated[Redis, Depends(get_redis_client)]


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


@router.post("/session")
async def create_session(data: UserLogin, session: SessionDep, redis_client: RedisDep, response: Response):
    try:
        user = await authenticate_user(session, data.email, data.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message) from None

    access_token = create_access_token(user.id)
    refresh_token, jti = create_refresh_token(user.id)

    await save_refresh_token(redis_client, jti, user.id)

    response.set_cookie(key="access_token",
                        value=access_token,
                        max_age=int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()),
                        httponly=True,
                        secure=settings.COOKIE_SECURE,
                        samesite="lax",
                        path="/")
    response.set_cookie(key="refresh_token",
                        value=refresh_token,
                        max_age=int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()),
                        httponly=True,
                        secure=settings.COOKIE_SECURE,
                        samesite="lax",
                        path="/session")

    return {"message": "Login successful"}
