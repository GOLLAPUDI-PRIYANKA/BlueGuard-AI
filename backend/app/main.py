from fastapi import FastAPI

app = FastAPI(
    title="BlueGuard-AI Backend",
    version="1.0.0"
)


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
