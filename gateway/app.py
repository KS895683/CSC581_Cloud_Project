from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import time
from collections import defaultdict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Gateway")

# In-memory rate limiting (sliding window)
request_counts = defaultdict(list)
RATE_LIMIT = 10  # requests per minute
TIME_WINDOW = 60  # seconds

BACKEND_URL = "http://backend:8001"

def check_rate_limit(ip: str) -> bool:
    """Check if IP has exceeded rate limit"""
    now = time.time()
    # Keep only requests from last TIME_WINDOW seconds
    request_counts[ip] = [t for t in request_counts[ip] if now - t < TIME_WINDOW]
    
    if len(request_counts[ip]) >= RATE_LIMIT:
        return False
    
    request_counts[ip].append(now)
    return True

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "gateway"}

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway_proxy(request: Request, path: str):
    client_ip = request.client.host
    request_path = f"/api/{path}"
    
    # 1. Rate limiting
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "limit": f"{RATE_LIMIT} requests per minute"}
        )
    
    # 2. Forward to backend
    logger.info(f"Forwarding {request.method} {request_path} to backend")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        backend_url = f"{BACKEND_URL}{request_path}"
        
        # Forward request to backend
        response = await client.request(
            method=request.method,
            url=backend_url,
            headers=dict(request.headers),
            content=await request.body() if request.method in ["POST", "PUT"] else None,
            params=request.query_params
        )
    
    # 3. Return response with gateway headers
    return JSONResponse(
        content=response.json() if response.headers.get("content-type") == "application/json" else {"raw": response.text},
        status_code=response.status_code,
        headers={
            "X-Gateway": "processed",
            "X-RateLimit-Checked": "true"
        }
    )