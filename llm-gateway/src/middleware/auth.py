import redis.asyncio as redis
import hashlib
from fastapi import HTTPException
from dotenv import load_dotenv
import os


load_dotenv()

r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

def hash_key(api_key: str)-> str:
    return hashlib.sha256(api_key.encode()).hexdigest()

async def check_auth(api_key:str):
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="No API key provided"
        )
    
    hashed = hash_key(api_key)
    exists = await r.exists(f"apikey:{hashed}")
    if not exists:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

async def create_api_key(key: str, owner: str):
    hashed = hash_key(key)
    await r.hset(f"apikey:{hashed}", mapping={
        "owner": owner,
        "active": "1",
        "created_at": str(__import__("time").time())
    })
    print(f"Created key for {owner} → hash: {hashed[:12]}...")

async def revoke_api_key(api_key: str):
    hashed = hash_key(api_key)
    await r.delete(f"apikey:{hashed}")
    print(f"Revoked key → hash: {hashed[:12]}...")

