import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from pydantic import ValidationError

# Environment variables with strict defaults for production
SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "7b9d566e13881473950f24e9b980e15926615b9432e185e4d29f0f1d1983084a")
REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY", "2f8a14b5d6f1a8c9e0d1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a secure JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a secure JWT refresh token with a longer lifespan.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str, is_refresh: bool = False) -> Dict[str, Any]:
    """
    Decodes and validates a JWT token.
    """
    try:
        key = REFRESH_SECRET_KEY if is_refresh else SECRET_KEY
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return {}