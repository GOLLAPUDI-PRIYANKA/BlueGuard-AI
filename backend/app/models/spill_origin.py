from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base, utcnow


class SpillOrigin(Base):
    __tablename__ = "spill_origins"

    origin_id = Column(String(20), primary_key=True)
    spill_id = Column(String(20), ForeignKey("spills.spill_id"), nullable=False, unique=True)
    estimated_time = Column(DateTime(timezone=True), nullable=False)
    geometry = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)
    confidence = Column(Float, nullable=False)
    method = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    spill = relationship("Spill", back_populates="origin")

    __table_args__ = (
        Index("idx_origin_spill_id", "spill_id"),
        Index("idx_origin_geometry", "geometry", postgresql_using="gist"),
    )
