import json

import httpx
import pytest
from app.services.ai_client import MockAIClient, RealAIClient
from app.services.gis_client import MockGISClient, RealGISClient
from app.services.ais_client import CandidateVessel, MockAISClient, RealAISClient
from app.services.attribution_client import MockAttributionClient, RealAttributionClient
from app.services.forecast_client import MockForecastClient
from app.services.impact_client import MockImpactClient
from app.core.exceptions import AppException, ErrorCode, ServiceUnavailableError


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
async def test_real_ai_detection_accepts_image_bounds():
    client = RealAIClient(
        base_url="http://ai-service:8001",
        transport=httpx.MockTransport(_ai_ok_handler),
    )
    result = await client.detect(
        "sentinel_scene_001.tif",
        model_version="unet_v1",
        image_bounds=[[14.0, 72.0], [16.0, 75.0]],
    )
    assert result.detected is True
    assert 14.0 <= result.centroid_lat <= 16.0
    assert 72.0 <= result.centroid_lon <= 75.0
    assert result.geometry_wkt.startswith("MULTIPOLYGON")


@pytest.mark.asyncio
async def test_real_ai_invalid_confidence_raises_model_error():
    def _bad_confidence_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "detected": True,
                "confidence": 1.5,
                "maskUri": "results/masks/scene_001_mask.png",
                "modelVersion": "unet_v1",
                "polygons": [[[60, 100], [120, 90], [150, 140], [80, 160], [60, 100]]],
            },
        )

    client = RealAIClient(
        base_url="http://ai-service:8001",
        transport=httpx.MockTransport(_bad_confidence_handler),
    )
    with pytest.raises(AppException) as excinfo:
        await client.detect("sentinel_scene_001.tif")
    assert excinfo.value.error_code == ErrorCode.MODEL_INFERENCE_FAILED


@pytest.mark.asyncio
async def test_real_ai_invalid_polygon_raises_model_error():
    def _bad_polygon_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "detected": True,
                "confidence": 0.93,
                "maskUri": "results/masks/scene_001_mask.png",
                "modelVersion": "unet_v1",
                "polygons": [[[60, 100], [300, 400], [150, 140], [80, 160], [60, 100]]],
            },
        )

    client = RealAIClient(
        base_url="http://ai-service:8001",
        transport=httpx.MockTransport(_bad_polygon_handler),
    )
    with pytest.raises(AppException) as excinfo:
        await client.detect("sentinel_scene_001.tif")
    assert excinfo.value.error_code == ErrorCode.MODEL_INFERENCE_FAILED


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
    candidates = [
        CandidateVessel(
            vessel_id="VES001", mmsi="419000123", name="Ocean Star",
            vessel_type="CARGO", flag_country="IN", distance_km=1.0,
            time_difference_min=10.0, route_consistency=0.9, ais_continuity=1.0,
        ),
        CandidateVessel(
            vessel_id="VES002", mmsi="419000456", name="Sea Queen",
            vessel_type="TANKER", flag_country="LK", distance_km=8.0,
            time_difference_min=40.0, route_consistency=0.5, ais_continuity=0.8,
        ),
        CandidateVessel(
            vessel_id="VES003", mmsi="419000789", name="Pacific Wanderer",
            vessel_type="BULK CARRIER", flag_country="PA", distance_km=20.0,
            time_difference_min=100.0, route_consistency=0.3, ais_continuity=0.5,
        ),
    ]
    result = await client.score_vessels(spill_id="SP101", candidates=candidates)
    assert len(result.attributions) == 3
    assert result.attributions[0].score >= result.attributions[1].score
    for attr in result.attributions:
        assert 0 <= attr.score <= 100
        assert "distanceKm" in attr.evidence


