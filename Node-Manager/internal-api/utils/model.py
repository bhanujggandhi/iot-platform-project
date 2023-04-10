import datetime
import time
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserSchema(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    role: str = Field(...)

    class Config:
        schema_extra = {"example": {"firstname": "John", "lastname": "Doe", "email": "joe@xyz.com", "password": "any"}}


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {"example": {"email": "joe@xyz.com", "password": "any"}}


class Task(BaseModel):
    name: str
    description: Optional[str]
    priority: int

    start_cond: str
    end_cond: str
    timeout: Optional[int]

    disabled: bool
    force_termination: bool
    force_run: bool

    status: str
    is_running: bool
    last_run: Optional[datetime.datetime]
    last_success: Optional[datetime.datetime]
    last_fail: Optional[datetime.datetime]
    last_terminate: Optional[datetime.datetime]
    last_inaction: Optional[datetime.datetime]
    last_crash: Optional[datetime.datetime]


class Log(BaseModel):
    timestamp: Optional[datetime.datetime] = Field(alias="created")
    task_name: str
    action: str
