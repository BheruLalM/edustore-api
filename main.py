import os
import time
<<<<<<< HEAD
=======
import sys
>>>>>>> 5cfc842 (new version of it)
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import traceback
import logging

<<<<<<< HEAD
=======
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

>>>>>>> 5cfc842 (new version of it)
from api.api_router import api_router
from core.exceptions import (
    DomainError,
    UserNotFound,
    CannotFollowYourself,
    NotFollowing,
    OTPCooldownActive,
    DocumentNotFound,
    DocumentAccessDenied,
    DownloadUrlGenerationFailed,
    DocumentOwnershipError,
    InvalidAvatarContentType,
    InvalidAvatarKey,
    AvatarUploadExpired,
    AvatarNotFound,
    ERROR_STATUS_MAP,
)

app = FastAPI(title="EduStore", description="Here you have all friends together")

# Router Inclusion
app.include_router(api_router)

# ------------------------------------------------------------------
# MIDDLEWARE STACK (Added in reverse order of execution)
# ------------------------------------------------------------------

# 3. Global Exception Handler (Outer middle layer)
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logging.error(f"Unhandled exception during {request.method} {request.url.path}: {exc}")
        logging.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal Server Error",
                "error_code": "unhandled_exception",
                "message": str(exc)
            }
        )

# 2. Add GZip compression for responses > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=6)

# 1. CORS Middleware (Outermost - ensures headers on ALL responses)
<<<<<<< HEAD
origins = [
    "https://edustore-omega.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
=======
from core.config import app_settings

if app_settings.is_production:
    # Production: Only allow production frontend
    origins = [
        app_settings.FRONTEND_URL,
        "https://edustore-omega.vercel.app",
        "https://*.vercel.app",  # Allow Vercel preview deployments
    ]
else:
    # Development: Allow localhost
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # For testing
    ]
>>>>>>> 5cfc842 (new version of it)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 0. Request timing middleware for performance monitoring
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        
        # Log slow requests (> 500ms)
        if process_time > 0.5:
            print(f"⏱️  Slow request: {request.method} {request.url.path} - {process_time:.3f}s")
        
        return response

app.add_middleware(TimingMiddleware)

# Outermost middleware is TimingMiddleware (added last)

@app.exception_handler(DomainError)
async def domain_exception_handler(request: Request, exc: DomainError):
    status_code = ERROR_STATUS_MAP.get(type(exc), 400)
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": str(exc),
            "error_code": getattr(exc, "error_code", "unknown_error"),
        },
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": "rate_limit_exceeded" if exc.status_code == 429 else "error",
        },
    )

@app.get("/")
async def home(request: Request):
    return {"message": "Hello! You are within the rate limit."}
<<<<<<< HEAD
=======

@app.get("/health")
async def health_check():
    """Health check endpoint for production monitoring"""
    from db.deps import get_db
    from core.redis import redis_client
    from sqlalchemy import text
    
    health_status = {
        "status": "healthy",
        "environment": app_settings.ENVIRONMENT,
        "database": "unknown",
        "redis": "unknown",
    }
    
    # Check database connection
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(e)}"
    
    # Check Redis connection
    try:
        if redis_client:
            redis_client.ping()
            health_status["redis"] = "connected"
        else:
            health_status["redis"] = "not configured"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(status_code=status_code, content=health_status)

>>>>>>> 5cfc842 (new version of it)
