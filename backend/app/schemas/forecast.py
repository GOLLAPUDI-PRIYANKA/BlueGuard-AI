from typing import Any, List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import UtcModel


class ForecastEntry(UtcModel):
    hours: int = Field(..., description="Forecast horizon in hours")
    areaSqKm: float = Field(..., ge=0)
    geometry: Any = Field(..., description="GeoJSON geometry")


class ForecastData(UtcModel):
    spillId: str
    forecast: List[ForecastEntry]
