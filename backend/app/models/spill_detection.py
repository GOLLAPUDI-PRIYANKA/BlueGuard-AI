from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class SpillDetection(Base):
    __tablename__ = "spill_detections"

    detection_id = Column(String(20), primary_key=True)
    spill_id = Column(String(20), ForeignKey("spills.spill_id"), nullable=False)
    image_source = Column(String(50), nullable=False)
    image_timestamp = Column(DateTime(timezone=True), nullable=False)
    model_version = Column(String(50), nullable=False)
    mask_uri = Column(String(500), nullable=True)
    prediction_confidence = Column(Float, nullable=False)

    spill = relationship("Spill", back_populates="detections")

    __table_args__ = (
        Index("idx_detection_spill_id", "spill_id"),
        Index("idx_detection_image_timestamp", "image_timestamp"),
    )
