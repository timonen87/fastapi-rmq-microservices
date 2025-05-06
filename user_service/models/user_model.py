import datetime as _dt
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from passlib.hash import bcrypt
from db.session import Base, engine
# from db.session import Base as DB_Base


Base.metadata.create_all(engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    is_verified = Column(Boolean , default=False)
    otp = Column(Integer)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=_dt.datetime.utcnow)

    def verify_password(self, password: str):
        return bcrypt.verify(password, self.hashed_password)