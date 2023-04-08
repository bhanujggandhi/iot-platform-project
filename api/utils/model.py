from pydantic import BaseModel, Field, EmailStr


class UserSchema(BaseModel):
    firstname: str = Field(...)
    lastname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {"example": {"firstname": "John", "lastname": "Doe", "email": "joe@xyz.com", "password": "any"}}


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {"example": {"email": "joe@xyz.com", "password": "any"}}
