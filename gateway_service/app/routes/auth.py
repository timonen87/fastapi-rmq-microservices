from fastapi import APIRouter, HTTPException
import requests
from app.models.schemas import UserCredentials, UserRegisteration, GenerateOtp, VerifyOtp
from app.config import USER_SERVICE_URL


router = APIRouter()


@router.post("/login")
async def login(user_data: UserCredentials):
    """
    Аутентификация пользователя по логину и паролю.
    
    Args:
        user_data (UserCredentials): Объект с полями `username`(email) и `password`.
    
    Returns:
        dict: Токены доступа (access_token, refresh_token) в случае успеха.
    
    Raises:
        HTTPException: 
            - 401: Неверные учетные данные.
            - 503: Сервис аутентификации недоступен.
    """
    try:
        # Отправляем запрос к сервису аутентификации
        response = requests.post(
            f"{USER_SERVICE_URL}/api/token",
            json={"username": user_data.username, "password": user_data.password}
        )
        if response.status_code == 200:
            return response.json()  # Возвращаем токены
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()  # Прокидываем ошибку от сервиса
            )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Служба аутентификации недоступна"
        )

@router.post("/register")
async def registeration(user_data: UserRegisteration):
    """
    Регистрация нового пользователя.
    
    Args:
        user_data (UserRegisteration): Объект с полями `name`, `email`, `password`.
    
    Returns:
        dict: Данные созданного пользователя.
    
    Raises:
        HTTPException:
            - 400: Некорректные данные (например, email уже занят).
            - 503: Сервис аутентификации недоступен.
    """
    try:
        response = requests.post(
            f"{USER_SERVICE_URL}/api/users",
            json={"name": user_data.name, "email": user_data.email, "password": user_data.password}
        )
        if response.status_code == 200:
            return response.json()  # Возвращаем данные пользователя
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Служба аутентификации недоступна"
        )

@router.post("/generate_otp")
async def generate_otp(user_data: GenerateOtp):
    """
    Генерация OTP (одноразового пароля) для пользователя.
    
    Args:
        user_data (GenerateOtp): Объект с полем `email`.
    
    Returns:
        dict: Статус отправки OTP (например, {"status": "success"}).
    
    Raises:
        HTTPException:
            - 404: Пользователь с таким email не найден.
            - 503: Сервис аутентификации недоступен.
    """
    try:
        response = requests.post(
            f"{USER_SERVICE_URL}/api/users/generate_otp",
            json={"email": user_data.email}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Служба аутентификации недоступна"
        )

@router.post("/verify_otp")
async def verify_otp(user_data: VerifyOtp):
    """
    Проверка OTP (одноразового пароля).
    
    Args:
        user_data (VerifyOtp): Объект с полями `email` и `otp`.
    
    Returns:
        dict: Результат проверки (например, {"verified": true}).
    
    Raises:
        HTTPException:
            - 400: Неверный OTP.
            - 503: Сервис аутентификации недоступен.
    """
    try:
        response = requests.post(
            f"{USER_SERVICE_URL}/api/users/verify_otp",
            json={"email": user_data.email, "otp": user_data.otp}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Служба аутентификации недоступна"
        )