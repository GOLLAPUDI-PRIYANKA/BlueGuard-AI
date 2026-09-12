import json

import httpx
import pytest
from app.services.ai_client import MockAIClient, RealAIClient
from app.services.gis_client import MockGISClient
from app.services.ais_client import MockAISClient
from app.services.attribution_client import MockAttributionClient
from app.services.forecast_client import MockForecastClient
from app.services.impact_client import MockImpactClient
from app.core.exceptions import ErrorCode, ServiceUnavailableError


@pytest.mark.asyncio
async def test_mock_ai_detection():
    client = MockAIClient()
    result = await client.detect("sentinel_scene_001.tif")
    assert result.detected in (True, False)
    assert 0 <= result.confidence <= 1
    assert result.area_sq_km >= 0
    assert result.geometry_wkt.startswith("MULTIPOLYGON")
    assert result.mask_uri.endswith(".tif")


def _ai_ok_handler(request: httpx.Request) -> httpx.Response:
    assert request.url.path == "/predict"
    body = json.loads(request.content)
    assert body["imageUri"] == "sentinel_scene_001.tif"
    assert body["modelVersion"] == "unet_v1"
    return httpx.Response(
        200,
        json={
            "detected": True,
            "confidence": 0.93,
            "maskUri": "results/masks/scene_001_mask.png",
            "modelVersion": "unet_v1",
            "polygons": [[[60, 100], [120, 90], [150, 140], [80, 160], [60, 100]]],
        },
    )


@pytest.mark.asyncio
async def test_real_ai_detection_happy_path():
    client = RealAIClient(
        base_url="http://ai-service:8001",
        transport=httpx.MockTransport(_ai_ok_handler),
    )
    result = await client.detect("sentinel_scene_001.tif", "unet_v1")
    assert result.detected is True
    assert result.confidence == pytest.approx(0.93)
    assert result.area_sq_km > 0
    assert result.severity in ("LOW", "MEDIUM", "HIGH")
    assert result.geometry_wkt.startswith("MULTIPOLYGON")
    assert result.centroid_lon == pytest.approx(73.845, abs=0.16)
    assert result.centroid_lat == pytest.approx(15.462, abs=0.16)
    assert result.mask_uri.endswith(".png")
    assert result.model_version == "unet_v1"


@pytest.mark.asyncio
async def test_real_ai_detection_no_oil():
    def _no_oil_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "detected": False,
                "confidence": 0.12,
                "maskUri": None,
                "modelVersion": "unet_v1",
                "polygons": [],
            },
        )

    client = RealAIClient(
        base_url="http://ai-service:8001",
        transport=httpx.MockTransport(_no_oil_handler),
    )
    result = await client.detect("sentinel_scene_001.tif")
    assert result.detected is False
    assert result.area_sq_km == 0.0
    assert result.severity == "LOW"
    assert result.confidence == pytest.approx(0.12)
    assert result.geometry_wkt.startswith("MULTIPOLYGON")


@pytest.mark.asyncio
async def test_real_ai_service_unavailable():
    def _down_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    client = RealAIClient(
        base_url="http://ai-service:8001",
        transport=httpx.MockTransport(_down_handler),
    )
    with pytest.raises(ServiceUnavailableError) as excinfo:
        await client.detect("sentinel_scene_001.tif")
    assert excinfo.value.error_code == ErrorCode.AI_SERVICE_UNAVAILABLE


@pytest.mark.asyncio
async def test_mock_gis_backtrack():
    client = MockGISClient()
    result = await client.backtrack(
        spill_geometry_wkt="MULTIPOLYGON (((73.8 15.4, 73.9 15.4, 73.9 15.5, 73.8 15.5, 73.8 15.4)))",
        centroid_lon=73.845,
        centroid_lat=15.462,
        detection_time="2026-08-29T10:00:00Z",
    )
    assert result.estimated_time.endswith("Z")
    assert 0 <= result.confidence <= 1
    assert result.geometry_wkt.startswith("MULTIPOLYGON")
    assert result.method == "advection_backtrack"


@pytest.mark.asyncio
async def test_mock_ais_candidates():
    client = MockAISClient()
    result = await client.get_candidate_vessels(
        origin_lon=73.5,
        origin_lat=15.2,
        start_time="2026-08-28T23:40:00Z",
        end_time="2026-08-29T08:30:00Z",
    )
    assert len(result.candidates) == 3
    for candidate in result.candidates:
        assert candidate.vessel_id.startswith("VES")
        assert candidate.distance_km > 0
        assert 0 <= candidate.route_consistency <= 1
        assert len(candidate.trajectory) >= 2


@pytest.mark.asyncio
async def test_mock_attribution():
    client = MockAttributionClient()
    result = await client.score_vessels(
        spill_id="SP101",
        origin_lon=73.5,
        origin_lat=15.2,
        origin_time="2026-08-28T23:40:00Z",
        candidate_vessel_ids=["VES001", "VES002", "VES003"],
    )
    assert len(result.attributions) == 3
    assert result.attributions[0].score >= result.attributions[1].score
    for attr in result.attributions:
        assert 0 <= attr.score <= 100
        assert "distanceKm" in attr.evidence


@pytest.mark.asyncio
async def test_mock_forecast():
    client = MockForecastClient()
    result = await client.forecast(
        spill_lon=73.845,
        spill_lat=15.462,
        spill_area_sq_km=18.6,
    )
    assert len(result.entries) == 3
    hours = [e.hours for e in result.entries]
    assert hours == [24, 48, 72]


@pytest.mark.asyncio
async def test_mock_impact():
    client = MockImpactClient()
    result = await client.assess_impact(
        spill_lon=73.845,
        spill_lat=15.462,
        spill_area_sq_km=18.6,
        spill_geometry_wkt="MULTIPOLYGON (((73.8 15.4, 73.9 15.4, 73.9 15.5, 73.8 15.5, 73.8 15.4)))",
    )
    assert result.marine_risk in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert result.affected_area_sq_km > 0
    assert len(result.zones) == 3