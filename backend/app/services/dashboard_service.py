from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.spill import Spill, SpillStatus, SpillSeverity
from app.models.suspect_score import SuspectScore
from app.schemas.impact import DashboardSummary


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self) -> DashboardSummary:
        total = self.db.query(func.count(Spill.spill_id)).scalar()
        active = (
            self.db.query(func.count(Spill.spill_id))
            .filter(Spill.status != SpillStatus.CLOSED)
            .scalar()
        )
        critical = (
            self.db.query(func.count(Spill.spill_id))
            .filter(Spill.severity == SpillSeverity.CRITICAL)
            .scalar()
        )
        vessels_under_investigation = (
            self.db.query(func.count(func.distinct(SuspectScore.vessel_id)))
            .join(Spill, Spill.spill_id == SuspectScore.spill_id)
            .filter(Spill.status != SpillStatus.CLOSED)
            .scalar()
        )

        return DashboardSummary(
            totalSpills=total,
            activeSpills=active,
            criticalSpills=critical,
            vesselsUnderInvestigation=vessels_under_investigation,
        )