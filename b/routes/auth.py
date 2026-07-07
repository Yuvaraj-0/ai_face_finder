from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
import logging

from database.db import get_db
from schemas.auth import LoginSchema
from services.auth_service import AuthService
from services.blacklist_service import BlacklistService
from middleware.auth_middleware import auth_middleware
from schemas.auth import RegisterSchema
router = APIRouter()
auth = AuthService()
blacklist = BlacklistService()
logger = logging.getLogger(__name__)
@router.post("/login")
def login(data: LoginSchema, response: Response, db=Depends(get_db)):

    access, refresh = auth.login(db, data)
 
    response.set_cookie("access_token", access, httponly=True)
    response.set_cookie("refresh_token", refresh, httponly=True)

    return {
  "message": "login success",
  "access_token": access,
  "refresh_token": refresh
}


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    try:
        # Log incoming request (never log passwords)
        logger.info(
            "Register request received: name=%s, email=%s",
            data.name,
            data.email,
        )

        user = auth.register(db, data)

        logger.info(
            "User registered successfully. user_id=%s email=%s",
            user.id,
            user.email,
        )
        return {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            },
        }

    except HTTPException:
        # Re-raise HTTP exceptions from the service
        raise

    except Exception as e:
        logger.exception("Registration failed")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/refresh")
def refresh(request: Request, db=Depends(get_db)):

    token = request.cookies.get("refresh_token")

    if blacklist.is_blacklisted(db, token):
        return {"error": "invalid refresh token"}

    new_access = auth.refresh(db, token)

    return {"access_token": new_access}


@router.post("/logout")
def logout(request: Request, db=Depends(get_db)):

    token = request.cookies.get("refresh_token")

    auth.logout(db, token, blacklist)

    return {"message": "logged out"}


@router.get("/me")
def me(user=Depends(auth_middleware)):
    return user