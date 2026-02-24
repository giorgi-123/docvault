from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from docvault.schemas.user import UserCreate, UserLogin, UserResponse, Token
from docvault.services.user import create_user, get_user_by_email
from docvault.database import get_db

# The prefix part in router adds `/auth` at the beginning of the all routes created using this `router(APIRouter)`
# So when we register new endpoints in code for example will be `/register` but in use it will be `/auth/register`
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", response_model=UserResponse)
async def register(data: UserCreate, session: AsyncSession = Depends(get_db)):
    pass


@router.post("/login", response_model=Token)
async def login(data: UserLogin):
    pass
