from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.vessel import Vessel


class VesselRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, vessel_id: str) -> Optional[Vessel]:
        return self.db.query(Vessel).filter(Vessel.vessel_id == vessel_id).first()

    def get_by_mmsi(self, mmsi: str) -> Optional[Vessel]:
        return self.db.query(Vessel).filter(Vessel.mmsi == mmsi).first()

    def create(
        self,
        vessel_id: str,
        mmsi: str = None,
        imo_number: str = None,
        name: str = "",
        vessel_type: str = None,
        flag_country: str = None,
    ) -> Vessel:
        vessel = Vessel(
            vessel_id=vessel_id,
            mmsi=mmsi,
            imo_number=imo_number,
            name=name,
            vessel_type=vessel_type,
            flag_country=flag_country,
        )
        self.db.add(vessel)
        self.db.flush()
        return vessel

    def upsert(
        self,
        vessel_id: str,
        mmsi: str = None,
        imo_number: str = None,
        name: str = "",
        vessel_type: str = None,
        flag_country: str = None,
    ) -> Vessel:
        vessel = self.get_by_id(vessel_id)
        if vessel:
            if mmsi:
                vessel.mmsi = mmsi
            if imo_number:
                vessel.imo_number = imo_number
            if name:
                vessel.name = name
            if vessel_type:
                vessel.vessel_type = vessel_type
            if flag_country:
                vessel.flag_country = flag_country
            self.db.flush()
            return vessel
        return self.create(vessel_id, mmsi, imo_number, name, vessel_type, flag_country)

    def get_all(self) -> List[Vessel]:
        return self.db.query(Vessel).all()
