import random
from dataclasses import dataclass
from typing import List


@dataclass
class ImpactZoneResult:
    zone_type: str
    risk_level: str
    geometry_wkt: str
    affected_area_sq_km: float


@dataclass
class ImpactResult:
    marine_risk: str
    fishing_risk: str
    coastal_risk: str
    affected_area_sq_km: float
    zones: List[ImpactZoneResult]


class ImpactClient:
    def __init__(self, base_url: str = "http://localhost:8006"):
        self.base_url = base_url

    async def assess_impact(
        self,
        spill_lon: float,
        spill_lat: float,
        spill_area_sq_km: float,
        spill_geometry_wkt: str,
    ) -> ImpactResult:
        raise NotImplementedError("Real impact client not yet implemented")


class MockImpactClient(ImpactClient):
    async def assess_impact(
        self,
        spill_lon: float,
        spill_lat: float,
        spill_area_sq_km: float,
        spill_geometry_wkt: str,
    ) -> ImpactResult:
        risks = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        marine_risk = random.choice(risks[1:])
        fishing_risk = random.choice(risks[:3])
        coastal_risk = random.choice(risks[1:])
        affected = round(spill_area_sq_km * random.uniform(1.2, 2.0), 1)

        zones = [
            ImpactZoneResult(
                zone_type="COASTAL",
                risk_level=coastal_risk,
                geometry_wkt=spill_geometry_wkt,
                affected_area_sq_km=round(affected * 0.4, 1),
            ),
            ImpactZoneResult(
                zone_type="FISHING",
                risk_level=fishing_risk,
                geometry_wkt=spill_geometry_wkt,
                affected_area_sq_km=round(affected * 0.35, 1),
            ),
            ImpactZoneResult(
                zone_type="ENVIRONMENTAL",
                risk_level=marine_risk,
                geometry_wkt=spill_geometry_wkt,
                affected_area_sq_km=round(affected * 0.25, 1),
            ),
        ]

        return ImpactResult(
            marine_risk=marine_risk,
            fishing_risk=fishing_risk,
            coastal_risk=coastal_risk,
            affected_area_sq_km=affected,
            zones=zones,
        )
