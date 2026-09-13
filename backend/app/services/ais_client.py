import logging
import random
from dataclasses import dataclass, field
from typing import List, Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger("marineguard.ais")


@dataclass
class CandidateVessel:
    vessel_id: str
    mmsi: str
    name: str
    vessel_type: str
    flag_country: str
    distance_km: float
    time_difference_min: float
    route_consistency: float
    ais_continuity: float
    trajectory: List[dict] = field(default_factory=list)
    heading_consistency: float = 0.0
    spatial_proximity: float = 0.0
    temporal_proximity: float = 0.0
    evidence_score: float = 0.0
    evidence_percentage: float = 0.0
    investigation_priority: str = "Low"


@dataclass
class AISCandidateResult:
    candidates: List[CandidateVessel]


class AISClient:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url

    async def get_candidate_vessels(
        self,
        origin_lon: float,
        origin_lat: float,
        start_time: str,
        end_time: str,
        spatial_radius_km: float = 10.0,
        temporal_window_minutes: float = 60.0,
    ) -> AISCandidateResult:
        raise NotImplementedError("Real AIS client not yet implemented")


def build_ais_client() -> AISClient:
    settings = get_settings()
    if settings.USE_MOCK_SERVICES:
        return MockAISClient()
    return RealAISClient(base_url=settings.AIS_SERVICE_URL)


class RealAISClient(AISClient):
    """HTTP adapter for Member 3's AIS candidate service (POST /candidate-vessels).

    Member 3 keys candidates on MMSI and embeds the explainable attribution
    evidence in each candidate, so this adapter:
      - derives a stable backend `vesselId` from the MMSI,
      - keeps the raw evidence fields for the attribution layer,
      - records the closest position as the vessel trajectory entry.
    """

    def __init__(self, base_url: str = "http://localhost:8002", transport: Optional[httpx.AsyncBaseTransport] = None):
        super().__init__(base_url.rstrip("/"))
        self._transport = transport

    async def get_candidate_vessels(
        self,
        origin_lon: float,
        origin_lat: float,
        start_time: str,
        end_time: str,
        spatial_radius_km: float = 10.0,
        temporal_window_minutes: float = 60.0,
    ) -> AISCandidateResult:
        from app.core.exceptions import AppException, ErrorCode, ServiceUnavailableError

        payload = {
            "origin_polygon": [{"latitude": origin_lat, "longitude": origin_lon}],
            "spill_timestamp": start_time,
            "spatial_radius_km": spatial_radius_km,
            "temporal_window_minutes": temporal_window_minutes,
        }

        timeout = httpx.Timeout(30.0)
        try:
            async with httpx.AsyncClient(transport=self._transport, timeout=timeout) as http:
                response = await http.post(f"{self.base_url}/candidate-vessels", json=payload)
        except httpx.HTTPError:
            raise ServiceUnavailableError("AIS", ErrorCode.AIS_SERVICE_UNAVAILABLE)

        if response.status_code != 200:
            raise ServiceUnavailableError("AIS", ErrorCode.AIS_SERVICE_UNAVAILABLE)
        try:
            body = response.json()
        except ValueError:
            raise ServiceUnavailableError("AIS", ErrorCode.AIS_SERVICE_UNAVAILABLE)

        candidates = []
        for index, raw in enumerate(body.get("candidates") or []):
            try:
                candidates.append(self._map_candidate(raw))
            except (KeyError, TypeError, ValueError) as exc:
                logger.error(f"Invalid AIS candidate #{index}: {exc}")
                raise AppException(
                    ErrorCode.AIS_SERVICE_UNAVAILABLE,
                    f"AIS service returned an invalid candidate: {exc}",
                    status_code=502,
                )

        candidates.sort(key=lambda c: c.evidence_percentage, reverse=True)
        return AISCandidateResult(candidates=candidates)

    @staticmethod
    def _map_candidate(raw: dict) -> CandidateVessel:
        mmsi = int(raw["mmsi"])
        latitude = float(raw["latitude"])
        longitude = float(raw["longitude"])
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError(f"candidate coordinates out of range: {latitude}, {longitude}")

        def ratio(value, name, minimum=0.0, maximum=1.0) -> float:
            value = float(value)
            if not minimum <= value <= maximum:
                raise ValueError(f"{name} outside {minimum}..{maximum}: {value}")
            return value

        distance_km = float(raw["distanceKm"])
        time_difference_min = float(raw["timeDifferenceMin"])
        if distance_km < 0 or time_difference_min < 0:
            raise ValueError("candidate distance/time difference must be >= 0")

        route_consistency = ratio(raw["routeConsistency"], "routeConsistency")
        ais_continuity = ratio(raw["aisContinuity"], "aisContinuity")
        heading_consistency = ratio(raw["headingConsistency"], "headingConsistency")
        spatial_proximity = ratio(raw["spatialProximity"], "spatialProximity")
        temporal_proximity = ratio(raw["temporalProximity"], "temporalProximity")
        evidence_percentage = ratio(raw["evidencePercentage"], "evidencePercentage", 0.0, 100.0)

        vessel_id = f"VES{int(mmsi):09d}"
        timestamp = str(raw.get("timestamp") or "")

        return CandidateVessel(
            vessel_id=vessel_id,
            mmsi=str(mmsi),
            name=str(raw.get("vessel_type") or f"Vessel {mmsi}"),
            vessel_type=raw.get("vessel_type"),
            flag_country=None,
            distance_km=round(distance_km, 3),
            time_difference_min=round(time_difference_min, 1),
            route_consistency=route_consistency,
            ais_continuity=ais_continuity,
            heading_consistency=heading_consistency,
            spatial_proximity=spatial_proximity,
            temporal_proximity=temporal_proximity,
            evidence_score=float(raw.get("evidenceScore", 0.0)),
            evidence_percentage=evidence_percentage,
            investigation_priority=str(raw.get("investigationPriority") or "Low"),
            trajectory=[{"lat": latitude, "lon": longitude, "timestamp": timestamp}]
            if timestamp
            else [],
        )


