from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: str = Field("Analyst", pattern="^(Admin|Analyst|Executive)$")

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str]
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None

class ErrorResponse(BaseModel):
    detail: str