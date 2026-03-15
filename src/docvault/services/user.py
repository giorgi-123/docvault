from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from docvault.models.user import User
from docvault.schemas.user import UserCreate
from docvault.services.auth import auth_service

async def create_user(session: AsyncSession, user_create_record: UserCreate) -> User:
    """Save new user to DB"""
    password_hash = auth_service.hash_password(user_create_record.password)
    user = User(email=user_create_record.email, 
                password_hash=password_hash,
                full_name=user_create_record.full_name)
    session.add(user)
    await session.flush()
    return user

async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Find user by email"""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

