from pydantic import BaseModel, Field
from app.schemas.common import UtcModel


class ImpactData(UtcModel):
    marineRisk: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    fishingRisk: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    coastalRisk: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    affectedAreaSqKm: float = Field(..., ge=0)


class DashboardSummary(UtcModel):
    totalSpills: int = Field(..., ge=0)
    activeSpills: int = Field(..., ge=0)
    criticalSpills: int = Field(..., ge=0)
    vesselsUnderInvestigation: int = Field(..., ge=0)


class ReportData(UtcModel):
    spillId: str
    reportStatus: str
    reportId: str
