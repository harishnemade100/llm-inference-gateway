from src.middleware.rate_limit import get_bucket_status
from fastapi import FastAPI, Request
from src.middleware.auth import check_auth

app = FastAPI()

@app.get("/v1/rate-limit/status")
async def rate_limit_status(request: Request):
    api_key = request.headers.get("Authorization", "").replace("Bearer ", "")
    await check_auth(api_key)
    return await get_bucket_status(api_key)