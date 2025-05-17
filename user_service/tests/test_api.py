import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db.session import Base, get_db
from models.user_model import User

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def test_user_data():
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def test_user(test_user_data):
    db = TestingSessionLocal()
    user = User(
        name=test_user_data["name"],
        email=test_user_data["email"],
        hashed_password=test_user_data["password"],
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

def test_create_user(test_user_data):
    response = client.post("/api/users", json=test_user_data)
    assert response.status_code == 201
    assert "Зарегистрированный пользователь" in response.json()["detail"]

def test_create_user_duplicate_email(test_user):
    response = client.post("/api/users", json={
        "name": "Another User",
        "email": test_user.email,
        "password": "password123"
    })
    assert response.status_code == 200
    assert "Пользователь с таким адресом электронной почты уже существует" in response.json()["detail"]

def test_generate_token(test_user_data):
    response = client.post("/api/token", json={
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_generate_token_invalid_credentials():
    response = client.post("/api/token", json={
        "username": "wrong@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Invalid Credentials" in response.json()["detail"]

def test_get_current_user(test_user, test_user_data):
    # First get token
    token_response = client.post("/api/token", json={
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    })
    token = token_response.json()["access_token"]
    
    # Test getting current user
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == test_user_data["email"]
    assert response.json()["name"] == test_user_data["name"]

def test_get_user_profile(test_user):
    response = client.get(f"/api/users/profile?email={test_user.email}")
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email
    assert response.json()["name"] == test_user.name

def test_generate_otp(test_user):
    response = client.post("/api/users/generate_otp", json={
        "email": test_user.email
    })
    assert response.status_code == 200
    assert "Код подтверждения отправлен на почту" in response.json()

def test_verify_otp(test_user):
    # First generate OTP
    client.post("/api/users/generate_otp", json={
        "email": test_user.email
    })
    
    # Get the OTP from the database
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == test_user.email).first()
    otp = user.otp
    db.close()
    
    # Verify OTP
    response = client.post("/api/users/verify_otp", json={
        "email": test_user.email,
        "otp": otp
    })
    assert response.status_code == 200
    assert "Электронная почта успешно подтверждена" in response.json() 