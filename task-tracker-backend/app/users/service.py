import logging

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.exceptions import EmailAlreadyTakenError, InvalidCredentialsError
from app.users.models import User
from app.users.schemas import UserCreate

password_hasher = PasswordHasher()
logger = logging.getLogger(__name__)


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def create_user(session: AsyncSession, data: UserCreate) -> User:
    existing = await get_user_by_email(session, data.email)

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


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(session, email)

    if user is None:
        logger.warning("Authentication failed, email address not found: email=%s", email)
        raise InvalidCredentialsError()

    try:
        password_hasher.verify(user.password_hash, password)
    except VerificationError:
        logger.warning("Authentication failed, password does not match: email=%s", email)
        raise InvalidCredentialsError() from None

    return user
