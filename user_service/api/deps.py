from jose import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import email_validator as _email_check
from fastapi import Depends, HTTPException, Security
from fastapi.responses import JSONResponse
from models.user_model import User
from schemas.token_schema import Token
from schemas.user_schema import UserCreate, UserSchema
import fastapi.security as _security
from db.session import SessionLocal, get_db
from passlib.hash import bcrypt
from db.session import Base, SessionLocal, engine, settings
import random
from exceptions import UserNotFoundException

oauth2schema = _security.OAuth2PasswordBearer("/api/token")

async def get_user_by_email(email: str, db: Session):
     # Retrieve a user by email from the database
    return db.query(User).filter(User.email == email and User.is_verified==True).first()

async def create_user(user: UserCreate, db: Session):
    # Create a new user in the database
    try:
        valid = _email_check.validate_email(user.email)
        name = user.name
        email = valid.email
    except _email_check.EmailNotValidError:
        raise HTTPException(status_code=404, detail="Введите правилтный email")

    user_obj = User(email=email, name=name, hashed_password=bcrypt.hash(user.password))
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

async def authenticate_user(email: str, password: str, db: Session):
    # Authenticate a user
    user = await get_user_by_email(email=email, db=db)
    if not user or not user.is_verified:
        raise UserNotFoundException
    return user


async def create_token(user: User):
    # Create a JWT token for authentication
    user_obj = UserSchema.from_orm(user)
    user_dict = user_obj.model_dump()
    del user_dict["created_at"]
    token = jwt.encode(user_dict, settings.SECRET_KEY, algorithm="HS256")

    return Token(access_token=token, token_type="bearer")



# def create_access_token(user: User) -> str:
#     expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     return jwt.encode(
#         {"exp": expire, "user_id": str(user.id)},
#         key=settings.SECRET_KEY.get_secret_value(),
#         algorithm=ALGORITHM,
#     )


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2schema)):
     # Get the current authenticated user from the JWT token
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = db.query(User).get(payload["id"])
    except:
        raise HTTPException(status_code=401, detail="Неверный пароль или email")
    return UserSchema.from_orm(user)

def generate_otp():
    # Generate a random OTP
    return str(random.randint(100000, 999999))