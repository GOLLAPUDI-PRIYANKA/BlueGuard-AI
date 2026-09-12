import random
from dataclasses import dataclass, field
from typing import List, Optional


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
    ) -> AISCandidateResult:
        raise NotImplementedError("Real AIS client not yet implemented")


class MockAISClient(AISClient):
    async def get_candidate_vessels(
        self,
        origin_lon: float,
        origin_lat: float,
        start_time: str,
        end_time: str,
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
                trajectory=[
                    {"lat": origin_lat - 0.3, "lon": origin_lon - 0.35, "timestamp": start_time},
                    {"lat": origin_lat - 0.25, "lon": origin_lon - 0.28, "timestamp": end_time},
                ],
            ),
        ]

        return AISCandidateResult(candidates=mock_vessels)
