import { useState, useCallback } from 'react';
import { actionRecognitionAPI } from '../api/actionRecognition';

/**
 * Custom hook for action recognition functionality
 */
export const useActionRecognition = () => {
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  /**
   * Predict action from video file
   */
  const predict = useCallback(async (file) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setUploadProgress(0);

    try {
      const data = await actionRecognitionAPI.predictAction(file, (progress) => {
        setUploadProgress(progress);
      });

      if (!data.success) {
        throw new Error(data.error || 'Prediction failed');
      }

      setResult(data);
      return data;
    } catch (err) {
      const errorMessage =
        err.response?.data?.detail ||
        err.response?.data?.error ||
        err.message ||
        'An error occurred';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  }, []);

  /**
   * Reset state
   */
  const reset = useCallback(() => {
    setLoading(false);
    setUploadProgress(0);
    setResult(null);
    setError(null);
  }, []);

  return {
    predict,
    reset,
    loading,
    uploadProgress,
    result,
    error,
  };
};

/**
 * Custom hook to check API health
 */
export const useAPIHealth = () => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);

  const checkHealth = useCallback(async () => {
    setLoading(true);
    try {
      const data = await actionRecognitionAPI.checkHealth();
      setHealth(data);
      return data;
    } catch (err) {
      setHealth({ status: 'error', model_loaded: false });
    } finally {
      setLoading(false);
    }
  }, []);

  return { health, checkHealth, loading };
};

export default useActionRecognition;
