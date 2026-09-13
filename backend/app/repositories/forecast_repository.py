from typing import List
from sqlalchemy.orm import Session
from app.models.drift_prediction import DriftPrediction


class ForecastRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        prediction_id: str,
        spill_id: str,
        forecast_hour: float,
        latitude: float,
        longitude: float,
        geometry_wkt: str,
        uncertainty: float = None,
        area_sq_km: float = 0.0,
    ) -> DriftPrediction:
        pred = DriftPrediction(
            prediction_id=prediction_id,
            spill_id=spill_id,
            forecast_hour=forecast_hour,
            area_sq_km=area_sq_km,
            latitude=latitude,
            longitude=longitude,
            geometry=f"SRID=4326;{geometry_wkt}",
            uncertainty=uncertainty,
        )
        self.db.add(pred)
        self.db.flush()
        return pred

    def get_by_spill_id(self, spill_id: str) -> List[DriftPrediction]:
        return (
            self.db.query(DriftPrediction)
            .filter(DriftPrediction.spill_id == spill_id)
            .order_by(DriftPrediction.forecast_hour)
            .all()
        )

    def delete_by_spill_id(self, spill_id: str) -> bool:
        deleted = (
            self.db.query(DriftPrediction)
            .filter(DriftPrediction.spill_id == spill_id)
            .delete()
        )
        self.db.flush()
        return deleted > 0
