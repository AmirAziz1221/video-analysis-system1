import os
import uuid
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from app.schemas import JobCreateResponse, JobStatusResponse
from app.storage import JOBS
from app.worker import process_video_job

router = APIRouter()


@router.post("/jobs", response_model=JobCreateResponse)
async def create_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    job_id = str(uuid.uuid4())
    os.makedirs("uploads", exist_ok=True)

    ext = os.path.splitext(file.filename)[1] or ".mp4"
    save_path = os.path.join("uploads", f"{job_id}{ext}")

    with open(save_path, "wb") as f:
        f.write(await file.read())

    JOBS[job_id] = {
        "status": "queued",
        "result": None,
        "error": None,
    }

    background_tasks.add_task(process_video_job, job_id, save_path, "mock", "mock")
    return JobCreateResponse(job_id=job_id, status="queued")


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        result=job.get("result"),
        error=job.get("error"),
    )