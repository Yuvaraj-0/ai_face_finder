from sqlalchemy import Column, String
from database.db import Base

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    token = Column(String(500), primary_key=True)