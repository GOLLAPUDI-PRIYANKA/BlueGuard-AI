from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.common import Coordinate, UtcModel
from app.models.spill import SpillSeverity, SpillStatus


class DetectRequest(BaseModel):
    imageUrl: str = Field(..., min_length=1, description="Image URI/path")
    source: str = Field(..., min_length=1, description="Image source e.g. SENTINEL_1")
    captureTime: datetime = Field(..., description="Image capture time in UTC")


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


class SuspectVessel(UtcModel):
    vesselId: str
    name: str
    score: float = Field(..., ge=0, le=100)
    evidence: SuspectEvidence


class SuspectsData(UtcModel):
    spillId: str
    suspects: List[SuspectVessel]