@pytest.mark.asyncio
async def test_real_attribution_maps_member3_evidence():
    client = RealAttributionClient()
    candidates = [
        CandidateVessel(
            vessel_id="VES123456789", mmsi="123456789", name="Vessel 123456789",
            vessel_type="Cargo", flag_country=None, distance_km=0.5,
            time_difference_min=5.0, route_consistency=0.8, ais_continuity=1.0,
            heading_consistency=0.9, spatial_proximity=0.95, temporal_proximity=0.92,
            evidence_score=0.87, evidence_percentage=87.2, investigation_priority="High",
        ),
        CandidateVessel(
            vessel_id="VES555555555", mmsi="555555555", name="Vessel 555555555",
            vessel_type="Fishing", flag_country=None, distance_km=9.0,
            time_difference_min=55.0, route_consistency=0.2, ais_continuity=0.3,
            heading_consistency=0.1, spatial_proximity=0.10, temporal_proximity=0.08,
            evidence_score=0.2, evidence_percentage=20.0, investigation_priority="Low",
        ),
    ]
    result = await client.score_vessels(spill_id="SP101", candidates=candidates)
    assert len(result.attributions) == 2
    assert result.attributions[0].vessel_id == "VES123456789"
    assert result.attributions[0].score == pytest.approx(87.2)
    assert result.attributions[0].spatial_score == pytest.approx(0.95)
    assert result.attributions[0].temporal_score == pytest.approx(0.92)
    assert result.attributions[0].route_score == pytest.approx(0.85)
    assert result.attributions[0].evidence["investigationPriority"] == "High"


@pytest.mark.asyncio
async def test_real_ais_candidates():
    def _handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/candidate-vessels"
        body = json.loads(request.content)
        assert body["origin_polygon"][0]["latitude"] == 15.2
        assert body["spill_timestamp"] == "2026-08-28T23:40:00Z"
        return httpx.Response(
            200,
            json={
                "candidate_count": 2,
                "candidates": [
                    {
                        "candidateRank": 1, "mmsi": 123456789, "imo_number": "IMO9000001",
                        "vessel_type": "Cargo", "latitude": 15.201, "longitude": 73.512,
                        "timestamp": "2026-08-28T23:40:00Z", "distanceKm": 0.05,
                        "timeDifferenceMin": 0.0, "headingConsistency": 0.99,
                        "routeConsistency": 0.8, "aisContinuity": 1.0,
                        "spatialProximity": 0.99, "temporalProximity": 1.0,
                        "evidenceScore": 0.9, "evidencePercentage": 90.0,
                        "investigationPriority": "High",
                    },
                    {
                        "candidateRank": 2, "mmsi": 987654321, "imo_number": "IMO9000002",
                        "vessel_type": "Tanker", "latitude": 15.26, "longitude": 73.6,
                        "timestamp": "2026-08-28T22:50:00Z", "distanceKm": 9.8,
                        "timeDifferenceMin": 50.0, "headingConsistency": 0.3,
                        "routeConsistency": 0.4, "aisContinuity": 0.6,
                        "spatialProximity": 0.02, "temporalProximity": 0.17,
                        "evidenceScore": 0.3, "evidencePercentage": 30.0,
                        "investigationPriority": "Low",
                    },
                ],
            },
        )

    client = RealAISClient(
        base_url="http://ais-service:8002",
        transport=httpx.MockTransport(_handler),
    )
    result = await client.get_candidate_vessels(
        origin_lon=73.512, origin_lat=15.2, start_time="2026-08-28T23:40:00Z",
        end_time="2026-08-29T08:30:00Z",
    )
    assert len(result.candidates) == 2
    assert result.candidates[0].vessel_id == "VES123456789"
    assert result.candidates[0].mmsi == "123456789"
    assert result.candidates[0].evidence_percentage == pytest.approx(90.0)
    assert result.candidates[0].trajectory[0]["lat"] == pytest.approx(15.201)
    assert result.candidates[1].vessel_id == "VES987654321"


