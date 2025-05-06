from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

class UserBase(BaseModel):
    name: str
    email: str

    class Config:
       from_attributes=True
       
class UserCreate(UserBase):
    password: str
    class Config:
       from_attributes=True

class UserSchema(UserBase):
    id: int
    created_at: datetime
    class Config:
       from_attributes=True

class GenerateUserToken(BaseModel):
    username: str
    password: str
    class Config:
       from_attributes=True

class GenerateOtp(BaseModel):
    email: str

class VerifyOtp(BaseModel):
    email: str
    otp: int