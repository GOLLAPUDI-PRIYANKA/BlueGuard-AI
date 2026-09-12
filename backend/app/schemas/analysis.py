from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.common import UtcModel


class AnalyzeRequest(BaseModel):
    includeForecast: bool = Field(default=True)
    includeImpact: bool = Field(default=True)
    aisHoursBefore: int = Field(default=12, ge=1, le=168)
    aisHoursAfter: int = Field(default=12, ge=1, le=168)


class AnalyzeResponseData(UtcModel):
    analysisId: str
    spillId: str
    status: str
    originConfidence: Optional[float] = None
    topSuspectVesselId: Optional[str] = None
