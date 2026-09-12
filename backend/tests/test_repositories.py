import pytest
from app.repositories.spill_repository import SpillRepository
from app.repositories.vessel_repository import VesselRepository
from app.repositories.detection_repository import DetectionRepository
from app.core.security import generate_id


def test_spill_repository_create_and_get(db_session):
    repo = SpillRepository(db_session)
    spill_id = "SP_TEST001"
    try:
        spill = repo.create(
            spill_id=spill_id,
            detected_at="2026-08-29T10:00:00Z",
            area_sq_km=18.6,
            severity="HIGH",
            confidence=0.94,
            centroid_lon=73.845,
            centroid_lat=15.462,
            geometry_wkt="MULTIPOLYGON (((73.8 15.4, 73.9 15.4, 73.9 15.5, 73.8 15.5, 73.8 15.4)))",
            status="DETECTED",
        )
        db_session.commit()
        assert spill.spill_id == spill_id
        assert spill.area_sq_km == 18.6

        fetched = repo.get_by_id(spill_id)
        assert fetched is not None
        assert fetched.severity == "HIGH"
    finally:
        repo.delete(spill_id)
        db_session.commit()


def test_vessel_repository_create_and_get_by_mmsi(db_session):
    repo = VesselRepository(db_session)
    vessel_id = "VES_TEST001"
    try:
        vessel = repo.create(
            vessel_id=vessel_id,
            mmsi="419000999",
            imo_number="IMO1234",
            name="Test Vessel",
            vessel_type="CARGO",
            flag_country="IN",
        )
        db_session.commit()
        assert vessel.vessel_id == vessel_id

        fetched = repo.get_by_mmsi("419000999")
        assert fetched is not None
        assert fetched.name == "Test Vessel"
    finally:
        db_session.query(type(vessel)).filter(type(vessel).vessel_id == vessel_id).delete()
        db_session.commit()


def test_detection_repository(db_session):
    spill_repo = SpillRepository(db_session)
    det_repo = DetectionRepository(db_session)

    spill_id = "SP_DET001"
    det_id = "DET_TEST001"
    try:
        spill_repo.create(
            spill_id=spill_id,
            detected_at="2026-08-29T10:00:00Z",
            area_sq_km=10.0,
            severity="MEDIUM",
            confidence=0.8,
            centroid_lon=73.0,
            centroid_lat=15.0,
            geometry_wkt="MULTIPOLYGON (((72.9 14.9, 73.1 14.9, 73.1 15.1, 72.9 15.1, 72.9 14.9)))",
        )
        det = det_repo.create(
            detection_id=det_id,
            spill_id=spill_id,
            image_source="SENTINEL_1",
            image_timestamp="2026-08-29T08:30:00Z",
            model_version="unet_v1",
            mask_uri="results/masks/SP_DET001.tif",
            prediction_confidence=0.8,
        )
        db_session.commit()

        fetched = det_repo.get_by_id(det_id)
        assert fetched is not None
        assert fetched.model_version == "unet_v1"
    finally:
        spill_repo.delete(spill_id)
        db_session.commit()