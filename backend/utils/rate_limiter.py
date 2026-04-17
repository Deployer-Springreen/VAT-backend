import time
from fastapi import Request, HTTPException
from redis.asyncio import Redis
import os

# Assuming Redis is available at REDIS_URL environment variable
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

class RateLimiter:
    def __init__(self, requests_limit: int, window_seconds: int):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds

    async def __call__(self, request: Request):
        # Use client IP or user_id as identifier
        # In a real app, you might want to use current_user_id if available
        identifier = request.client.host
        key = f"rate_limit:{identifier}:{request.scope['path']}"

        try:
            current = await redis_client.get(key)
        except Exception as e:
            # Fallback if redis is not available - allow request but log error
            print(f"Redis error: {e}")
            return

        if current and int(current) >= self.requests_limit:
            raise HTTPException(status_code=429, detail="Too many requests")

        async with redis_client.pipeline(transaction=True) as pipe:
            await pipe.incr(key)
            await pipe.expire(key, self.window_seconds)
            await pipe.execute()

def rate_limit(requests: int, window: int):
    return RateLimiter(requests, window)
