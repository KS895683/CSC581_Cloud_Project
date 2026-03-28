from fastapi import FastAPI, Request
import time
import uuid

app = FastAPI(title="Backend Service")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "backend"}

@app.get("/api/data")
async def get_data():
    """Return sample data"""
    return {
        "message": "Hello from backend!",
        "timestamp": time.time(),
        "request_id": str(uuid.uuid4()),
        "items": [{"id": i, "value": f"item_{i}"} for i in range(5)]
    }

@app.post("/api/echo")
async def echo_data(request: Request):
    """Echo back received data"""
    data = await request.json()
    return {
        "echo": data,
        "received_at": time.time(),
        "processed_by": "backend"
    }