from typing import Optional
from sqlalchemy.orm import Session
from app.models.spill_origin import SpillOrigin


class OriginRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        origin_id: str,
        spill_id: str,
        estimated_time,
        geometry_wkt: str,
        confidence: float,
        method: str,
    ) -> SpillOrigin:
        origin = SpillOrigin(
            origin_id=origin_id,
            spill_id=spill_id,
            estimated_time=estimated_time,
            geometry=f"SRID=4326;{geometry_wkt}",
            confidence=confidence,
            method=method,
        )
        self.db.add(origin)
        self.db.flush()
        return origin

    def get_by_spill_id(self, spill_id: str) -> Optional[SpillOrigin]:
        return self.db.query(SpillOrigin).filter(
            SpillOrigin.spill_id == spill_id
        ).first()

    def get_by_id(self, origin_id: str) -> Optional[SpillOrigin]:
        return self.db.query(SpillOrigin).filter(
            SpillOrigin.origin_id == origin_id
        ).first()

    def delete_by_spill_id(self, spill_id: str) -> bool:
        origin = self.get_by_spill_id(spill_id)
        if origin:
            self.db.delete(origin)
            self.db.flush()
            return True
        return False
