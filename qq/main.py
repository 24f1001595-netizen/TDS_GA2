import time
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title="Descriptive Statistics Service")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ALLOWED_ORIGIN = "https://dash-i2p2d9.example.com"
EMAIL = "24f1001595@ds.study.iitm.ac.in"  # <-- Replace with your logged-in email address


# ---------------------------------------------------------------------------
# Middleware: X-Request-ID & X-Process-Time
# ---------------------------------------------------------------------------
class CustomHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time

        response.headers["X-Request-ID"] = req_id
        response.headers["X-Process-Time"] = f"{process_time:.6f}"

        return response


# Add the header middleware first
app.add_middleware(CustomHeaderMiddleware)

# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------
# FastAPI's built-in CORSMiddleware strictly validates against allow_origins.
# Requests/preflights matching ALLOWED_ORIGIN receive the ACAO header.
# Any other origin receives NO Access-Control-Allow-Origin header.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/stats")
async def get_stats(values: str = Query(..., description="Comma-separated integers")):
    if not values.strip():
        raise HTTPException(
            status_code=400, detail="Empty 'values' parameter provided."
        )

    try:
        nums = [int(v.strip()) for v in values.split(",") if v.strip()]
    except ValueError:
        raise HTTPException(
            status_code=400, detail="All values must be valid integers."
        )

    if not nums:
        raise HTTPException(status_code=400, detail="No valid integers found.")

    count = len(nums)
    total_sum = sum(nums)
    min_val = min(nums)
    max_val = max(nums)
    mean_val = round(total_sum / count, 4)

    return {
        "email": EMAIL,
        "count": count,
        "sum": total_sum,
        "min": min_val,
        "max": max_val,
        "mean": mean_val,
    }


@app.get("/")
async def root():
    return {"status": "healthy"}
