import enum
from sqlalchemy import Column, String, Float, DateTime, Enum, Index
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base, utcnow


class SpillStatus(str, enum.Enum):
    DETECTED = "DETECTED"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"
    CLOSED = "CLOSED"


class SpillSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Spill(Base):
    __tablename__ = "spills"

    spill_id = Column(String(20), primary_key=True)
    detected_at = Column(DateTime(timezone=True), nullable=False)
    area_sq_km = Column(Float, nullable=False)
    severity = Column(Enum(SpillSeverity), nullable=False)
    confidence = Column(Float, nullable=False)
    centroid = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    geometry = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)
    status = Column(
        Enum(SpillStatus), nullable=False, default=SpillStatus.DETECTED
    )
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    detections = relationship("SpillDetection", back_populates="spill", cascade="all, delete-orphan")
    origin = relationship("SpillOrigin", back_populates="spill", uselist=False, cascade="all, delete-orphan")
    suspect_scores = relationship("SuspectScore", back_populates="spill", cascade="all, delete-orphan")
    drift_predictions = relationship("DriftPrediction", back_populates="spill", cascade="all, delete-orphan")
    impact_zones = relationship("ImpactZone", back_populates="spill", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_spill_centroid", "centroid", postgresql_using="gist"),
        Index("idx_spill_geometry", "geometry", postgresql_using="gist"),
        Index("idx_spill_status", "status"),
        Index("idx_spill_detected_at", "detected_at"),
    )
