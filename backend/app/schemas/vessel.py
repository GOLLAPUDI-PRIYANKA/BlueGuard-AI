from datetime import datetime
from typing import List
from app.schemas.common import UtcModel


class TrajectoryPoint(UtcModel):
    lat: float
    lon: float
    timestamp: datetime


class VesselTrajectoryData(UtcModel):
    vesselId: str
    path: List[TrajectoryPoint]
