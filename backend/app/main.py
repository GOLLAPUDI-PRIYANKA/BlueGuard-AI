from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(
    title="BlueGuard-AI Backend",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "success": True,
        "message": "BlueGuard-AI backend is running"
    }


@app.get("/health")
def health():
    return {
        "success": True,
        "status": "healthy"
    }
