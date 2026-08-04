import logging

import jwt
from fastapi import APIRouter, HTTPException, Request, Response, status

from app.users.cookies import set_auth_cookies
from app.users.dependencies import CurrentUserDep, RedisDep, SessionDep
from app.users.exceptions import EmailAlreadyTakenError, InvalidCredentialsError
from app.users.schemas import UserCreate, UserLogin, UserRead
from app.users.security import create_access_token, create_refresh_token, decode_token
from app.users.service import authenticate_user, create_user
from app.users.token_storage import get_refresh_token_owner, rotate_refresh_token, \
    save_refresh_token

router = APIRouter(tags=["users"])
logger = logging.getLogger(__name__)


@router.post("/user", response_model=UserRead)
async def register(data: UserCreate, session: SessionDep):
    try:
        user = await create_user(session, data)
    except EmailAlreadyTakenError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from None

    return user


@router.get("/user", response_model=UserRead)
async def read_current_user(user: CurrentUserDep):
    return user


@router.post("/session")
async def create_session(data: UserLogin, session: SessionDep, redis_client: RedisDep, response: Response):
    try:
        user = await authenticate_user(session, data.email, data.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message) from None

    access_token = create_access_token(user.id)
    refresh_token, jti = create_refresh_token(user.id)

    await save_refresh_token(redis_client, jti, user.id)

    set_auth_cookies(response, access_token, refresh_token)

    return {"message": "Login successful"}


@router.put("/session")
async def refresh_session(request: Request, redis_client: RedisDep, response: Response):
    cookie = request.cookies.get("refresh_token")

    if cookie is None:
        logger.warning("Session refresh failed, refresh token cookie is missing")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        payload = decode_token(cookie)
    except jwt.InvalidTokenError:
        logger.warning("Session refresh failed, invalid or expired refresh token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None

    if payload.get("type") != "refresh":
        logger.warning("Session refresh failed, wrong token type: type=%s", payload.get("type"))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    jti = payload.get("jti")

    if jti is None:
        logger.warning("Session refresh failed, token has no jti")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user_id = await get_refresh_token_owner(redis_client, jti)

    if user_id is None:
        logger.warning("Session refresh failed, refresh token not found in storage")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user_id = int(user_id)
    access_token = create_access_token(user_id)
    refresh_token, new_jti = create_refresh_token(user_id)

    await rotate_refresh_token(redis_client, jti, new_jti, user_id)

    set_auth_cookies(response, access_token, refresh_token)

    return {"message": "Session refreshed"}
