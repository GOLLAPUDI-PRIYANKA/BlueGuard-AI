from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field, field_serializer


class UtcModel(BaseModel):
    @field_serializer("*", check_fields=False)
    def _serialize_datetime(self, value):
        if isinstance(value, datetime):
            return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        return value


class SuccessResponse(BaseModel):
    success: bool = True
    data: Any
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    errorCode: str
    message: str


class Coordinate(UtcModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")
