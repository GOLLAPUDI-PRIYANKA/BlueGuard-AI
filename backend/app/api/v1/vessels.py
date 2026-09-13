from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.common import SuccessResponse, ErrorResponse
from app.services.vessel_service import VesselService
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/vessels", tags=["vessels"])


@router.get(
    "/{vessel_id}/trajectory",
    response_model=SuccessResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get vessel trajectory for a time range",
    description="Returns the historical trajectory of a vessel as a series of timestamped positions.",
)
async def get_trajectory(
    vessel_id: str,
    start_time: Optional[str] = Query(None, description="Start time ISO 8601"),
    end_time: Optional[str] = Query(None, description="End time ISO 8601"),
    db: Session = Depends(get_db),
):
    service = VesselService(db)
    st = datetime.fromisoformat(start_time.replace("Z", "+00:00")) if start_time else None
    et = datetime.fromisoformat(end_time.replace("Z", "+00:00")) if end_time else None
    result = service.get_trajectory(vessel_id, start_time=st, end_time=et)
    return SuccessResponse(data=result.model_dump())
