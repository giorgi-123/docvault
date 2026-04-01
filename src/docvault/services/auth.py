from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from docvault.config import settings
from docvault.models.user import User
from docvault.database import get_db

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
bearer_scheme = HTTPBearer()

async def get_current_user(
        # token: str = Depends(oauth2_scheme),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        from docvault.services.user import get_user_by_email
        user = await get_user_by_email(session=session, email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

class Auth:
    def __init__(self):
        self.pwd_hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        return self.pwd_hasher.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            self.pwd_hasher.verify(hashed_password, plain_password)
            return True
        except VerifyMismatchError:
            return False

    def create_access_token(self, data: dict) -> str:
        expiration_date = datetime.now() + timedelta(minutes=settings.access_token_expire_minutes)
        return jwt.encode({**data, "exp": expiration_date}, settings.secret_key, algorithm=settings.algorithm)


auth_service = Auth()