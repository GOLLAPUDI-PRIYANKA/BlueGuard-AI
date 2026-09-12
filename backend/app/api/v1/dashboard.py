from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.common import SuccessResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "/summary",
    response_model=SuccessResponse,
    summary="Get dashboard KPIs",
    description="Returns summary statistics: total spills, active spills, critical spills, and vessels under investigation.",
)
async def get_summary(db: Session = Depends(get_db)):
    service = DashboardService(db)
    result = service.get_summary()
    return SuccessResponse(data=result.model_dump())
