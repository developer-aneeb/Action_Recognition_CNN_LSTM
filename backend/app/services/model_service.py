"""
Model Service
Handles loading and inference of the action recognition model
"""

import os
import numpy as np
import logging
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow.keras.models import load_model

from app.core import settings, ModelNotLoadedException

logger = logging.getLogger(__name__)


class ModelService:
    """Service for managing the action recognition model"""
    
    def __init__(self):
        self._model = None
        self._is_loaded = False
        self._model_path = settings.MODEL_PATH
        self._classes = settings.ACTION_CLASSES
        self._num_classes = len(self._classes)
        
        # Input shape: (num_frames, height, width, channels)
        self._input_shape = (
            settings.NUM_FRAMES,
            settings.FRAME_HEIGHT,
            settings.FRAME_WIDTH,
            settings.CHANNELS
        )
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._is_loaded
    
    @property
    def model(self):
        """Get the loaded model"""
        if not self._is_loaded:
            raise ModelNotLoadedException()
        return self._model
    
    @property
    def classes(self) -> List[str]:
        """Get action classes"""
        return self._classes
    
    @property
    def num_classes(self) -> int:
        """Get number of classes"""
        return self._num_classes
    
    def load_model(self) -> bool:
        """
        Load the action recognition model
        
        Returns:
            True if successful, False otherwise
        """
        try:
            model_path = Path(self._model_path)
            
            if not model_path.exists():
                logger.error(f"Model file not found: {self._model_path}")
                return False
            
            logger.info(f"Loading model from: {self._model_path}")
            
            # Load the model
            self._model = load_model(str(model_path), compile=False)
            
            # Recompile with standard settings
            self._model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            self._is_loaded = True
            logger.info("✅ Model loaded successfully!")
            logger.info(f"   Input shape: {self._input_shape}")
            logger.info(f"   Classes: {self._num_classes}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            self._is_loaded = False
            return False
    
    def predict(self, frames: np.ndarray) -> Tuple[int, float, np.ndarray]:
        """
        Perform action recognition on extracted frames
        
        Args:
            frames: numpy array of shape (num_frames, height, width, channels)
                   Values should be in range [0, 255]
        
        Returns:
            Tuple of (predicted_class_index, confidence, all_probabilities)
        """
        if not self._is_loaded:
            raise ModelNotLoadedException()
        
        # Normalize frames to [0, 1]
        if frames.max() > 1.0:
            frames = frames / 255.0
        
        # Add batch dimension if needed
        if len(frames.shape) == 4:
            frames = np.expand_dims(frames, axis=0)
        
        # Predict
        predictions = self._model.predict(frames, verbose=0)[0]
        
        # Get top prediction
        predicted_idx = int(np.argmax(predictions))
        confidence = float(predictions[predicted_idx])
        
        return predicted_idx, confidence, predictions
    
    def get_top_k_predictions(
        self, 
        probabilities: np.ndarray, 
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top-k predictions with class names
        
        Args:
            probabilities: Prediction probabilities
            k: Number of top predictions to return
        
        Returns:
            List of dictionaries with rank, action, and confidence
        """
        k = min(k, self._num_classes)
        top_indices = np.argsort(probabilities)[-k:][::-1]
        
        results = []
        for rank, idx in enumerate(top_indices, 1):
            results.append({
                "rank": rank,
                "action": self._classes[idx],
                "confidence": float(probabilities[idx])
            })
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_name": "Action Recognition CNN-LSTM (MobileNetV2)",
            "model_path": self._model_path,
            "num_classes": self._num_classes,
            "classes": self._classes,
            "input_shape": {
                "num_frames": self._input_shape[0],
                "height": self._input_shape[1],
                "width": self._input_shape[2],
                "channels": self._input_shape[3]
            },
            "is_loaded": self._is_loaded
        }


# Singleton instance
model_service = ModelService()
