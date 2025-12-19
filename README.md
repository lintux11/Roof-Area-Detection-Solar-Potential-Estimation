# Roof-Area-Detection-Solar-Potential-Estimation
This project detects usable rooftop areas from satellite images using computer vision and machine learning. A CNN based segmentation model identifies roof surfaces and filters non usable regions. The extracted area is combined with solar irradiance data to estimate solar energy potential and support informed solar panel planning.


# AI-Powered Roof Area Detection System

A production-ready full-stack application to detect roof areas from satellite/drone images, calculate usable solar area, and estimate solar panel capacity using Deep Learning.

## Features

- **AI Segmentation**: Uses PyTorch DeepLabV3 (ResNet50) to detect roof areas.
- **Solar Estimation**: Calculates usable area and potential solar panel capacity.
- **Interactive UI**: React + TailwindCSS frontend with mask overlay and opacity controls.
- **Robust Backend**: FastAPI with PostgreSQL storage and async SQLAlchemy.
- **Dockerized**: Complete stack containerized with Docker Compose.

## Tech Stack

- **Backend**: Python, FastAPI, PyTorch, OpenCV, SQLAlchemy, PostgreSQL
- **Frontend**: TypeScript, React, Vite, TailwindCSS
- **Deployment**: Docker, Docker Compose, Nginx

## Getting Started

### Prerequisites

- Docker and Docker Compose installed.

### Running the Application

1. **Clone the repository** (if not already done).
2. **Start the stack**:
   ```bash
   docker-compose up --build
   ```
3. **Access the application**:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Development Setup

#### Backend
```bash
cd app/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd app/frontend
npm install
npm run dev
```

## API Endpoints

- `POST /api/v1/analysis/upload`: Upload image.
- `POST /api/v1/analysis/segment`: Run segmentation.
- `POST /api/v1/analysis/calculate`: Calculate areas.
- `POST /api/v1/analysis/panel-estimation`: Estimate panels.
- `GET /api/v1/analysis/{id}`: Get report details.

## Project Structure

- `/app/backend`: FastAPI application code.
- `/app/frontend`: React application code.
- `/app/data`: Storage for uploaded images and generated masks.
- `/app/models`: Directory for model weights (auto-downloaded).

