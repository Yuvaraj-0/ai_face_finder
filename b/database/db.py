import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.db import settings


engine = None
SessionLocal = None
Base = declarative_base()

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
# Create engine



def init_db():
    global engine, SessionLocal
    from models.user import User
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()