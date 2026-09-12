from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.vessel_repository import VesselRepository
from app.models.vessel_position import VesselPosition
from app.core.exceptions import VesselNotFoundError
from app.schemas.vessel import VesselTrajectoryData, TrajectoryPoint


class VesselService:
    def __init__(self, db: Session):
        self.db = db
        self.vessel_repo = VesselRepository(db)

    def get_trajectory(
        self,
        vessel_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> VesselTrajectoryData:
        vessel = self.vessel_repo.get_by_id(vessel_id)
        if not vessel:
            raise VesselNotFoundError(vessel_id)

        query = self.db.query(VesselPosition).filter(
            VesselPosition.vessel_id == vessel_id
        )
        if start_time:
            query = query.filter(VesselPosition.timestamp >= start_time)
        if end_time:
            query = query.filter(VesselPosition.timestamp <= end_time)

        positions = query.order_by(VesselPosition.timestamp).all()

        path = [
            TrajectoryPoint(
                lat=pos.latitude,
                lon=pos.longitude,
                timestamp=pos.timestamp,
            )
            for pos in positions
        ]

        return VesselTrajectoryData(vesselId=vessel_id, path=path)
