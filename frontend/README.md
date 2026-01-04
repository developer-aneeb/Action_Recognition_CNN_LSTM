# Action Recognition Frontend

A React-based frontend for the Action Recognition API.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### 3. Make Sure Backend is Running

The frontend expects the backend API at `http://localhost:8000`

```bash
cd ../backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── actionRecognition.js  # API client
│   ├── hooks/
│   │   └── useActionRecognition.js  # Custom hooks
│   ├── App.jsx  # Main component
│   ├── main.jsx  # Entry point
│   └── index.css  # Styles
├── package.json
├── vite.config.js
├── tailwind.config.js
└── index.html
```

## ✨ Features

- 📹 Drag & drop video upload
- 🎯 Real-time action recognition
- 📊 Confidence scores and top predictions
- 📱 Responsive design
- ⚡ Fast processing feedback

## 🎯 Supported Actions

| Action | Emoji |
|--------|-------|
| Basketball | 🏀 |
| Biking | 🚴 |
| Diving | 🏊 |
| Golf Swing | ⛳ |
| Horse Riding | 🐴 |
| Soccer Juggling | ⚽ |
| Swing | 🎡 |
| Tennis Swing | 🎾 |
| Trampoline Jumping | 🤸 |
| Volleyball Spiking | 🏐 |
| Walking | 🚶 |

## 🔧 Configuration

Create a `.env` file to customize the API URL:

```env
VITE_API_URL=http://localhost:8000
```

## 🏗️ Build for Production

```bash
npm run build
```

Output will be in the `dist` folder.
