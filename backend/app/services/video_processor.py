"""
Video Processing Service
Handles video file processing and frame extraction
"""

import cv2
import numpy as np
import tempfile
import os
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from app.core import settings, VideoProcessingException, InvalidVideoException

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Service for processing videos and extracting frames"""
    
    def __init__(self):
        self.num_frames = settings.NUM_FRAMES
        self.frame_height = settings.FRAME_HEIGHT
        self.frame_width = settings.FRAME_WIDTH
        self.target_size = (self.frame_width, self.frame_height)
    
    def extract_frames_uniform(
        self, 
        video_path: str, 
        num_frames: Optional[int] = None,
        target_size: Optional[Tuple[int, int]] = None
    ) -> Optional[np.ndarray]:
        """
        Extract frames uniformly sampled across the video.
        Ensures temporal coverage of the entire action.
        
        Args:
            video_path: Path to video file
            num_frames: Number of frames to extract (default from settings)
            target_size: (width, height) for resizing (default from settings)
        
        Returns:
            numpy array of shape (num_frames, height, width, 3) or None if failed
        """
        num_frames = num_frames or self.num_frames
        target_size = target_size or self.target_size
        
        frames = []
        cap = None
        
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"Could not open video: {video_path}")
                raise InvalidVideoException(f"Cannot open video file")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames == 0:
                raise InvalidVideoException("Video has no frames")
            
            if total_frames < num_frames:
                # Read all frames and pad
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, target_size)
                    frames.append(frame)
                
                # Pad by repeating last frame
                while len(frames) < num_frames:
                    if frames:
                        frames.append(frames[-1].copy())
                    else:
                        raise InvalidVideoException("Could not extract any frames")
            else:
                # Uniform sampling
                indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
                
                for idx in indices:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                    ret, frame = cap.read()
                    if ret:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame = cv2.resize(frame, target_size)
                        frames.append(frame)
                    else:
                        # Fallback: use last valid frame
                        if frames:
                            frames.append(frames[-1].copy())
            
            if len(frames) != num_frames:
                raise VideoProcessingException(
                    f"Frame extraction incomplete: got {len(frames)}, expected {num_frames}"
                )
            
            return np.array(frames, dtype=np.float32)
            
        except (InvalidVideoException, VideoProcessingException):
            raise
        except Exception as e:
            logger.error(f"Error extracting frames: {str(e)}")
            raise VideoProcessingException(f"Frame extraction failed: {str(e)}")
        finally:
            if cap is not None:
                cap.release()
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get video metadata
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        cap = None
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise InvalidVideoException("Cannot open video file")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0
            
            return {
                "fps": round(fps, 2),
                "total_frames": total_frames,
                "width": width,
                "height": height,
                "duration_seconds": round(duration, 2)
            }
        except InvalidVideoException:
            raise
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return {}
        finally:
            if cap is not None:
                cap.release()
    
    async def save_upload_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to temporary location
        
        Args:
            file_content: File bytes
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        # Ensure upload directory exists
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create unique filename
        suffix = Path(filename).suffix
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=suffix, 
            dir=upload_dir
        )
        
        try:
            temp_file.write(file_content)
            temp_file.close()
            return temp_file.name
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            raise VideoProcessingException(f"Failed to save file: {str(e)}")
    
    def cleanup_file(self, file_path: str) -> None:
        """Remove temporary file"""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {str(e)}")


# Singleton instance
video_processor = VideoProcessor()
