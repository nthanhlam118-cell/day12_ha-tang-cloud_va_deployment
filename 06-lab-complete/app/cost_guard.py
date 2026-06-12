import redis
from datetime import datetime
from fastapi import HTTPException, status
from .config import settings

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def check_budget(user_id: str, estimated_cost: float = 0.05):
    """
    Check if the user is within their monthly budget.
    """
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    current = float(r.get(key) or 0)
    if current + estimated_cost > settings.MONTHLY_BUDGET_USD:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Monthly budget exceeded"
        )
    
    r.incrbyfloat(key, estimated_cost)
    r.expire(key, 32 * 24 * 3600)  # 32 days
    return True
