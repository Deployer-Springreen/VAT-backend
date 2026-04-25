import asyncio
import time
from functools import wraps
from typing import Callable, Any
from redis_db import redis_client

class CircuitBreakerOpenException(Exception):
    pass

def circuit_breaker(name: str, failure_threshold: int = 5, recovery_timeout: int = 30):
    """
    Custom Redis-based Circuit Breaker.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            state_key = f"cb:{name}:state" # "open", "closed", "half-open"
            failure_key = f"cb:{name}:failures"

            state = await redis_client.get(state_key) or "closed"

            if state == "open":
                raise CircuitBreakerOpenException(f"Circuit {name} is OPEN")

            try:
                # If half-open, allow one request
                # For simplicity in this custom implementation, we treat closed and half-open similarly for the call
                result = await func(*args, **kwargs)

                # Success: reset failures
                if state == "half-open":
                    await redis_client.set(state_key, "closed")
                    await redis_client.delete(failure_key)

                return result
            except Exception as e:
                # Failure logic
                failures = await redis_client.incr(failure_key)
                if failures >= failure_threshold:
                    await redis_client.setex(state_key, recovery_timeout, "open")

                raise e
        return wrapper
    return decorator
