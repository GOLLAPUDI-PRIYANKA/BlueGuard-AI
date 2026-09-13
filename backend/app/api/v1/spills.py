from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db
from app.schemas.common import SuccessResponse, ErrorResponse
from app.schemas.spill import DetectRequest
from app.schemas.analysis import AnalyzeRequest
from app.services.spill_service import SpillService
from app.services.analysis_service import AnalysisService
from app.repositories.forecast_repository import ForecastRepository
from app.repositories.impact_repository import ImpactRepository
from app.core.exceptions import SpillNotFoundError

router = APIRouter(prefix="/spills", tags=["spills"])


@router.post(
    "/detect",
    response_model=SuccessResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Upload/register satellite image for detection",
    description="Sends satellite imagery to the AI model for oil spill detection. Returns spill metadata if detected.",
)
async def detect_spill(request: DetectRequest, db: Session = Depends(get_db)):
    service = SpillService(db)
    result = await service.detect_spill(request)
    return SuccessResponse(data=result.model_dump(), message="Detection complete")


@router.get(
    "/{spill_id}",
    response_model=SuccessResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get complete spill metadata",
    description="Retrieves full metadata for a detected oil spill including area, severity, confidence, and centroid.",
)
async def get_spill(spill_id: str, db: Session = Depends(get_db)):
    service = SpillService(db)
    result = service.get_spill(spill_id)
    return SuccessResponse(data=result.model_dump())


@router.get(
    "/{spill_id}/nearby-vessels",
    response_model=SuccessResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Find vessels near spill/source area",
    description="Returns vessels within a configurable radius of the spill centroid, ordered by distance.",
)
async def get_nearby_vessels(spill_id: str, db: Session = Depends(get_db)):
    service = SpillService(db)
    result = service.get_nearby_vessels(spill_id)
    return SuccessResponse(data=result.model_dump())


@router.get(
    "/{spill_id}/origin",
    response_model=SuccessResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Estimate probable source region/time",
    description="Returns the estimated origin location and time for the spill based on GIS backtracking.",
)
async def get_origin(spill_id: str, db: Session = Depends(get_db)):
    service = SpillService(db)
    result = service.get_origin(spill_id)
    return SuccessResponse(data=result.model_dump())


@router.get(
    "/{spill_id}/suspects",
    response_model=SuccessResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Rank candidate vessels",
    description="Returns ranked suspect vessels with attribution scores and explainable evidence.",
)
async def get_suspects(spill_id: str, db: Session = Depends(get_db)):
    service = SpillService(db)
    result = service.get_suspects(spill_id)
    return SuccessResponse(data=result.model_dump())


@router.get(
    "/{spill_id}/forecast",
    response_model=SuccessResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Predict future drift",
    description="Returns 24/48/72-hour forecast predictions for spill drift and area expansion.",
)
async def get_forecast(spill_id: str, db: Session = Depends(get_db)):
    from geoalchemy2 import shape
    from shapely.geometry import mapping

    repo = ForecastRepository(db)
    preds = repo.get_by_spill_id(spill_id)
    if not preds:
        raise SpillNotFoundError(spill_id)

    forecast_entries = []
    for p in preds:
        geom = shape.to_shape(p.geometry)
        forecast_entries.append({
            "hours": int(p.forecast_hour),
            "areaSqKm": round(p.area_sq_km, 1),
            "geometry": mapping(geom),
        })

    from app.schemas.forecast import ForecastData
    data = ForecastData(spillId=spill_id, forecast=forecast_entries)
    return SuccessResponse(data=data.model_dump())


@router.get(
    "/{spill_id}/impact",
    response_model=SuccessResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Estimate environmental exposure",
    description="Returns risk levels for coastal, fishing, and environmental zones affected by the spill.",
)
async def get_impact(spill_id: str, db: Session = Depends(get_db)):
    repo = ImpactRepository(db)
    zones = repo.get_by_spill_id(spill_id)
    if not zones:
        raise SpillNotFoundError(spill_id)

    marine = next((z for z in zones if z.zone_type == "ENVIRONMENTAL"), None)
    fishing = next((z for z in zones if z.zone_type == "FISHING"), None)
    coastal = next((z for z in zones if z.zone_type == "COASTAL"), None)
    total_area = sum(z.affected_area_sq_km for z in zones)

    from app.schemas.impact import ImpactData
    data = ImpactData(
        marineRisk=marine.risk_level if marine else "LOW",
        fishingRisk=fishing.risk_level if fishing else "LOW",
        coastalRisk=coastal.risk_level if coastal else "LOW",
        affectedAreaSqKm=round(total_area, 1),
    )
    return SuccessResponse(data=data.model_dump())


@router.post(
    "/{spill_id}/analyze",
    response_model=SuccessResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Run complete investigation pipeline",
    description="Orchestrates the full analysis pipeline: backtracking, AIS correlation, attribution, forecast, and impact.",
)
async def analyze_spill(
    spill_id: str,
    request: Optional[AnalyzeRequest] = Body(default=None),
    db: Session = Depends(get_db),
):
    if request is None:
        request = AnalyzeRequest()
    service = AnalysisService(db)
    result = await service.analyze(spill_id, request)
    return SuccessResponse(data=result.model_dump(), message="Analysis complete")
