import os
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import traceback
import logging

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
origins = [
    "https://edustore-omega.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

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
