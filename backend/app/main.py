from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import setup_logging
from app.api.v1 import spills, vessels, dashboard, reports

logger = setup_logging()
settings = get_settings()

app = FastAPI(
    title="BlueGuard AI — Marine Oil Spill Detection Backend",
    description=(
        "Backend API for oil spill detection, backtracking, vessel attribution, "
        "forecasting and environmental impact assessment. "
        "Part of SIH 2026 Problem Statement 26143."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "errorCode": exc.error_code.value,
            "message": exc.message,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "errorCode": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
        },
    )


app.include_router(spills.router, prefix="/api/v1")
app.include_router(vessels.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "service": "BlueGuard AI Backend"}


@app.get("/health", tags=["health"])
async def health():
    return {"status": "healthy"}
