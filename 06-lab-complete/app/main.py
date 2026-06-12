import sys
import json
import time
import signal
import asyncio
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
import redis
import logging

from .config import settings
from .auth import verify_api_key
from .rate_limiter import check_rate_limit
from .cost_guard import check_budget

import importlib.util
import os

# Configure structured JSON logging
class JSONLogFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "event": record.getMessage(),
            "name": record.name
        }
        return json.dumps(log_obj)

logger = logging.getLogger("agent")
logger.setLevel(settings.LOG_LEVEL)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONLogFormatter())
logger.addHandler(handler)

# Load mock_llm from utils
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "utils", "mock_llm.py"))
spec = importlib.util.spec_from_file_location("mock_llm", utils_path)
mock_llm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mock_llm)

app = FastAPI(title="Production AI Agent")
r = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Graceful shutdown state
is_shutting_down = False

def shutdown_handler(signum, frame):
    global is_shutting_down
    logger.info("Received SIGTERM, initiating graceful shutdown...")
    is_shutting_down = True

signal.signal(signal.SIGTERM, shutdown_handler)

@app.middleware("http")
async def shutdown_middleware(request: Request, call_next):
    if is_shutting_down and request.url.path not in ["/health", "/ready"]:
        return JSONResponse(status_code=503, content={"detail": "Service is shutting down"})
    response = await call_next(request)
    return response

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    try:
        r.ping()
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(status_code=503, content={"status": "not ready"})

@app.post("/ask")
def ask(
    question: str,
    user_id: str = Depends(verify_api_key)
):
    # Enforce Rate Limiting and Cost Guard
    check_rate_limit(user_id)
    check_budget(user_id, estimated_cost=0.05)
    
    # Stateless conversation history from Redis
    history_key = f"history:{user_id}"
    history = r.lrange(history_key, 0, -1)
    
    logger.info(f"Processing question from user_id: {user_id}")
    
    # Call Mock LLM
    response = mock_llm.ask(question)
    
    # Save state back to Redis
    r.rpush(history_key, f"Q: {question}")
    r.rpush(history_key, f"A: {response}")
    # Keep only last 20 messages (10 Q&A pairs)
    r.ltrim(history_key, -20, -1)
    
    return {
        "user_id": user_id,
        "question": question,
        "answer": response
    }
