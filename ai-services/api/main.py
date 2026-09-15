"""
api/main.py
Inference API for the oil spill segmentation model (M2 integration glue).

Implements the team contract:
    POST /predict   Image URI + model version -> mask URI, confidence, polygons

Sits on top of src/inference.py. The model works in 256x256 pixel space;
polygons are returned in pixel coordinates and georeferenced by the backend
(GIS service provides real scene bounds later).
"""

import os
import re
import sys
import tempfile
import urllib.request
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

API_DIR = Path(__file__).resolve().parent
SRC_DIR = API_DIR.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from inference import CHECKPOINT_PATH, predict  # noqa: E402

RESULTS_DIR = API_DIR.parent / "results" / "masks"

app = FastAPI(
    title="BlueGuard AI - Oil Spill Segmentation Service",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    imageUri: str = Field(..., description="Local path, http(s) URL or file:// URI of the scene image")
    modelVersion: str = Field(default="unet_v1", description="Model version identifier")


class PredictResponse(BaseModel):
    detected: bool
    confidence: float
    maskUri: str | None
    modelVersion: str
    polygons: list[list[list[float]]]
    numRegions: int


def _checkpoint_available() -> bool:
    checkpoint_exists = Path(CHECKPOINT_PATH).exists()
    if checkpoint_exists:
        file_size = Path(CHECKPOINT_PATH).stat().st_size
        print(f"✅ Model checkpoint found: {CHECKPOINT_PATH} ({file_size / (1024*1024):.2f} MB)")
    else:
        print(f"⚠️  Model checkpoint not found at: {CHECKPOINT_PATH}")
    return checkpoint_exists


def _ensure_model_exists():
    """Create mock model if it doesn't exist."""
    if not _checkpoint_available():
        print("Creating mock model on startup...")
        try:
            from create_mock_model import create_mock_model
            create_mock_model()
            print("✅ Mock model created successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to create mock model: {e}")
            return False
    return True


def _resolve_image(image_uri: str) -> str:
    if image_uri.startswith("s3://"):
        raise HTTPException(
            status_code=422,
            detail="s3:// URIs are not supported yet; pass a local path or http(s)/file URL",
        )
    if image_uri.startswith(("http://", "https://", "file://")):
        with tempfile.NamedTemporaryFile(suffix=Path(image_uri).suffix or ".png", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            urllib.request.urlretrieve(image_uri, tmp_path)
            return tmp_path
        except OSError:
            os.unlink(tmp_path)
            raise HTTPException(status_code=422, detail=f"Could not download image from '{image_uri}'")
    local = Path(image_uri)
    if not local.exists():
        raise HTTPException(status_code=422, detail=f"Image not found at '{local}'")
    return str(local)


def _mask_to_png(mask, image_uri: str) -> str:
    from PIL import Image

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    base = re.sub(r"[^A-Za-z0-9_.-]", "_", Path(image_uri).stem)
    mask_path = RESULTS_DIR / f"{base}_mask.png"
    Image.fromarray((mask * 255).astype("uint8")).save(mask_path)
    return str(mask_path)


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup."""
    print("🚀 BlueGuard AI Service starting up...")
    _ensure_model_exists()


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "service": "BlueGuard AI Segmentation Service"}


@app.get("/health", tags=["health"])
async def health():
    model_ready = _checkpoint_available()
    return {
        "status": "healthy" if model_ready else "degraded",
        "model_loaded": model_ready,
        "checkpoint": CHECKPOINT_PATH,
    }


@app.post("/predict", response_model=PredictResponse, tags=["inference"])
async def predict_endpoint(request: PredictRequest):
    # Ensure model exists before predicting
    if not _checkpoint_available():
        print("Model not found, attempting to create...")
        if not _ensure_model_exists():
            raise HTTPException(
                status_code=503,
                detail=f"Model checkpoint not available at '{CHECKPOINT_PATH}'. "
                       "Failed to create mock model.",
            )

    image_path = _resolve_image(request.imageUri)

    try:
        result = predict(image_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {exc}")

    mask_uri = _mask_to_png(result["mask"], image_path) if result["polygons"] else None

    return PredictResponse(
        detected=bool(result["polygons"]),
        confidence=result["confidence"],
        maskUri=mask_uri,
        modelVersion=request.modelVersion,
        polygons=result["polygons"],
        numRegions=result["num_regions"],
    )
