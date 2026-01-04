import React, { useState, useRef, useCallback, useEffect } from 'react';
import { 
  Upload, 
  Video, 
  CheckCircle, 
  AlertCircle, 
  Loader2, 
  BarChart3,
  Clock,
  FileVideo,
  Trash2,
  Info,
  Activity
} from 'lucide-react';
import { useActionRecognition, useAPIHealth } from './hooks/useActionRecognition';

// Action class icons/emojis
const ACTION_ICONS = {
  basketball: '🏀',
  biking: '🚴',
  diving: '🏊',
  golf_swing: '⛳',
  horse_riding: '🐴',
  soccer_juggling: '⚽',
  swing: '🎡',
  tennis_swing: '🎾',
  trampoline_jumping: '🤸',
  volleyball_spiking: '🏐',
  walking: '🚶',
};

function App() {
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [videoPreview, setVideoPreview] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const { predict, reset, loading, uploadProgress, result, error } = useActionRecognition();
  const { health, checkHealth } = useAPIHealth();

  // Check API health on mount
  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  // Handle file selection
  const handleFileSelect = useCallback((file) => {
    if (!file) return;

    // Validate file type
    const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime', 'video/x-msvideo', 'video/mpeg', 'video/webm'];
    if (!validTypes.some(type => file.type.includes(type.split('/')[1]))) {
      alert('Please select a valid video file (MP4, AVI, MOV, MPEG, WebM)');
      return;
    }

    // Validate file size (100MB)
    if (file.size > 100 * 1024 * 1024) {
      alert('File size must be less than 100MB');
      return;
    }

    setSelectedFile(file);
    setVideoPreview(URL.createObjectURL(file));
    reset();
  }, [reset]);

  // Handle drag and drop
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  }, [handleFileSelect]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragOver(false);
  }, []);

  // Handle file input change
  const handleInputChange = useCallback((e) => {
    const file = e.target.files[0];
    handleFileSelect(file);
  }, [handleFileSelect]);

  // Handle prediction
  const handlePredict = useCallback(async () => {
    if (!selectedFile) return;
    try {
      await predict(selectedFile);
    } catch (err) {
      console.error('Prediction error:', err);
    }
  }, [selectedFile, predict]);

  // Clear selection
  const handleClear = useCallback(() => {
    setSelectedFile(null);
    setVideoPreview(null);
    reset();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [reset]);

  // Format confidence as percentage
  const formatConfidence = (confidence) => {
    return `${(confidence * 100).toFixed(1)}%`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Activity className="w-8 h-8 text-indigo-400" />
              <div>
                <h1 className="text-2xl font-bold text-white">Action Recognition</h1>
                <p className="text-sm text-white/60">AI-Powered Video Analysis</p>
              </div>
            </div>
            
            {/* API Status */}
            <div className="flex items-center gap-2">
              {health?.model_loaded ? (
                <span className="flex items-center gap-1 text-green-400 text-sm">
                  <CheckCircle className="w-4 h-4" />
                  Model Ready
                </span>
              ) : (
                <span className="flex items-center gap-1 text-yellow-400 text-sm">
                  <AlertCircle className="w-4 h-4" />
                  Model Loading...
                </span>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="space-y-6">
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                <Upload className="w-5 h-5" />
                Upload Video
              </h2>

              {/* Drop Zone */}
              <div
                className={`upload-zone rounded-xl p-8 text-center cursor-pointer transition-all ${
                  isDragOver ? 'drag-over border-indigo-400 bg-indigo-500/20' : 'border-white/30'
                }`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="video/*"
                  className="hidden"
                  onChange={handleInputChange}
                />
                
                <Video className="w-12 h-12 mx-auto text-white/60 mb-4" />
                <p className="text-white font-medium mb-2">
                  Drag & drop your video here
                </p>
                <p className="text-white/60 text-sm">
                  or click to browse
                </p>
                <p className="text-white/40 text-xs mt-2">
                  MP4, AVI, MOV, MPEG, WebM • Max 100MB
                </p>
              </div>

              {/* Selected File Info */}
              {selectedFile && (
                <div className="mt-4 bg-white/5 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <FileVideo className="w-8 h-8 text-indigo-400" />
                      <div>
                        <p className="text-white font-medium truncate max-w-[200px]">
                          {selectedFile.name}
                        </p>
                        <p className="text-white/60 text-sm">
                          {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={handleClear}
                      className="p-2 text-white/60 hover:text-red-400 transition"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              )}

              {/* Video Preview */}
              {videoPreview && (
                <div className="mt-4 rounded-lg overflow-hidden">
                  <video
                    ref={videoRef}
                    src={videoPreview}
                    controls
                    className="w-full max-h-64 bg-black rounded-lg"
                  />
                </div>
              )}

              {/* Progress Bar */}
              {loading && uploadProgress > 0 && (
                <div className="mt-4">
                  <div className="flex justify-between text-sm text-white/60 mb-1">
                    <span>Uploading...</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-white/20 rounded-full h-2">
                    <div
                      className="progress-bar bg-indigo-500 h-2 rounded-full"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Predict Button */}
              <button
                onClick={handlePredict}
                disabled={!selectedFile || loading || !health?.model_loaded}
                className={`w-full mt-4 py-3 px-6 rounded-xl font-semibold text-white transition-all ${
                  !selectedFile || loading || !health?.model_loaded
                    ? 'bg-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 shadow-lg hover:shadow-indigo-500/25'
                }`}
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <Activity className="w-5 h-5" />
                    Recognize Action
                  </span>
                )}
              </button>
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-red-400 font-medium">Error</p>
                    <p className="text-red-300/80 text-sm">{error}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Results Section */}
          <div className="space-y-6">
            {result ? (
              <>
                {/* Main Prediction */}
                <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
                  <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    Prediction Result
                  </h2>

                  <div className="text-center py-6">
                    <div className="text-6xl mb-4">
                      {ACTION_ICONS[result.prediction.action] || '🎬'}
                    </div>
                    <h3 className="text-3xl font-bold text-white capitalize mb-2">
                      {result.prediction.action.replace('_', ' ')}
                    </h3>
                    <div className="inline-flex items-center gap-2 bg-green-500/20 text-green-400 px-4 py-2 rounded-full">
                      <BarChart3 className="w-4 h-4" />
                      <span className="font-semibold">
                        {formatConfidence(result.prediction.confidence)} Confidence
                      </span>
                    </div>
                  </div>

                  {/* Processing Time */}
                  <div className="flex items-center justify-center gap-2 text-white/60 text-sm mt-4">
                    <Clock className="w-4 h-4" />
                    Processed in {result.processing_time_ms.toFixed(0)}ms
                  </div>
                </div>

                {/* Top Predictions */}
                <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5" />
                    Top Predictions
                  </h2>

                  <div className="space-y-3">
                    {result.top_predictions.map((pred, idx) => (
                      <div key={idx} className="flex items-center gap-3">
                        <span className="text-2xl">{ACTION_ICONS[pred.action] || '🎬'}</span>
                        <div className="flex-1">
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-white capitalize">
                              {pred.action.replace('_', ' ')}
                            </span>
                            <span className="text-white/60">
                              {formatConfidence(pred.confidence)}
                            </span>
                          </div>
                          <div className="w-full bg-white/20 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full transition-all ${
                                idx === 0 ? 'bg-green-500' : idx === 1 ? 'bg-yellow-500' : 'bg-blue-500'
                              }`}
                              style={{ width: `${pred.confidence * 100}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Video Info */}
                {result.video_info && (
                  <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                      <Info className="w-5 h-5" />
                      Video Information
                    </h2>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-white/60">Duration</p>
                        <p className="text-white font-medium">
                          {result.video_info.duration_seconds?.toFixed(1) || 'N/A'}s
                        </p>
                      </div>
                      <div>
                        <p className="text-white/60">FPS</p>
                        <p className="text-white font-medium">
                          {result.video_info.fps?.toFixed(0) || 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-white/60">Resolution</p>
                        <p className="text-white font-medium">
                          {result.video_info.width}x{result.video_info.height}
                        </p>
                      </div>
                      <div>
                        <p className="text-white/60">Size</p>
                        <p className="text-white font-medium">
                          {result.video_info.size_mb} MB
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </>
            ) : (
              /* Placeholder when no result */
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 h-full flex flex-col items-center justify-center min-h-[400px]">
                <Video className="w-16 h-16 text-white/30 mb-4" />
                <h3 className="text-xl font-medium text-white/60 mb-2">
                  No Results Yet
                </h3>
                <p className="text-white/40 text-center max-w-sm">
                  Upload a video and click "Recognize Action" to see the AI prediction
                </p>

                {/* Supported Actions */}
                <div className="mt-8 text-center">
                  <p className="text-white/60 text-sm mb-3">Supported Actions:</p>
                  <div className="flex flex-wrap justify-center gap-2">
                    {Object.entries(ACTION_ICONS).map(([action, icon]) => (
                      <span
                        key={action}
                        className="px-3 py-1 bg-white/10 rounded-full text-sm text-white/80 flex items-center gap-1"
                      >
                        {icon} {action.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 border-t border-white/10">
        <div className="max-w-6xl mx-auto px-4 text-center text-white/40 text-sm">
          <p>Action Recognition using CNN-LSTM with MobileNetV2 Transfer Learning</p>
          <p className="mt-1">Trained on UCF11 Dataset • 11 Action Classes</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
