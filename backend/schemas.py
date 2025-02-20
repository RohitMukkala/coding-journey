from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    leetcode_username: Optional[str] = None
    github_username: Optional[str] = None
    codechef_username: Optional[str] = None
    codeforces_username: Optional[str] = None
    profile_picture: Optional[str] = None

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    profile_picture: Optional[str] = None
    leetcode_username: Optional[str] = None
    github_username: Optional[str] = None
    codechef_username: Optional[str] = None
    codeforces_username: Optional[str] = None

    class Config:
        from_attributes = True 