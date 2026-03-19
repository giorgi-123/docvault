from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from docvault.schemas.user import UserCreate, UserLogin, UserResponse, Token
from docvault.services.user import create_user, get_user_by_email
from docvault.services.auth import auth_service
from docvault.database import get_db

import logging

_logger = logging.getLogger(__name__)


# The prefix part in router adds `/auth` at the beginning of the all routes created using this `router(APIRouter)`
# So when we register new endpoints in code for example will be `/register` but in use it will be `/auth/register`
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", response_model=UserResponse)
async def register(data: UserCreate, session: AsyncSession=Depends(get_db)):
    get_user = await get_user_by_email(session, data.email)
    if get_user:
        raise HTTPException(status_code=400, detail="Email already registered!")
    user = await create_user(session, data)
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at
    )


@router.post("/login", response_model=Token)
async def login(data: UserLogin, session: AsyncSession=Depends(get_db)):
    user = await get_user_by_email(session, data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials!")
    valid_password = auth_service.verify_password(data.password, user.password_hash)
    if not valid_password:
        raise HTTPException(status_code=401, detail="Invalid credentials!")
    token = auth_service.create_access_token({"sub": data.email})
    token = Token(
        access_token=token,
    )
    return token

