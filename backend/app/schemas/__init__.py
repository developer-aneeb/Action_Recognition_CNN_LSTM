"""
Pydantic Schemas for API Request/Response Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============================================
# Health & Status Schemas
# ============================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., example="healthy")
    model_loaded: bool = Field(..., example=True)
    version: str = Field(..., example="1.0.0")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ModelInfoResponse(BaseModel):
    """Model information response"""
    model_name: str = Field(..., example="Action Recognition CNN-LSTM")
    model_path: str
    num_classes: int = Field(..., example=11)
    classes: List[str]
    input_shape: Dict[str, int]
    is_loaded: bool


# ============================================
# Prediction Schemas
# ============================================

class PredictionResult(BaseModel):
    """Single prediction result"""
    action: str = Field(..., example="basketball")
    confidence: float = Field(..., ge=0, le=1, example=0.95)
    class_index: int = Field(..., example=0)


class TopPrediction(BaseModel):
    """Top-k prediction"""
    rank: int = Field(..., example=1)
    action: str = Field(..., example="basketball")
    confidence: float = Field(..., ge=0, le=1, example=0.95)


class PredictionResponse(BaseModel):
    """Full prediction response"""
    success: bool = Field(..., example=True)
    prediction: PredictionResult
    top_predictions: List[TopPrediction]
    processing_time_ms: float = Field(..., example=150.5)
    video_info: Optional[Dict[str, Any]] = None
    message: str = Field(..., example="Action recognized successfully")


class BatchPredictionResponse(BaseModel):
    """Batch prediction response"""
    success: bool
    total_videos: int
    successful: int
    failed: int
    results: List[PredictionResponse]
    total_processing_time_ms: float


# ============================================
# Error Schemas
# ============================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = Field(default=False)
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    success: bool = Field(default=False)
    error: str = "Validation Error"
    details: List[Dict[str, Any]]


# ============================================
# Video Info Schemas
# ============================================

class VideoInfo(BaseModel):
    """Video metadata"""
    filename: str
    size_bytes: int
    size_mb: float
    duration_seconds: Optional[float] = None
    fps: Optional[float] = None
    total_frames: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None


class FrameExtractionInfo(BaseModel):
    """Frame extraction details"""
    frames_extracted: int
    frame_size: str
    extraction_method: str = "uniform_sampling"
