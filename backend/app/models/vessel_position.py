from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base


class VesselPosition(Base):
    __tablename__ = "vessel_positions"

    position_id = Column(String(20), primary_key=True)
    vessel_id = Column(String(20), ForeignKey("vessels.vessel_id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, nullable=True)
    course = Column(Float, nullable=True)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)

    vessel = relationship("Vessel", back_populates="positions")

    __table_args__ = (
        Index("idx_vpos_vessel_id", "vessel_id"),
        Index("idx_vpos_timestamp", "timestamp"),
        Index("idx_vpos_geometry", "geometry", postgresql_using="gist"),
        Index("idx_vpos_vessel_time", "vessel_id", "timestamp"),
    )
