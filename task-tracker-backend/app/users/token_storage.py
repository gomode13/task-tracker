from datetime import timedelta

from redis.asyncio import Redis

from app.config import settings

REFRESH_TOKEN_PREFIX = "refresh:"
REFRESH_TOKEN_TTL_SECONDS = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())


async def save_refresh_token(redis_client: Redis, jti: str, user_id: int) -> None:
    await redis_client.setex(f"{REFRESH_TOKEN_PREFIX}{jti}", REFRESH_TOKEN_TTL_SECONDS, str(user_id))


async def get_refresh_token_owner(redis_client: Redis, jti: str) -> str | None:
    return await redis_client.get(f"{REFRESH_TOKEN_PREFIX}{jti}")


async def delete_refresh_token(redis_client: Redis, jti: str) -> None:
    await redis_client.delete(f"{REFRESH_TOKEN_PREFIX}{jti}")


async def rotate_refresh_token(redis_client: Redis, jti: str, new_jti: str, user_id: int) -> None:
    async with redis_client.pipeline(transaction=True) as pipe:
        pipe.delete(f"{REFRESH_TOKEN_PREFIX}{jti}")
        pipe.setex(f"{REFRESH_TOKEN_PREFIX}{new_jti}", REFRESH_TOKEN_TTL_SECONDS, str(user_id))
        await pipe.execute()
