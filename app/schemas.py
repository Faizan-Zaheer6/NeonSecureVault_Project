from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_admin: bool = False 

class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

# --- Document Schemas ---
class Document(BaseModel):
    id: int
    filename: str
    version: int
    owner_id: int
    
    class Config:
        from_attributes = True

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None