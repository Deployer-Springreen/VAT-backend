from redis.asyncio import Redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
