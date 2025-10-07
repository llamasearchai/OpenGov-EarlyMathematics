"""Main FastAPI application for OpenGov-EarlyMathematics."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from opengov_earlymathematics.api.routes import api_router
from opengov_earlymathematics.config import settings
from opengov_earlymathematics.utils.logger import get_logger

logger = get_logger(__name__)
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting OpenGov-EarlyMathematics API")

    # Initialize services
    await initialize_services()

    yield

    # Cleanup
    logger.info("Shutting down OpenGov-EarlyMathematics API")


async def initialize_services():
    """Initialize application services."""
    try:
        # Initialize database connections
        # await init_database()

        # Initialize ML models
        # await init_ml_models()

        # Initialize cache
        # await init_redis()

        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description="AI-powered personalized mathematics education platform API",
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = __import__("datetime").datetime.utcnow()

        response = await call_next(request)

        process_time = (__import__("datetime").datetime.utcnow() - start_time).total_seconds()

        # Use plain string formatting to avoid passing extra kwargs to stdlib logger
        logger.info(
            f"Request processed method={request.method} url={request.url} "
            f"status_code={response.status_code} process_time={process_time:.6f}s"
        )

        return response

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": settings.api_version}

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "OpenGov-EarlyMathematics API",
            "version": settings.api_version,
            "description": "AI-powered personalized mathematics education platform",
            "docs": "/docs",
        }

    return app


# Create application instance
app = create_application()

# Include API routes
app.include_router(api_router, prefix=settings.api_prefix)


if __name__ == "__main__":  # pragma: no cover

    import uvicorn

    logger.info("Starting server...")
    uvicorn.run(
        "opengov_earlymathematics.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
