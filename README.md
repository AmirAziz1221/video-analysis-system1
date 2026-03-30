# Video Analysis System 

## Overview

This project decouples the original Streamlit-based video analysis app into two services:

- **Frontend:** Streamlit UI for video upload, job submission, and result display
- **Backend:** FastAPI service for video processing, YOLOv8 detection, AI summarization, and agent workflow

The goal of this architecture is to:
- move heavy computer vision and agent logic out of the UI
- improve responsiveness
- support asynchronous job processing
- make deployment easier with Docker containers

---

## Architecture

```text
┌─────────────────────┐        HTTP        ┌─────────────────────┐
│   Streamlit UI      │  ───────────────▶  │    FastAPI API      │
│   frontend/app.py   │                    │   backend/app/*     │
└─────────────────────┘                    └─────────────────────┘
         │                                           │
         │                                           │
         ▼                                           ▼
  Upload video, poll job                    Extract frames, run YOLO,
  status, show results                      summarize, build report
```

### Request flow

1. User uploads a video in Streamlit
2. Streamlit sends the file to FastAPI
3. FastAPI creates a `job_id`
4. FastAPI starts background processing
5. Streamlit polls job status
6. When finished, the final report is returned and displayed

---

## Project Structure

```text
video-analysis-system/
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api.py
│   │   ├── schemas.py
│   │   ├── storage.py
│   │   ├── worker.py
│   │   └── services/
│   │       ├── video_input.py
│   │       ├── frame_extractor.py
│   │       ├── object_detector.py
│   │       ├── ai_summarizer.py
│   │       └── agent_workflow.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
├── .env
└── README.md
```

---

## Features

- Streamlit frontend for easy interaction
- FastAPI backend for processing and APIs
- YOLOv8 object detection
- AI summarization support
- Agent workflow support
- asynchronous background job handling
- Dockerized frontend and backend
- clean service separation
- easier future scaling

---

## Backend Responsibilities

The FastAPI backend handles:

- video upload
- job creation
- background processing
- frame extraction
- YOLOv8 detection
- AI summary generation
- agent report generation
- job status tracking
- result storage

### Main API endpoints

#### Health check
```http
GET /health
```

#### Create processing job
```http
POST /jobs
```

#### Check job status
```http
GET /jobs/{job_id}
```

---

## Frontend Responsibilities

The Streamlit frontend handles:

- video upload form
- sending the file to FastAPI
- polling job status
- showing final JSON output
- keeping the UI responsive

The frontend should not contain:
- YOLO inference logic
- frame extraction logic
- LangChain/CrewAI logic
- long-running processing code

---

## Async Processing Strategy

The backend should return quickly when a video is uploaded.

Instead of processing the full video inside the request itself, the backend:

- creates a job entry
- starts background processing
- returns `job_id`
- lets the frontend poll until completion

This avoids blocking the UI and reduces request bottlenecks.

### Why this helps

Without async/background processing:
- uploads may hang
- Streamlit can freeze during heavy work
- long video processing blocks the user flow

With background jobs:
- the API stays responsive
- the UI remains interactive
- the system becomes easier to scale later

### Current approach

This project uses:
- FastAPI endpoint
- background task / job-based processing
- in-memory job tracking

### Future production upgrade options

For larger-scale systems, replace in-memory jobs with:
- Redis + Celery
- RQ
- database-backed job storage
- object storage for uploaded files and reports

---

## Docker Setup

The project uses two Docker containers:

### 1. Backend container
Runs:
- FastAPI
- YOLO
- OpenCV headless
- processing services

### 2. Frontend container
Runs:
- Streamlit UI

### Start both services

```bash
docker compose up --build
```

### Service URLs

- Frontend: `http://localhost:8501`
- Backend API: `http://localhost:8000`
- FastAPI docs: `http://localhost:8000/docs`

---

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
GROQ_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

Use mock providers if you do not want to configure API keys yet.

---

## Recommended Development Order

To avoid errors, implement in this order:

1. create `frontend` and `backend` folders
2. move existing processing modules into `backend/app/services`
3. create FastAPI API files
4. simplify Streamlit into upload + polling only
5. add Dockerfiles
6. add `docker-compose.yml`
7. run containers locally
8. test backend health
9. test job creation endpoint
10. test frontend upload flow
11. enable real YOLO and agent providers

---

## Local Development

### Backend only
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend only
```bash
cd frontend
streamlit run app.py
```

---

## Deployment Notes

- use `opencv-python-headless` in containers
- use Python 3.11 for compatibility
- keep secrets out of GitHub
- use `.env` locally and platform secrets in deployment
- start with mock providers for stable testing

---

## Example Workflow

1. Start both containers
2. Open the Streamlit app
3. Upload a video
4. Submit the job
5. Wait while the frontend polls backend status
6. View the final detection and analysis report

---

## Benefits of This Refactor

This refactor improves the system by:

- decoupling UI from inference logic
- making debugging easier
- isolating processing errors in the backend
- making deployment cleaner
- preparing the project for future scaling
- reducing frontend bottlenecks

---

## Future Improvements

Possible next steps:
- persistent database for jobs
- WebSocket live progress updates
- Celery worker queue
- cloud object storage for uploads
- authentication
- multiple model selection
- result dashboard

---

## Author Note

This README documents the decoupled architecture requested in the task:

- move YOLOv8 and LangChain logic out of Streamlit
- build a dedicated FastAPI backend
- containerize frontend and backend with Docker
- improve responsiveness with async/background processing
