import time
import requests
import streamlit as st

BACKEND_URL = "http://backend:8000"

st.set_page_config(page_title="Video Analysis Frontend", layout="wide")
st.title("🎬 Video Analysis Frontend")
st.caption("Streamlit UI + FastAPI backend")

uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov", "mkv"])

if uploaded_file is not None:
    if st.button("Analyze Video"):
        with st.spinner("Uploading video to backend..."):
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "video/mp4")
            }
            resp = requests.post(f"{BACKEND_URL}/jobs", files=files, timeout=120)
            resp.raise_for_status()
            job = resp.json()
            job_id = job["job_id"]

        st.success(f"Job created: {job_id}")

        status_placeholder = st.empty()
        result_placeholder = st.empty()

        while True:
            time.sleep(2)
            r = requests.get(f"{BACKEND_URL}/jobs/{job_id}", timeout=120)
            r.raise_for_status()
            data = r.json()

            status_placeholder.info(f"Job status: {data['status']}")

            if data["status"] == "completed":
                result = data["result"]
                result_placeholder.json(result)
                st.success("Analysis complete")
                break

            if data["status"] == "failed":
                st.error(data.get("error", "Unknown error"))
                break