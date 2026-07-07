from fastapi import Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session

from database.db import get_db
from models.user import User
from services.jwt_service import decode_token


def get_current_photographer(
    request: Request,
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    print("\n========== AUTH DEBUG ==========")

    print("Authorization Header:", authorization)
    print("Cookie access_token:", request.cookies.get("access_token"))

    token = None

    # Prefer Authorization header
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        print("Using Authorization Header")

    elif request.cookies.get("access_token"):
        token = request.cookies.get("access_token")
        print("Using Cookie")

    print("Extracted Token:", token)

    if not token:
        print("ERROR: No token found")
        raise HTTPException(
            status_code=401,
            detail="Token missing"
        )

    try:
        payload = decode_token(token)
        print("Decoded Payload:", payload)

    except Exception as e:
        print("JWT Decode Error:", repr(e))
        raise

    try:
        user = (
            db.query(User)
            .filter(User.id == payload["user_id"])
            .first()
        )

        print("Database User:", user)

    except Exception as e:
        print("Database Error:", repr(e))
        raise

    if user is None:
        print("ERROR: User not found")
        raise HTTPException(
            status_code=401,
            detail="Invalid user"
        )

    print("User ID:", user.id)
    print("User Role:", user.role)

    if user.role != "photographer":
        print("ERROR: User is not a photographer")
        raise HTTPException(
            status_code=403,
            detail="Only photographers can access this resource"
        )

    print("Authentication Successful")
    print("===============================\n")

    return user