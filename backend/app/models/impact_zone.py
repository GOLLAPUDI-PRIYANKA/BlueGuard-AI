import enum
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base, utcnow


class ZoneType(str, enum.Enum):
    COASTAL = "COASTAL"
    FISHING = "FISHING"
    ENVIRONMENTAL = "ENVIRONMENTAL"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ImpactZone(Base):
    __tablename__ = "impact_zones"

    id = Column(String(20), primary_key=True)
    spill_id = Column(String(20), ForeignKey("spills.spill_id"), nullable=False)
    zone_type = Column(Enum(ZoneType), nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    geometry = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)
    affected_area_sq_km = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    spill = relationship("Spill", back_populates="impact_zones")

    __table_args__ = (
        Index("idx_impact_spill_id", "spill_id"),
        Index("idx_impact_geometry", "geometry", postgresql_using="gist"),
    )
