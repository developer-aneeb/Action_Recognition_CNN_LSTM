# Action Recognition API Backend

A FastAPI-based backend service for video action recognition using a trained CNN-LSTM model with MobileNetV2 transfer learning.

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration settings
│   │   └── exceptions.py    # Custom exceptions
│   ├── schemas/
│   │   └── __init__.py      # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── model_service.py # ML model handling
│       └── video_processor.py # Video/frame processing
├── uploads/                  # Temporary upload directory
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Edit .env if needed
```

### 3. Ensure Model File Exists

Make sure the model file is at:
```
Recogition_app/model/best_action_recognition_model.h5
```

### 4. Run the Server

```bash
# Development mode
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### Base URL: `http://localhost:8000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and available endpoints |
| `/docs` | GET | Swagger UI documentation |
| `/redoc` | GET | ReDoc documentation |
| `/api/v1/health` | GET | Health check & model status |
| `/api/v1/model/info` | GET | Model information |
| `/api/v1/classes` | GET | List all action classes |
| `/api/v1/predict` | POST | Predict action from video |
| `/api/v1/predict/batch` | POST | Batch predict multiple videos |

### Predict Action

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_video.mp4"
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "action": "basketball",
    "confidence": 0.95,
    "class_index": 0
  },
  "top_predictions": [
    {"rank": 1, "action": "basketball", "confidence": 0.95},
    {"rank": 2, "action": "volleyball_spiking", "confidence": 0.03},
    {"rank": 3, "action": "soccer_juggling", "confidence": 0.01}
  ],
  "processing_time_ms": 150.5,
  "video_info": {
    "filename": "your_video.mp4",
    "size_mb": 2.5,
    "duration_seconds": 5.0,
    "fps": 30.0
  },
  "message": "Action recognized: basketball (95.0% confidence)"
}
```

## 🎯 Supported Action Classes

The model recognizes 11 action classes from UCF11 dataset:

1. basketball
2. biking
3. diving
4. golf_swing
5. horse_riding
6. soccer_juggling
7. swing
8. tennis_swing
9. trampoline_jumping
10. volleyball_spiking
11. walking

## 📁 Supported Video Formats

- MP4 (`.mp4`)
- AVI (`.avi`)
- MOV (`.mov`)
- MKV (`.mkv`)
- MPG/MPEG (`.mpg`, `.mpeg`)
- WebM (`.webm`)

**Max file size:** 100MB

## 🔧 Configuration

Environment variables can be set in `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `PORT` | `8000` | Server port |
| `HOST` | `0.0.0.0` | Server host |
| `NUM_FRAMES` | `16` | Frames to extract per video |
| `FRAME_HEIGHT` | `112` | Frame height in pixels |
| `FRAME_WIDTH` | `112` | Frame width in pixels |
| `MAX_FILE_SIZE` | `104857600` | Max upload size (100MB) |

## 🔗 Frontend Integration

### JavaScript/TypeScript Example

```javascript
const predictAction = async (videoFile) => {
  const formData = new FormData();
  formData.append('file', videoFile);

  const response = await fetch('http://localhost:8000/api/v1/predict', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Prediction failed');
  }

  return response.json();
};
```

### React Hook Example

```jsx
import { useState } from 'react';

const useActionRecognition = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const predict = async (file) => {
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const res = await fetch('http://localhost:8000/api/v1/predict', {
        method: 'POST',
        body: formData,
      });
      
      const data = await res.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Prediction failed');
      }
      
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { predict, result, loading, error };
};
```

## 🛡️ Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "error": "Error type",
  "detail": "Detailed error message"
}
```

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request (invalid video, unsupported format) |
| 413 | File too large |
| 422 | Validation error |
| 500 | Internal server error |
| 503 | Model not loaded |

## 📝 License

MIT License
