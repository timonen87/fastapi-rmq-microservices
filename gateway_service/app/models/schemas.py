from pydantic import BaseModel

class GenerateUserToken(BaseModel):
    username: str
    password: str

class UserCredentials(BaseModel):
    username: str
    password: str

class UserRegisteration(BaseModel):
    name: str
    email: str
    password: str

class GenerateOtp(BaseModel):
    email: str

class VerifyOtp(BaseModel):
    email: str
    otp: int 