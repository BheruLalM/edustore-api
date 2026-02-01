import os
import time
import sys
import logging
import traceback

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from api.api_router import api_router
from core.config import app_settings
from core.exceptions import (
    DomainError,
    ERROR_STATUS_MAP,
)

# ------------------------------------------------------------------
# LOGGING CONFIG
# ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# APP INIT
# ------------------------------------------------------------------
app = FastAPI(
    title="EduStore",
    description="EduStore Backend API",
)

# Router
app.include_router(api_router)

# ------------------------------------------------------------------
# GLOBAL EXCEPTION MIDDLEWARE
# ------------------------------------------------------------------
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(
            "Unhandled exception %s %s",
            request.method,
            request.url.path,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal Server Error",
                "error_code": "unhandled_exception",
            },
        )

@app.middleware("http")
async def options_preflight_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return JSONResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": app_settings.FRONTEND_URL,
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "86400",
            },
        )
    return await call_next(request)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[app_settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ------------------------------------------------------------------
# REQUEST TIMING MIDDLEWARE
# ------------------------------------------------------------------
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        response.headers["X-Process-Time"] = f"{duration:.3f}"

        if duration > 0.5:
            logger.warning(
                "Slow request %s %s %.3fs",
                request.method,
                request.url.path,
                duration,
            )
        return response


app.add_middleware(TimingMiddleware)

# ------------------------------------------------------------------
# DOMAIN EXCEPTIONS
# ------------------------------------------------------------------
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
            "error_code": "rate_limit_exceeded"
            if exc.status_code == 429
            else "error",
        },
    )

# ------------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------------
@app.get("/")
async def home():
    return {"message": "EduStore API running"}

@app.get("/health")
async def health_check():
    from db.deps import get_db
    from core.redis import redis_client
    from sqlalchemy import text

    status = {
        "status": "healthy",
        "environment": app_settings.ENVIRONMENT,
        "database": "unknown",
        "redis": "unknown",
    }

    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        status["database"] = "connected"
    except Exception as e:
        status["status"] = "unhealthy"
        status["database"] = str(e)

    try:
        if redis_client:
            redis_client.ping()
            status["redis"] = "connected"
        else:
            status["redis"] = "not configured"
    except Exception as e:
        status["redis"] = str(e)

    return JSONResponse(
        status_code=200 if status["status"] == "healthy" else 503,
        content=status,
    )
