from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal


# ---------- CREATE ----------
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str

    @field_validator("role")
    def normalize_role(cls, v):
        return v.upper()


# ---------- RESPONSE ----------
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str   # <<< agregado

    class Config:
        orm_mode = True  


# ---------- LOGIN ----------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- TOKEN (LOGIN OUTPUT) ----------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    id: int           # <<< agregado
    username: str 
    email: str
    role: str         # <<< agregado
