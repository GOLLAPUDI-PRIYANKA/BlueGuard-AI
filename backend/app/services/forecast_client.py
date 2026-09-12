import random
from dataclasses import dataclass
from typing import List


@dataclass
class ForecastEntry:
    hours: int
    area_sq_km: float
    geometry_wkt: str
    center_lat: float
    center_lon: float
    uncertainty: float
    moored_area_sq_km: float = None


@dataclass
class ForecastResult:
    entries: List[ForecastEntry]


class ForecastClient:
    def __init__(self, base_url: str = "http://localhost:8005"):
        self.base_url = base_url

    async def forecast(
        self,
        spill_lon: float,
        spill_lat: float,
        spill_area_sq_km: float,
        current_wind_u: float = 0.0,
        current_wind_v: float = 0.0,
        current_current_u: float = 0.0,
        current_current_v: float = 0.0,
    ) -> ForecastResult:
        raise NotImplementedError("Real forecast client not yet implemented")


class MockForecastClient(ForecastClient):
    async def forecast(
        self,
        spill_lon: float,
        spill_lat: float,
        spill_area_sq_km: float,
        current_wind_u: float = 0.0,
        current_wind_v: float = 0.0,
        current_current_u: float = 0.0,
        current_current_v: float = 0.0,
    ) -> ForecastResult:
        entries = []
        drift_per_hour = 0.002
        for hours in [24, 48, 72]:
            factor = hours / 24.0
            area = round(spill_area_sq_km * (1 + 0.15 * factor) + random.uniform(-1, 1), 1)
            area = max(0.0, area)
            center_lon = spill_lon + drift_per_hour * hours
            center_lat = spill_lat + drift_per_hour * 0.5 * hours

            spread = 0.01 * factor
            half = spread
            coords = [
                (center_lon - half, center_lat - half),
                (center_lon + half, center_lat - half),
                (center_lon + half, center_lat + half),
                (center_lon - half, center_lat + half),
                (center_lon - half, center_lat - half),
            ]
            coord_str = ", ".join(f"{lon} {lat}" for lon, lat in coords)
            geometry_wkt = f"MULTIPOLYGON ((({coord_str})))"

            entries.append(
                ForecastEntry(
                    hours=hours,
                    area_sq_km=area,
                    geometry_wkt=geometry_wkt,
                    center_lat=center_lat,
                    center_lon=center_lon,
                    uncertainty=round(random.uniform(0.15, 0.35), 2),
                )
            )

        return ForecastResult(entries=entries)
