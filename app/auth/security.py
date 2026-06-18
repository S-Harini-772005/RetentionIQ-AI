from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database.session import get_db
from app.models.user import User
from app.auth.jwt_handler import decode_token

# Bcrypt for secure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against the hashed version.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generates a secure bcrypt hash from a password.
    """
    return pwd_context.hash(password)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to retrieve the current authenticated user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    email: Optional[str] = payload.get("sub")
    token_type: Optional[str] = payload.get("type")
    
    if email is None or token_type != "access":
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email, User.is_active == True, User.is_deleted == False).first()
    
    if user is None:
        raise credentials_exception
        
    return user