import logging
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status

from app.dependencies import SessionDep
from app.users.models import User
from app.users.security import decode_token
from app.users.service import get_user_by_id

logger = logging.getLogger(__name__)


async def get_current_user(request: Request, session: SessionDep) -> User:
    access_token = request.cookies.get("access_token")

    if access_token is None:
        logger.warning("Authentication failed, access token cookie is missing")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        payload = decode_token(access_token)
    except jwt.InvalidTokenError:
        logger.warning("Authentication failed, invalid or expired access token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None

    if payload.get("type") != "access":
        logger.warning("Authentication failed, wrong token type: type=%s", payload.get("type"))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user_id = payload.get("sub")

    if user_id is None:
        logger.warning("Authentication failed, token has no subject")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user_id = int(user_id)
    user = await get_user_by_id(session, user_id)

    if user is None:
        logger.warning("Authentication failed, user not found: id=%s", user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
