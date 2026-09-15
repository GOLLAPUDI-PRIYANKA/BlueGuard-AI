from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, Field
from app.schemas.common import Coordinate, UtcModel
from app.models.spill import SpillSeverity, SpillStatus


class DetectRequest(BaseModel):
    imageUrl: str = Field(..., min_length=1, description="Image URI/path")
    source: str = Field(..., min_length=1, description="Image source e.g. SENTINEL_1")
    captureTime: datetime = Field(..., description="Image capture time in UTC")
    imageBounds: Optional[List[List[float]]] = Field(
        default=None,
        description="Optional georeferencing bounds [[south, west], [north, east]] to convert model pixel polygons to WGS84",
    )


class DetectResponseData(UtcModel):
    spillId: str
    detected: bool
    confidence: float = Field(..., ge=0, le=1)
    areaSqKm: float = Field(..., ge=0)
    severity: SpillSeverity
    centroid: Coordinate


class SpillDetail(UtcModel):
    spillId: str
    status: SpillStatus
    areaSqKm: float = Field(..., ge=0)
    severity: SpillSeverity
    confidence: float = Field(..., ge=0, le=1)
    detectedAt: datetime
    centroid: Coordinate


class NearbyVessel(UtcModel):
    vesselId: str
    name: str
    distanceKm: float = Field(..., ge=0)


class NearbyVesselsData(UtcModel):
    spillId: str
    vessels: List[NearbyVessel]


class OriginPoint(UtcModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class SpillOriginData(UtcModel):
    spillId: str
    estimatedOrigin: OriginPoint
    estimatedTime: datetime
    confidence: float = Field(..., ge=0, le=1)


class SuspectEvidence(UtcModel):
    distanceKm: float = Field(..., ge=0)
    timeDifferenceMin: float
    routeConsistency: float = Field(..., ge=0, le=1)
    aisContinuity: float = Field(..., ge=0, le=1)
    headingConsistency: Optional[float] = Field(None, ge=0, le=1)
    spatialProximity: Optional[float] = Field(None, ge=0, le=1)
    temporalProximity: Optional[float] = Field(None, ge=0, le=1)
    investigationPriority: Optional[str] = None


class TrajectoryPoint(UtcModel):
    lat: float
    lon: float
    timestamp: Optional[Any] = None


class SuspectVessel(UtcModel):
    vesselId: str
    name: str
    mmsi: Optional[str] = None
    vesselType: Optional[str] = None
    flagCountry: Optional[str] = None
    score: float = Field(..., ge=0, le=100)
    evidence: SuspectEvidence
    trajectory: List[TrajectoryPoint] = Field(default_factory=list)


class SuspectsData(UtcModel):
    spillId: str
    suspects: List[SuspectVessel]
