from datetime import timedelta

from fastapi import Response

from app.config import settings


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
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
