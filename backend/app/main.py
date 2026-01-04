"""
FastAPI Main Application
Action Recognition API with CNN-LSTM Model
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core import settings
from app.core.exceptions import ActionRecognitionException
from app.api import router
from app.services import model_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler
    - Loads model on startup
    - Cleanup on shutdown
    """
    # Startup
    logger.info("🚀 Starting Action Recognition API...")
    logger.info(f"   Version: {settings.APP_VERSION}")
    logger.info(f"   Model Path: {settings.MODEL_PATH}")
    
    # Load the model
    success = model_service.load_model()
    if success:
        logger.info("✅ Model loaded and ready for predictions!")
    else:
        logger.warning("⚠️  Model failed to load. API will run in degraded mode.")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Action Recognition API...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Exception handlers
@app.exception_handler(ActionRecognitionException)
async def action_recognition_exception_handler(
    request: Request, 
    exc: ActionRecognitionException
):
    """Handle custom application exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": exc.message,
            "detail": exc.details
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation Error",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.exception(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Include API routes
app.include_router(router, prefix="/api/v1", tags=["Action Recognition"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs": "/docs",
        "health": "/api/v1/health",
        "endpoints": {
            "predict": "/api/v1/predict",
            "batch_predict": "/api/v1/predict/batch",
            "classes": "/api/v1/classes",
            "model_info": "/api/v1/model/info",
            "health": "/api/v1/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
