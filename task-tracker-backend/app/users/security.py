import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


def create_access_token(user_id: int) -> str:
    token_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "jti": token_id,
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def create_refresh_token(user_id: int) -> tuple[str, str]:
    token_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "jti": token_id,
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, token_id


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
