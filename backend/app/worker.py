import os
import uuid
import json
from app.storage import JOBS
from app.services.video_input import load_video, release_video
from app.services.frame_extractor import extract_frames, get_frame_stats
from app.services.object_detector import load_detector, detect_objects_in_frames, summarize_detections
from app.services.ai_summarizer import get_summary
from app.services.agent_workflow import run_agent

MODEL = None


def get_model():
    global MODEL
    if MODEL is None:
        MODEL = load_detector()
    return MODEL


def process_video_job(job_id: str, video_path: str, ai_provider: str = "mock", agent_mode: str = "mock"):
    try:
        JOBS[job_id]["status"] = "processing"

        output_dir = os.path.join("data", job_id)
        os.makedirs(output_dir, exist_ok=True)
        frame_dir = os.path.join(output_dir, "frames")
        annotated_dir = os.path.join(output_dir, "annotated")

        cap, meta = load_video(video_path)
        frame_paths, frame_arrays = extract_frames(
            cap,
            output_dir=frame_dir,
            frame_interval=30,
            max_frames=20,
        )
        release_video(cap)

        stats = get_frame_stats(frame_arrays)

        model = get_model()
        all_detections = detect_objects_in_frames(
            model,
            frame_arrays,
            frame_paths,
            confidence_threshold=0.4,
            output_dir=annotated_dir,
        )

        detection_summary = summarize_detections(all_detections)
        ai_summary = get_summary(detection_summary, meta, provider=ai_provider)
        agent_report = run_agent(detection_summary, meta, ai_summary, mode=agent_mode)

        result = {
            "video_metadata": meta,
            "frame_stats": stats,
            "detection_summary": detection_summary,
            "all_detections": all_detections,
            "ai_summary": ai_summary,
            "agent_report": agent_report,
        }

        report_path = os.path.join(output_dir, "analysis_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["result"] = result

    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)