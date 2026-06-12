import time
import redis
from fastapi import HTTPException, status
from .config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def check_rate_limit(user_id: str):
    key = f"rate_limit:{user_id}"
    current_time = int(time.time())
    window_start = current_time - 60

    # Remove requests older than 1 minute
    r.zremrangebyscore(key, 0, window_start)
    
    # Count current requests
    request_count = r.zcard(key)
    
    if request_count >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    # Add current request
    r.zadd(key, {str(current_time): current_time})
    r.expire(key, 60)
    
    return True
