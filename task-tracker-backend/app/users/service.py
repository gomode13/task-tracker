import logging

from argon2 import PasswordHasher
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.exceptions import EmailAlreadyTakenError
from app.users.models import User
from app.users.schemas import UserCreate

password_hasher = PasswordHasher()
logger = logging.getLogger(__name__)


async def create_user(session: AsyncSession, data: UserCreate) -> User:
    query = select(User).where(User.email == data.email)
    result = await session.execute(query)
    existing = result.scalar_one_or_none()

    if existing is not None:
        logger.warning("Registration failed, email taken: email=%s", data.email)
        raise EmailAlreadyTakenError()

    user = User(email=data.email, password_hash=password_hasher.hash(data.password))
    session.add(user)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        logger.warning("Registration race condition on duplicate email: email=%s", data.email)
        raise EmailAlreadyTakenError() from None

    await session.refresh(user)
    logger.info("User created: id=%s, email=%s", user.id, user.email)
    return user
