
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from passlib.hash import bcrypt
from db.session import Base, engine



Base.metadata.create_all(engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    is_verified = Column(Boolean , default=False)
    otp = Column(Integer)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    def verify_password(self, password: str):
        return bcrypt.verify(password, self.hashed_password)