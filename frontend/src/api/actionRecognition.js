import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for video processing
});

export const actionRecognitionAPI = {
  /**
   * Check API health status
   */
  checkHealth: async () => {
    const response = await api.get('/api/v1/health');
    return response.data;
  },

  /**
   * Get model information
   */
  getModelInfo: async () => {
    const response = await api.get('/api/v1/model/info');
    return response.data;
  },

  /**
   * Get list of action classes
   */
  getClasses: async () => {
    const response = await api.get('/api/v1/classes');
    return response.data;
  },

  /**
   * Predict action from video file
   * @param {File} file - Video file to analyze
   * @param {Function} onProgress - Progress callback
   */
  predictAction: async (file, onProgress = null) => {
    const formData = new FormData();
    formData.append('file', file);

    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    };

    if (onProgress) {
      config.onUploadProgress = (progressEvent) => {
        const progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(progress);
      };
    }

    const response = await api.post('/api/v1/predict', formData, config);
    return response.data;
  },

  /**
   * Batch predict actions from multiple video files
   * @param {File[]} files - Array of video files
   */
  predictBatch: async (files) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await api.post('/api/v1/predict/batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default api;
