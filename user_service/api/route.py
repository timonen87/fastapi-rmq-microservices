
from fastapi import APIRouter, Depends, HTTPException, Response

from schemas.user_schema import UserCreate, GenerateUserToken, UserSchema, GenerateOtp, VerifyOtp
from sqlalchemy.orm import Session
from models.user_model import User
from sqlalchemy import select

from db.session import SessionLocal, get_db
import deps as _deps
import service as _service
import logging




router_users = APIRouter(
    tags=["User Auth"],
)



@router_users.post("/api/users" ,  tags = ['User Auth'])
async def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db)):
    db_user = await _deps.get_user_by_email(email=user.email, db=db)

    if db_user:
        logging.info('Пользователь с таким адресом электронной почты уже существует')
        raise HTTPException(
            status_code=200,
            detail="Пользователь с таким адресом электронной почты уже существует")
    

    user = await _deps.create_user(user=user, db=db)

    return HTTPException(
            status_code=201,
            detail="Зарегистрированный пользователь, пожалуйста, подтвердите адрес электронной почты для активации учетной записи !")



@router_users.post("/api/token" ,tags = ['User Auth'])
async def generate_token(
    #form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(), 
    user_data: GenerateUserToken,
    db: Session = Depends(get_db)):
    user = await _deps.authenticate_user(email=user_data.username, password=user_data.password, db=db)

    if not user.is_verified :
        logging.info('Проверка электронной почты еще не завершена. Пожалуйста, подтвердите свой адрес электронной почты, чтобы продолжить. ')
        raise HTTPException(
            status_code=403, detail="Проверка электронной почты еще не завершена. Пожалуйста, подтвердите свой адрес электронной почты, чтобы продолжить.")

    if not user:
        logging.info('Invalid Credentials')
        raise HTTPException(
            status_code=401, detail="Invalid Credentials")
    
    logging.info('JWT Token Generated')
    return await _deps.create_token(user=user)


@router_users.get("/api/users/me", response_model=UserSchema, tags = ['User Auth'])
async def get_user(user: UserSchema = Depends(_deps.get_current_user)):
    return user


@router_users.get("/api/users/profile", tags=['User Auth'])
async def get_user(email: str, db: Session = Depends(_deps.get_db)) -> UserSchema:
    query = select(User).filter_by(email=email)
    result = db.execute(query)
    return result.scalar_one_or_none()
  

@router_users.post("/api/users/generate_otp", response_model=str, tags=["User Auth"])
async def send_otp_mail(userdata: GenerateOtp, db: Session = Depends(_deps.get_db)):
    user = await _deps.get_user_by_email(email=userdata.email, db=db)

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Пользователь уже верифицирован")

    # Generate and send OTP
    otp = _deps.generate_otp()
    print(otp)
    _service.send_otp(userdata.email, otp, _service.channel)

    # Store the OTP in the database
    user.otp = otp
    db.add(user)
    db.commit()

    return "Код подтверждения отправлен на почту"


@router_users.post("/api/users/verify_otp", tags=["User Auth"])
async def verify_otp(userdata: VerifyOtp, db: Session = Depends(_deps.get_db)):
    user = await _deps.get_user_by_email(email=userdata.email, db=db )

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if not user.otp or user.otp != userdata.otp:
        raise HTTPException(status_code=400, detail="Не верный OTP код")

    # Update user's is_verified field
    user.is_verified = True
    user.otp = None  # Clear the OTP
    db.add(user)
    db.commit()

    return "Электронная почта успешно подтверждена"