@pytest.mark.asyncio
async def test_real_ais_invalid_candidate_rejected():
    def _handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "candidate_count": 1,
                "candidates": [
                    {
                        "candidateRank": 1, "mmsi": 123456789,
                        "latitude": 150.0, "longitude": 73.5,
                        "timestamp": "2026-08-28T23:40:00Z", "distanceKm": 1.0,
                        "timeDifferenceMin": 0.0, "headingConsistency": 1.0,
                        "routeConsistency": 1.0, "aisContinuity": 1.0,
                        "spatialProximity": 1.0, "temporalProximity": 1.0,
                        "evidenceScore": 1.0, "evidencePercentage": 100.0,
                        "investigationPriority": "High",
                    }
                ],
            },
        )

    client = RealAISClient(
        base_url="http://ais-service:8002",
        transport=httpx.MockTransport(_handler),
    )
    with pytest.raises(AppException) as excinfo:
        await client.get_candidate_vessels(
            origin_lon=73.5, origin_lat=15.2, start_time="2026-08-28T23:40:00Z",
            end_time="2026-08-29T08:30:00Z",
        )
    assert excinfo.value.error_code == ErrorCode.AIS_SERVICE_UNAVAILABLE


@pytest.mark.asyncio
async def test_real_gis_backtrack():
    def _handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/backtrack"
        return httpx.Response(
            200,
            json={
                "origin_lat": 15.201, "origin_lon": 73.512,
                "origin_time": "2026-08-28T23:40:00Z", "confidence": 0.81,
                "uncertainty_km": 12.0, "hours_back": 10.33,
                "model": "baseline_advection_demo_reference",
            },
        )

    client = RealGISClient(
        base_url="http://gis-service:5001",
        transport=httpx.MockTransport(_handler),
    )
    result = await client.backtrack(
        spill_geometry_wkt="MULTIPOLYGON (((73.8 15.4, 73.9 15.4, 73.9 15.5, 73.8 15.5, 73.8 15.4)))",
        centroid_lon=73.845, centroid_lat=15.462, detection_time="2026-08-29T10:00:00Z",
    )
    assert result.origin_lat == pytest.approx(15.201)
    assert result.origin_lon == pytest.approx(73.512)
    assert result.estimated_time == "2026-08-28T23:40:00Z"
    assert result.confidence == pytest.approx(0.81)
    assert result.geometry_wkt.startswith("MULTIPOLYGON")
    assert result.method == "baseline_advection_demo_reference"


@pytest.mark.asyncio
async def test_real_gis_forecast():
    def _handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/forecast"
        return httpx.Response(
            200,
            json={
                "forecast_points": [
                    {"hours": 24, "time": "2026-08-30T00:00:00Z", "lat": 15.58,
                     "lon": 74.12, "area_km2": 22.4, "confidence": 0.68, "uncertainty_km": 20.0},
                    {"hours": 48, "time": "2026-08-31T00:00:00Z", "lat": 15.89,
                     "lon": 74.45, "area_km2": 31.7, "confidence": 0.68, "uncertainty_km": 20.0},
                    {"hours": 72, "time": "2026-09-01T00:00:00Z", "lat": 16.12,
                     "lon": 74.78, "area_km2": 43.2, "confidence": 0.68, "uncertainty_km": 20.0},
                ],
                "confidence": 0.68, "uncertainty_km": 20.0,
                "model": "baseline_advection_demo_reference",
            },
        )

    client = RealGISClient(
        base_url="http://gis-service:5001",
        transport=httpx.MockTransport(_handler),
    )
    result = await client.forecast(
        spill_lon=73.512, spill_lat=15.201, spill_area_sq_km=0.0,
        origin_time="2026-08-28T23:40:00Z", hours_forward=72,
    )
    assert len(result.entries) == 3
    assert [e.hours for e in result.entries] == [24, 48, 72]
    assert result.entries[0].center_lat == pytest.approx(15.58)
    assert result.entries[0].area_sq_km == pytest.approx(22.4)
    assert result.entries[2].geometry_wkt.startswith("MULTIPOLYGON")


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