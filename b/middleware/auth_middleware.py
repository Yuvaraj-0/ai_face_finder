from services.jwt_service import decode_token
from fastapi import HTTPException

def auth_middleware(request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(401)

    try:
        return decode_token(token)
    except:
        raise HTTPException(401)