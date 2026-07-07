from fastapi import datastructures
from utils.password import hash_password, verify_password
from services.jwt_service import create_access_token, create_refresh_token
from models.user import User
from fastapi import HTTPException, status
import uuid
class AuthService:

    def register(self, db, data):
        print("PASSWORD TYPE:", type(data.password))
        print("PASSWORD VALUE:", repr(data.password))
        print("PASSWORD LEN:", len(str(data.password)))
        existing_user = (
            db.query(User)
            .filter(User.email == data.email)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = User(
            id=str(uuid.uuid4()),
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),

        )
        

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    def login(self, db, data):
        user = db.query(User).filter(User.email == data.email).first()

        if not user or not verify_password(data.password, user.password_hash):
            raise Exception("Invalid credentials")

        access = create_access_token({"user_id": user.id})
        refresh = create_refresh_token({"user_id": user.id})
        print("access_token", access, "refresh_token", refresh)
        return {
                "access_token": access,
                "refresh_token": refresh
            }