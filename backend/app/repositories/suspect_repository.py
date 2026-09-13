from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.suspect_score import SuspectScore


class SuspectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        score_id: str,
        spill_id: str,
        vessel_id: str,
        score: float,
        spatial_score: float,
        temporal_score: float,
        route_score: float,
        evidence_json: dict = None,
    ) -> SuspectScore:
        suspect = SuspectScore(
            score_id=score_id,
            spill_id=spill_id,
            vessel_id=vessel_id,
            score=score,
            spatial_score=spatial_score,
            temporal_score=temporal_score,
            route_score=route_score,
            evidence_json=evidence_json,
        )
        self.db.add(suspect)
        self.db.flush()
        return suspect

    def get_by_spill_id(self, spill_id: str) -> List[SuspectScore]:
        return (
            self.db.query(SuspectScore)
            .filter(SuspectScore.spill_id == spill_id)
            .order_by(SuspectScore.score.desc())
            .all()
        )

    def get_by_spill_and_vessel(
        self, spill_id: str, vessel_id: str
    ) -> Optional[SuspectScore]:
        return self.db.query(SuspectScore).filter(
            SuspectScore.spill_id == spill_id,
            SuspectScore.vessel_id == vessel_id,
        ).first()

    def delete_by_spill_id(self, spill_id: str) -> bool:
        deleted = (
            self.db.query(SuspectScore)
            .filter(SuspectScore.spill_id == spill_id)
            .delete()
        )
        self.db.flush()
        return deleted > 0

    def get_top_suspect(self, spill_id: str) -> Optional[SuspectScore]:
        return (
            self.db.query(SuspectScore)
            .filter(SuspectScore.spill_id == spill_id)
            .order_by(SuspectScore.score.desc())
            .first()
        )
