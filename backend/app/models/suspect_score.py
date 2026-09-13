from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base, utcnow


class SuspectScore(Base):
    __tablename__ = "suspect_scores"

    score_id = Column(String(20), primary_key=True)
    spill_id = Column(String(20), ForeignKey("spills.spill_id"), nullable=False)
    vessel_id = Column(String(20), ForeignKey("vessels.vessel_id"), nullable=False)
    score = Column(Float, nullable=False)
    spatial_score = Column(Float, nullable=False)
    temporal_score = Column(Float, nullable=False)
    route_score = Column(Float, nullable=False)
    evidence_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    spill = relationship("Spill", back_populates="suspect_scores")
    vessel = relationship("Vessel", back_populates="suspect_scores")

    __table_args__ = (
        Index("idx_suspect_spill_id", "spill_id"),
        Index("idx_suspect_vessel_id", "vessel_id"),
        Index("idx_suspect_score", "score"),
    )
