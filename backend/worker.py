import asyncio
from arq import create_pool
from arq.connections import RedisSettings
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

async def send_otp_email(ctx, email: str, otp: str):
    # Simulate heavy email sending operation
    print(f"DEBUG [Worker]: Sending OTP {otp} to {email}...")
    await asyncio.sleep(2) # Simulate latency
    print(f"DEBUG [Worker]: OTP sent to {email}")

class WorkerSettings:
    functions = [send_otp_email]
    redis_settings = RedisSettings(host=REDIS_HOST, port=REDIS_PORT)
