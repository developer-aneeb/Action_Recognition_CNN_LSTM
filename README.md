# Action Recognition CNN-LSTM App

A full-stack application for video action recognition using deep learning (CNN-LSTM with MobileNetV2 transfer learning). Supports UCF11 dataset (11 action classes).

## 📦 Structure

```
app/
├── backend/      # FastAPI backend (API, model, video processing)
├── frontend/     # React frontend (UI, upload, results)
├── model/        # Trained model (.h5) and notebook
├── model_results/# Output results, metrics, reports
```

## 🚀 Quick Start

### 1. Clone the Repo
```bash
git clone https://github.com/developer-aneeb/Action_Recognition_CNN_LSTM.git
cd Action_Recognition_CNN_LSTM/app
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```

### 4. Access the App
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## 🧠 Model
- Trained on UCF11 dataset
- 11 action classes: basketball, biking, diving, golf_swing, horse_riding, soccer_juggling, swing, tennis_swing, trampoline_jumping, volleyball_spiking, walking
- Model file: `model/best_action_recognition_model.h5`

## 🛡️ Features
- Drag & drop video upload
- Real-time action prediction
- Confidence scores & top predictions
- Batch prediction support
- Error handling & validation

## 📝 Development
- Python (FastAPI, TensorFlow, OpenCV)
- JavaScript (React, Vite, Tailwind)

## 📁 Ignore
See `.gitignore` for files/folders to exclude from git (models, uploads, node_modules, etc).

## 📄 License
MIT
