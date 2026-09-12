from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from geoalchemy2 import shape, functions
from shapely.geometry import mapping
from app.models.spill import Spill, SpillStatus
from app.core.security import generate_id


class SpillRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        spill_id: str,
        detected_at,
        area_sq_km: float,
        severity: str,
        confidence: float,
        centroid_lon: float,
        centroid_lat: float,
        geometry_wkt: str,
        status: str = SpillStatus.DETECTED,
    ) -> Spill:
        spill = Spill(
            spill_id=spill_id,
            detected_at=detected_at,
            area_sq_km=area_sq_km,
            severity=severity,
            confidence=confidence,
            centroid=f"SRID=4326;POINT({centroid_lon} {centroid_lat})",
            geometry=f"SRID=4326;{geometry_wkt}",
            status=status,
        )
        self.db.add(spill)
        self.db.flush()
        return spill

    def get_by_id(self, spill_id: str) -> Optional[Spill]:
        return self.db.query(Spill).filter(Spill.spill_id == spill_id).first()

    def get_all(self) -> List[Spill]:
        return self.db.query(Spill).all()

    def update_status(self, spill_id: str, status: str) -> Optional[Spill]:
        spill = self.get_by_id(spill_id)
        if spill:
            spill.status = status
            self.db.flush()
        return spill

    def get_nearby_vessels(self, spill_id: str, radius_km: float = 50.0) -> list:
        from app.models.vessel import Vessel
        from app.models.vessel_position import VesselPosition

        spill = self.get_by_id(spill_id)
        if not spill:
            return []

        results = (
            self.db.query(Vessel, VesselPosition, functions.ST_DistanceSphere(
                VesselPosition.geometry, spill.centroid
            ).label("distance_m"))
            .join(VesselPosition, Vessel.vessel_id == VesselPosition.vessel_id)
            .filter(
                functions.ST_DWithin(
                    functions.ST_Transform(VesselPosition.geometry, 3857),
                    functions.ST_Transform(spill.centroid, 3857),
                    radius_km * 1000,
                )
            )
            .distinct(Vessel.vessel_id)
            .order_by(Vessel.vessel_id, "distance_m")
            .all()
        )
        return results

    def count_by_status(self, status: str) -> int:
        return self.db.query(Spill).filter(Spill.status == status).count()

    def count_all(self) -> int:
        return self.db.query(Spill).count()

    def delete(self, spill_id: str) -> bool:
        spill = self.get_by_id(spill_id)
        if spill:
            self.db.delete(spill)
            self.db.flush()
            return True
        return False
