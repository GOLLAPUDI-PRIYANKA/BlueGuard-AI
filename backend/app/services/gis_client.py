import random
from dataclasses import dataclass


@dataclass
class BacktrackResult:
    origin_lon: float
    origin_lat: float
    estimated_time: str
    confidence: float
    geometry_wkt: str
    method: str


class GISClient:
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url

    async def backtrack(
        self,
        spill_geometry_wkt: str,
        centroid_lon: float,
        centroid_lat: float,
        detection_time: str,
    ) -> BacktrackResult:
        raise NotImplementedError("Real GIS client not yet implemented")


class MockGISClient(GISClient):
    async def backtrack(
        self,
        spill_geometry_wkt: str,
        centroid_lon: float,
        centroid_lat: float,
        detection_time: str,
    ) -> BacktrackResult:
        origin_lon = centroid_lon - random.uniform(0.1, 0.3)
        origin_lat = centroid_lat - random.uniform(0.1, 0.3)
        confidence = round(random.uniform(0.65, 0.90), 2)

        half = 0.02
        coords = [
            (origin_lon - half, origin_lat - half),
            (origin_lon + half, origin_lat - half),
            (origin_lon + half, origin_lat + half),
            (origin_lon - half, origin_lat + half),
            (origin_lon - half, origin_lat - half),
        ]
        coord_str = ", ".join(f"{lon} {lat}" for lon, lat in coords)
        geometry_wkt = f"MULTIPOLYGON ((({coord_str})))"

        return BacktrackResult(
            origin_lon=origin_lon,
            origin_lat=origin_lat,
            estimated_time="2026-08-28T23:40:00Z",
            confidence=confidence,
            geometry_wkt=geometry_wkt,
            method="advection_backtrack",
        )
