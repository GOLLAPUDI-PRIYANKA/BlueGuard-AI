from sqlalchemy import Column, String, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Vessel(Base):
    __tablename__ = "vessels"

    vessel_id = Column(String(20), primary_key=True)
    mmsi = Column(String(20), nullable=True)
    imo_number = Column(String(20), nullable=True)
    name = Column(String(200), nullable=False)
    vessel_type = Column(String(50), nullable=True)
    flag_country = Column(String(10), nullable=True)

    positions = relationship("VesselPosition", back_populates="vessel", cascade="all, delete-orphan")
    suspect_scores = relationship("SuspectScore", back_populates="vessel", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_vessel_mmsi", "mmsi"),
        Index("idx_vessel_imo", "imo_number"),
    )
