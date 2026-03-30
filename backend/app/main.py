from fastapi import FastAPI
from app.api import router

app = FastAPI(title="Video Analysis Backend")
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}