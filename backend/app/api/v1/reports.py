from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.common import SuccessResponse, ErrorResponse
from app.schemas.impact import ReportData
from app.core.exceptions import SpillNotFoundError, ReportNotFoundError
from app.core.security import generate_id

router = APIRouter(tags=["reports"])


@router.get(
    "/spills/{spill_id}/report",
    response_model=SuccessResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Generate investigation report metadata / export",
    description="Returns report metadata and status for a completed spill analysis.",
)
async def get_report(spill_id: str, db: Session = Depends(get_db)):
    from app.repositories.spill_repository import SpillRepository
    from app.models.spill import SpillStatus

    repo = SpillRepository(db)
    spill = repo.get_by_id(spill_id)
    if not spill:
        raise SpillNotFoundError(spill_id)

    if spill.status != SpillStatus.ANALYSIS_COMPLETE:
        return SuccessResponse(
            data=ReportData(
                spillId=spill_id,
                reportStatus="PENDING",
                reportId="",
            ).model_dump(),
            message="Analysis not yet complete",
        )

    report_id = f"RPT-{spill_id}"
    data = ReportData(
        spillId=spill_id,
        reportStatus="READY",
        reportId=report_id,
    )
    return SuccessResponse(data=data.model_dump())
