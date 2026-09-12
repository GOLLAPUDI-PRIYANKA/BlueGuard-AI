import random
from dataclasses import dataclass
from typing import List

from app.core.config import get_settings
from app.services.ais_client import CandidateVessel


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
    async def score_vessels(
        self,
        spill_id: str,
        candidates: List[CandidateVessel],
    ) -> AttributionResult:
        raise NotImplementedError("Real attribution client not yet implemented")


def build_attribution_client() -> AttributionClient:
    settings = get_settings()
    if settings.USE_MOCK_SERVICES:
        return MockAttributionClient()
    return RealAttributionClient()


class RealAttributionClient(AttributionClient):
    """Consumer of Member 3's embedded explainable evidence.

    Member 3's candidate service already computes spatial/temporal proximity,
    heading/route consistency and AIS continuity, plus an evidence score. This
    adapter maps that output onto the backend's suspect-score schema without
    re-simulating the attribution.
    """

    async def score_vessels(
        self,
        spill_id: str,
        candidates: List[CandidateVessel],
    ) -> AttributionResult:
        attributions = []
        for candidate in candidates:
            route_score = round(
                (candidate.heading_consistency + candidate.route_consistency) / 2.0, 3
            )
            attributions.append(
                VesselAttribution(
                    vessel_id=candidate.vessel_id,
                    score=round(candidate.evidence_percentage, 1),
                    spatial_score=candidate.spatial_proximity,
                    temporal_score=candidate.temporal_proximity,
                    route_score=route_score,
                    evidence={
                        "distanceKm": candidate.distance_km,
                        "timeDifferenceMin": candidate.time_difference_min,
                        "routeConsistency": candidate.route_consistency,
                        "aisContinuity": candidate.ais_continuity,
                        "headingConsistency": candidate.heading_consistency,
                        "spatialProximity": candidate.spatial_proximity,
                        "temporalProximity": candidate.temporal_proximity,
                        "investigationPriority": candidate.investigation_priority,
                    },
                )
            )
        attributions.sort(key=lambda a: a.score, reverse=True)
        return AttributionResult(attributions=attributions)


class MockAttributionClient(AttributionClient):
    async def score_vessels(
        self,
        spill_id: str,
        candidates: List[CandidateVessel],
    ) -> AttributionResult:
        attributions = []
        for i, candidate in enumerate(candidates):
            base_score = max(
                0.0, min(100.0, 100.0 - i * 25.0 + random.uniform(-5, 5))
            )
            spatial = round(random.uniform(0.5, 1.0), 2)
            temporal = round(random.uniform(0.4, 1.0), 2)
            route = round(random.uniform(0.3, 1.0), 2)

            attributions.append(
                VesselAttribution(
                    vessel_id=candidate.vessel_id,
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