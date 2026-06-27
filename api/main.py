from fastapi import FastAPI
from api.routers import interactions
from api.services import inference

app = FastAPI(
    title="Hybrid Music Recommendation API",
    description="Hệ thống gọi ý âm nhạc kết hợp Collaborative Filtering và Baseline.",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    inference.load_models()

app.include_router(interactions.router)

@app.get("/", tags=["Health Check"])
def root():
    return {"status": "ok", "message": "API đang hoạt động bình thường!"}