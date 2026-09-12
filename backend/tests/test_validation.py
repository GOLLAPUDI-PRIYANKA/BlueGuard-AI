import pytest
from app.schemas.spill import (
    Coordinate,
    DetectRequest,
    DetectResponseData,
    SpillDetail,
    NearbyVesselsData,
    SuspectsData,
)
from app.schemas.analysis import AnalyzeRequest
from app.schemas.vessel import VesselTrajectoryData
from pydantic import ValidationError
from datetime import datetime


def test_coordinate_valid():
    c = Coordinate(lat=15.462, lon=73.845)
    assert c.lat == 15.462
    assert c.lon == 73.845


def test_coordinate_invalid_lat():
    with pytest.raises(ValidationError):
        Coordinate(lat=91.0, lon=73.845)


def test_coordinate_invalid_lon():
    with pytest.raises(ValidationError):
        Coordinate(lat=15.462, lon=-181.0)


def test_detect_request_valid():
    req = DetectRequest(
        imageUrl="scene.tif",
        source="SENTINEL_1",
        captureTime="2026-08-29T08:30:00Z",
    )
    assert req.source == "SENTINEL_1"


def test_detect_request_invalid_time():
    with pytest.raises(ValidationError):
        DetectRequest(
            imageUrl="scene.tif",
            source="SENTINEL_1",
            captureTime="not-valid",
        )


def test_analyze_request_defaults():
    req = AnalyzeRequest()
    assert req.includeForecast is True
    assert req.includeImpact is True
    assert req.aisHoursBefore == 12


def test_analyze_request_invalid_hours():
    with pytest.raises(ValidationError):
        AnalyzeRequest(aisHoursBefore=0)


def test_confidence_bounds():
    with pytest.raises(ValidationError):
        DetectResponseData(
            spillId="SP101",
            detected=True,
            confidence=1.5,
            areaSqKm=10.0,
            severity="HIGH",
            centroid=Coordinate(lat=15.0, lon=73.0),
        )


def test_area_non_negative():
    with pytest.raises(ValidationError):
        DetectResponseData(
            spillId="SP101",
            detected=True,
            confidence=0.9,
            areaSqKm=-5.0,
            severity="HIGH",
            centroid=Coordinate(lat=15.0, lon=73.0),
        )