class MockAISClient(AISClient):
    async def get_candidate_vessels(
        self,
        origin_lon: float,
        origin_lat: float,
        start_time: str,
        end_time: str,
        spatial_radius_km: float = 10.0,
        temporal_window_minutes: float = 60.0,
    ) -> AISCandidateResult:
        mock_vessels = [
            CandidateVessel(
                vessel_id="VES001",
                mmsi="419000123",
                name="Ocean Star",
                vessel_type="CARGO",
                flag_country="IN",
                distance_km=round(random.uniform(1.0, 5.0), 1),
                time_difference_min=round(random.uniform(5, 30), 0),
                route_consistency=round(random.uniform(0.7, 0.98), 2),
                ais_continuity=round(random.uniform(0.85, 1.0), 2),
                heading_consistency=round(random.uniform(0.7, 1.0), 2),
                spatial_proximity=round(random.uniform(0.7, 1.0), 2),
                temporal_proximity=round(random.uniform(0.7, 1.0), 2),
                evidence_percentage=round(random.uniform(70, 95), 1),
                evidence_score=round(random.uniform(0.70, 0.95), 3),
                investigation_priority="High",
                trajectory=[
                    {"lat": origin_lat - 0.1, "lon": origin_lon - 0.15, "timestamp": start_time},
                    {"lat": origin_lat - 0.05, "lon": origin_lon - 0.08, "timestamp": end_time},
                ],
            ),
            CandidateVessel(
                vessel_id="VES002",
                mmsi="419000456",
                name="Sea Queen",
                vessel_type="TANKER",
                flag_country="LK",
                distance_km=round(random.uniform(5.0, 15.0), 1),
                time_difference_min=round(random.uniform(30, 90), 0),
                route_consistency=round(random.uniform(0.4, 0.7), 2),
                ais_continuity=round(random.uniform(0.6, 0.9), 2),
                heading_consistency=round(random.uniform(0.4, 0.7), 2),
                spatial_proximity=round(random.uniform(0.4, 0.7), 2),
                temporal_proximity=round(random.uniform(0.5, 0.8), 2),
                evidence_percentage=round(random.uniform(45, 70), 1),
                evidence_score=round(random.uniform(0.45, 0.70), 3),
                investigation_priority="Medium",
                trajectory=[
                    {"lat": origin_lat - 0.2, "lon": origin_lon - 0.25, "timestamp": start_time},
                    {"lat": origin_lat - 0.15, "lon": origin_lon - 0.18, "timestamp": end_time},
                ],
            ),
            CandidateVessel(
                vessel_id="VES003",
                mmsi="419000789",
                name="Pacific Wanderer",
                vessel_type="BULK CARRIER",
                flag_country="PA",
                distance_km=round(random.uniform(10.0, 25.0), 1),
                time_difference_min=round(random.uniform(60, 180), 0),
                route_consistency=round(random.uniform(0.2, 0.5), 2),
                ais_continuity=round(random.uniform(0.3, 0.7), 2),
                heading_consistency=round(random.uniform(0.2, 0.5), 2),
                spatial_proximity=round(random.uniform(0.2, 0.5), 2),
                temporal_proximity=round(random.uniform(0.2, 0.6), 2),
                evidence_percentage=round(random.uniform(20, 45), 1),
                evidence_score=round(random.uniform(0.20, 0.45), 3),
                investigation_priority="Low",
                trajectory=[
                    {"lat": origin_lat - 0.3, "lon": origin_lon - 0.35, "timestamp": start_time},
                    {"lat": origin_lat - 0.25, "lon": origin_lon - 0.28, "timestamp": end_time},
                ],
            ),
        ]

        return AISCandidateResult(candidates=mock_vessels)