from sqlalchemy import Column, String, Float, DateTime, Index
from geoalchemy2 import Geometry
from app.core.database import Base


class EnvironmentData(Base):
    __tablename__ = "environment_data"

    id = Column(String(20), primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    wind_u = Column(Float, nullable=True)
    wind_v = Column(Float, nullable=True)
    current_u = Column(Float, nullable=True)
    current_v = Column(Float, nullable=True)
    source = Column(String(100), nullable=True)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)

    __table_args__ = (
        Index("idx_env_timestamp", "timestamp"),
        Index("idx_env_geometry", "geometry", postgresql_using="gist"),
    )
