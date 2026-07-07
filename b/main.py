from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database.db import get_db,engine,init_db
from fastapi.middleware.cors import CORSMiddleware
from routes.event_router import router as event_router
from sqlalchemy import text
from routes.photo import router as photo_router
import logging
from core.redis import redis_client
from core.qdrant import client
from routes.auth import router
from middleware.rate_limit_middleware import rate_limit


# from services.qdrant_service import QdrantService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("app")

app = FastAPI()




app.include_router(router)          # Auth routes
app.include_router(event_router)  
app.include_router(photo_router)    # Event routes

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def startup():
    init_db()
    print("Database connected successfully")
@app.get("/")
def home(db: Session = Depends(get_db)):
    return {"message": "DB connected successfully"}


# QdrantService.create_collection()
try:
    redis_client.ping()
    print("✅ Connected to Redis")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
@app.middleware("http")
async def middleware(request, call_next):

    rate_limit(request)

    response = await call_next(request)
    return response