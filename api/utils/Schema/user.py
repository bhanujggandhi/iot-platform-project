from enum import Enum
from pydantic import BaseModel, EmailStr


class Role(str, Enum):
    developer = "developer"
    admin = "admin"
    platform = "platform"


class User(BaseModel):
    name: str
    email: EmailStr
    role: Role
    password: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True
