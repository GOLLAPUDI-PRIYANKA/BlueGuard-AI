import random
from dataclasses import dataclass
from typing import List


@dataclass
class VesselAttribution:
    vessel_id: str
    score: float
    spatial_score: float
    temporal_score: float
    route_score: float
    evidence: dict


@dataclass
class AttributionResult:
    attributions: List[VesselAttribution]


class AttributionClient:
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url

    async def score_vessels(
        self,
        spill_id: str,
        origin_lon: float,
        origin_lat: float,
        origin_time: str,
        candidate_vessel_ids: List[str],
    ) -> AttributionResult:
        raise NotImplementedError("Real attribution client not yet implemented")


class MockAttributionClient(AttributionClient):
    async def score_vessels(
        self,
        spill_id: str,
        origin_lon: float,
        origin_lat: float,
        origin_time: str,
        candidate_vessel_ids: List[str],
    ) -> AttributionResult:
        attributions = []
        for i, vid in enumerate(candidate_vessel_ids):
            base_score = max(0.0, min(100.0, 100.0 - i * 25.0 + random.uniform(-5, 5)))
            spatial = round(random.uniform(0.5, 1.0), 2)
            temporal = round(random.uniform(0.4, 1.0), 2)
            route = round(random.uniform(0.3, 1.0), 2)

            attributions.append(
                VesselAttribution(
                    vessel_id=vid,
                    score=round(base_score, 1),
                    spatial_score=spatial,
                    temporal_score=temporal,
                    route_score=route,
                    evidence={
                        "distanceKm": round(random.uniform(1.0, 20.0), 1),
                        "timeDifferenceMin": round(random.uniform(5, 120), 0),
                        "routeConsistency": route,
                        "aisContinuity": round(random.uniform(0.5, 1.0), 2),
                    },
                )
            )

        attributions.sort(key=lambda a: a.score, reverse=True)
        return AttributionResult(attributions=attributions)
