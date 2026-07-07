from services.rate_limiter import RateLimiter
from fastapi import HTTPException

limiter = RateLimiter()

def rate_limit(request):
    ip = request.client.host

    if not limiter.check(ip):
        raise HTTPException(429, "Too many requests")