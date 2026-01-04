"""
API Routes for Action Recognition
"""

import time
import logging
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from app.core import (
    settings,
    VideoProcessingException,
    InvalidVideoException,
    ModelNotLoadedException,
    FileTooLargeException,
    UnsupportedFormatException,
)
from app.services import model_service, video_processor
from app.schemas import (
    PredictionResponse,
    PredictionResult,
    TopPrediction,
    ErrorResponse,
    HealthResponse,
    ModelInfoResponse,
    VideoInfo,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    # Check file extension
    if file.filename:
        ext = Path(file.filename).suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise UnsupportedFormatException(
                f"File format '{ext}' not supported. "
                f"Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check API health and model status"
)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model_service.is_loaded else "degraded",
        model_loaded=model_service.is_loaded,
        version=settings.APP_VERSION
    )


@router.get(
    "/model/info",
    response_model=ModelInfoResponse,
    summary="Model Information",
    description="Get information about the loaded model"
)
async def get_model_info():
    """Get model information"""
    info = model_service.get_model_info()
    return ModelInfoResponse(**info)


@router.get(
    "/classes",
    response_model=List[str],
    summary="Get Action Classes",
    description="Get list of all recognizable action classes"
)
async def get_classes():
    """Get list of action classes"""
    return model_service.classes


@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid video file"},
        500: {"model": ErrorResponse, "description": "Processing error"},
        503: {"model": ErrorResponse, "description": "Model not loaded"},
    },
    summary="Predict Action",
    description="Upload a video file to recognize the action being performed"
)
async def predict_action(
    file: UploadFile = File(..., description="Video file to analyze")
):
    """
    Perform action recognition on uploaded video
    
    - **file**: Video file (mp4, avi, mov, mkv, mpg, mpeg, webm)
    
    Returns predicted action with confidence score and top-5 predictions
    """
    start_time = time.time()
    temp_path = None
    
    try:
        # Check if model is loaded
        if not model_service.is_loaded:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model is not loaded. Please try again later."
            )
        
        # Validate file
        validate_file(file)
        
        # Read file content
        content = await file.read()
        
        # Check file size
        file_size = len(content)
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024):.0f}MB"
            )
        
        # Save to temporary file
        temp_path = await video_processor.save_upload_file(content, file.filename or "video.mp4")
        
        # Get video info
        video_info = video_processor.get_video_info(temp_path)
        video_info["filename"] = file.filename
        video_info["size_bytes"] = file_size
        video_info["size_mb"] = round(file_size / (1024 * 1024), 2)
        
        # Extract frames
        frames = video_processor.extract_frames_uniform(temp_path)
        
        if frames is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract frames from video"
            )
        
        # Perform prediction
        pred_idx, confidence, probabilities = model_service.predict(frames)
        
        # Get top predictions
        top_preds = model_service.get_top_k_predictions(probabilities, k=5)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        return PredictionResponse(
            success=True,
            prediction=PredictionResult(
                action=model_service.classes[pred_idx],
                confidence=confidence,
                class_index=pred_idx
            ),
            top_predictions=[TopPrediction(**p) for p in top_preds],
            processing_time_ms=round(processing_time, 2),
            video_info=video_info,
            message=f"Action recognized: {model_service.classes[pred_idx]} ({confidence:.1%} confidence)"
        )
        
    except HTTPException:
        raise
    except UnsupportedFormatException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.message)
        )
    except InvalidVideoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.message)
        )
    except VideoProcessingException as e:
        logger.error(f"Video processing error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video processing failed: {e.message}"
        )
    except ModelNotLoadedException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.message
        )
    except Exception as e:
        logger.exception(f"Unexpected error during prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    finally:
        # Cleanup temporary file
        if temp_path:
            video_processor.cleanup_file(temp_path)


@router.post(
    "/predict/batch",
    summary="Batch Predict Actions",
    description="Upload multiple video files for batch action recognition"
)
async def predict_batch(
    files: List[UploadFile] = File(..., description="Video files to analyze")
):
    """
    Perform action recognition on multiple videos
    
    - **files**: List of video files
    
    Returns predictions for each video
    """
    if not model_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. Please try again later."
        )
    
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per batch"
        )
    
    results = []
    successful = 0
    failed = 0
    total_start = time.time()
    
    for file in files:
        temp_path = None
        try:
            validate_file(file)
            content = await file.read()
            
            if len(content) > settings.MAX_FILE_SIZE:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": "File too large"
                })
                failed += 1
                continue
            
            temp_path = await video_processor.save_upload_file(content, file.filename or "video.mp4")
            frames = video_processor.extract_frames_uniform(temp_path)
            
            if frames is None:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": "Could not extract frames"
                })
                failed += 1
                continue
            
            pred_idx, confidence, probabilities = model_service.predict(frames)
            top_preds = model_service.get_top_k_predictions(probabilities, k=3)
            
            results.append({
                "filename": file.filename,
                "success": True,
                "prediction": {
                    "action": model_service.classes[pred_idx],
                    "confidence": confidence
                },
                "top_predictions": top_preds
            })
            successful += 1
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
            failed += 1
        finally:
            if temp_path:
                video_processor.cleanup_file(temp_path)
    
    total_time = (time.time() - total_start) * 1000
    
    return {
        "success": failed == 0,
        "total_videos": len(files),
        "successful": successful,
        "failed": failed,
        "results": results,
        "total_processing_time_ms": round(total_time, 2)
    }
