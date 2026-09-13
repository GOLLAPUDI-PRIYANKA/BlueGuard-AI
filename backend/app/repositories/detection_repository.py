from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.spill_detection import SpillDetection


class DetectionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        detection_id: str,
        spill_id: str,
        image_source: str,
        image_timestamp,
        model_version: str,
        mask_uri: str = None,
        prediction_confidence: float = 0.0,
    ) -> SpillDetection:
        detection = SpillDetection(
            detection_id=detection_id,
            spill_id=spill_id,
            image_source=image_source,
            image_timestamp=image_timestamp,
            model_version=model_version,
            mask_uri=mask_uri,
            prediction_confidence=prediction_confidence,
        )
        self.db.add(detection)
        self.db.flush()
        return detection

    def get_by_id(self, detection_id: str) -> Optional[SpillDetection]:
        return self.db.query(SpillDetection).filter(
            SpillDetection.detection_id == detection_id
        ).first()

    def get_by_spill_id(self, spill_id: str) -> List[SpillDetection]:
        return self.db.query(SpillDetection).filter(
            SpillDetection.spill_id == spill_id
        ).all()

    def get_latest_for_spill(self, spill_id: str) -> Optional[SpillDetection]:
        return (
            self.db.query(SpillDetection)
            .filter(SpillDetection.spill_id == spill_id)
            .order_by(SpillDetection.image_timestamp.desc())
            .first()
        )
