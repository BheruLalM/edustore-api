import os
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

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
)

app = FastAPI(title="EduStore", description="Here you have all friends together")
app.include_router(api_router)

ERROR_STATUS_MAP = {
    UserNotFound: 404,
    CannotFollowYourself: 400,
    NotFollowing: 404,
    OTPCooldownActive: 429,
    DocumentNotFound: 404,
    DocumentAccessDenied: 403,
    DownloadUrlGenerationFailed: 503,
    DocumentOwnershipError: 400,
    InvalidAvatarContentType: 400,
    InvalidAvatarKey: 400,
    AvatarUploadExpired: 400,
    AvatarNotFound: 404,
}
origins = [
    "http://localhost:5173",  # frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # frontend URL allow karo
    allow_credentials=True,          # cookies allow
    allow_methods=["*"],             # GET, POST, OPTIONS etc.
    allow_headers=["*"],             # Content-Type, Authorization etc.
)

# Add GZip compression for responses > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=6)

# Request timing middleware for performance monitoring
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
