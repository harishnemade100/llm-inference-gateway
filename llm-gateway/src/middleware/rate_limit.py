import redis.asyncio as redis
import time
from fastapi import HTTPException
from dotenv import load_dotenv
import os

load_dotenv()


r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Configuration
BUCKET_MAX    = 100   # maximum tokens a bucket can hold
REFILL_RATE   = 10    # tokens added per minute
REQUEST_COST  = 1     # tokens each request costs


async def check_rate_limit(api_key: str):
    bucket_key = f"bucket:{api_key}"
    now = time.time()

    # Get current bucket state
    data = await r.hgetall(bucket_key)

    if data is not None:
        
        tokens = BUCKET_MAX
        last_refill = now

    else:
        tokens = float(data[b"tokens"])
        last_refill = float(data[b"last_refill"])

        # Refill tokens based on time passed
        elapsed_minutes       = (now - last_refill) / 60  # convert to minutes
        refill_amount =   elapsed_minutes * REFILL_RATE
        tokens = min(BUCKET_MAX, tokens + refill_amount)

    
    # Check if Enough tokens for the request
    if tokens < REQUEST_COST:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please wait before retrying.",
                "retry_after_seconds": round((REQUEST_COST - tokens) / (REFILL_RATE / 60))
            }
        )
    
    # Deduct tokens and update bucket state
    await r.hset(bucket_key, mapping={
        "tokens": tokens - REQUEST_COST,
        "last_refill": now
    })

async def get_bucket_status(api_key: str):
    bucket_key = f"bucket:{api_key}"
    data = await r.hgetall(bucket_key)

    if data is None:
        return {
            "tokens": BUCKET_MAX,
            "last_refill": time.time()
        }
    
    tokens = float(data[b"tokens"])
    last_refill = float(data[b"last_refill"])

    elapsed_minutes = (time.time() - last_refill) / 60
    tokens          = min(BUCKET_MAX, tokens + elapsed_minutes * REFILL_RATE)


    return {
        "tokens_remaining": round(tokens, 2),
        "bucket_max":       BUCKET_MAX,
        "refill_rate":      f"{REFILL_RATE} tokens/minute"
    }

async def reset_bucket(api_key: str):
    bucket_key = f"ratelimit:{api_key}"
    await r.delete(bucket_key)
    print(f"Bucket reset for {api_key}")
    

