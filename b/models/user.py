from sqlalchemy import Column, String, DateTime
from datetime import datetime
from database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    name = Column(String(100))
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(String(20), default="USER")
    created_at = Column(DateTime, default=datetime.utcnow)