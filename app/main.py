from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.core.logging import configure_logging, get_logger
from app.core.settings import get_settings

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("app.startup", env=settings.app_env)
    yield
    logger.info("app.shutdown")


app = FastAPI(
    title="Okeanos AI Platform API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


def _error_response(
    request: Request,
    *,
    code: str,
    message: str,
    details: object | None,
    status_code: int,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "details": details,
            "request_id": request_id,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return _error_response(
        request,
        code="HTTP_ERROR",
        message=exc.detail if isinstance(exc.detail, str) else "HTTP exception",
        details=None if isinstance(exc.detail, str) else exc.detail,
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return _error_response(
        request,
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details=exc.errors(),
        status_code=422,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("app.unhandled_exception", error=str(exc))
    return _error_response(
        request,
        code="INTERNAL_ERROR",
        message="Internal server error",
        details=None,
        status_code=500,
    )


app.include_router(api_router)
