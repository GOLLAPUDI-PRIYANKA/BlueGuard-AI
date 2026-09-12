from typing import List
from sqlalchemy.orm import Session
from app.models.impact_zone import ImpactZone


class ImpactRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        impact_id: str,
        spill_id: str,
        zone_type: str,
        risk_level: str,
        geometry_wkt: str,
        affected_area_sq_km: float,
    ) -> ImpactZone:
        zone = ImpactZone(
            id=impact_id,
            spill_id=spill_id,
            zone_type=zone_type,
            risk_level=risk_level,
            geometry=f"SRID=4326;{geometry_wkt}",
            affected_area_sq_km=affected_area_sq_km,
        )
        self.db.add(zone)
        self.db.flush()
        return zone

    def get_by_spill_id(self, spill_id: str) -> List[ImpactZone]:
        return (
            self.db.query(ImpactZone)
            .filter(ImpactZone.spill_id == spill_id)
            .all()
        )

    def delete_by_spill_id(self, spill_id: str) -> bool:
        deleted = (
            self.db.query(ImpactZone)
            .filter(ImpactZone.spill_id == spill_id)
            .delete()
        )
        self.db.flush()
        return deleted > 0
