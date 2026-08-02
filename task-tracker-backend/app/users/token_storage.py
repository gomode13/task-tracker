from datetime import timedelta

from redis.asyncio import Redis

from app.config import settings

REFRESH_TOKEN_PREFIX = "refresh:"


async def save_refresh_token(redis_client: Redis, jti: str, user_id: int) -> None:
    ttl_seconds = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
    await redis_client.setex(f"{REFRESH_TOKEN_PREFIX}{jti}", ttl_seconds, str(user_id))


async def get_refresh_token_owner(redis_client: Redis, jti: str) -> str | None:
    return await redis_client.get(f"{REFRESH_TOKEN_PREFIX}{jti}")


async def delete_refresh_token(redis_client: Redis, jti: str) -> None:
    await redis_client.delete(f"{REFRESH_TOKEN_PREFIX}{jti}")
