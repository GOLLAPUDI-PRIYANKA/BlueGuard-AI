from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base, utcnow


class DriftPrediction(Base):
    __tablename__ = "drift_predictions"

    prediction_id = Column(String(20), primary_key=True)
    spill_id = Column(String(20), ForeignKey("spills.spill_id"), nullable=False)
    forecast_hour = Column(Float, nullable=False)
    area_sq_km = Column(Float, nullable=False, default=0.0)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geometry = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)
    uncertainty = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    spill = relationship("Spill", back_populates="drift_predictions")

    __table_args__ = (
        Index("idx_forecast_spill_id", "spill_id"),
        Index("idx_forecast_geometry", "geometry", postgresql_using="gist"),
    )
