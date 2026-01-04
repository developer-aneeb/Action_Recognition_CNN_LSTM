"""
Custom Exception Classes and Error Handlers
"""

from fastapi import HTTPException, status
from typing import Any, Optional


class ActionRecognitionException(Exception):
    """Base exception for action recognition errors"""
    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class ModelNotLoadedException(ActionRecognitionException):
    """Raised when the model is not loaded"""
    def __init__(self, message: str = "Model is not loaded. Please wait for initialization."):
        super().__init__(message)


class VideoProcessingException(ActionRecognitionException):
    """Raised when video processing fails"""
    def __init__(self, message: str = "Failed to process video", details: Optional[Any] = None):
        super().__init__(message, details)


class InvalidVideoException(ActionRecognitionException):
    """Raised when video file is invalid"""
    def __init__(self, message: str = "Invalid video file"):
        super().__init__(message)


class FileTooLargeException(ActionRecognitionException):
    """Raised when uploaded file exceeds size limit"""
    def __init__(self, message: str = "File size exceeds maximum allowed limit"):
        super().__init__(message)


class UnsupportedFormatException(ActionRecognitionException):
    """Raised when file format is not supported"""
    def __init__(self, message: str = "Unsupported file format"):
        super().__init__(message)


# HTTP Exception helpers
def raise_not_found(detail: str = "Resource not found"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def raise_bad_request(detail: str = "Bad request"):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def raise_internal_error(detail: str = "Internal server error"):
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


def raise_service_unavailable(detail: str = "Service temporarily unavailable"):
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)
