import logging
import math
import random
from dataclasses import dataclass
from typing import Optional

import httpx
from shapely.geometry import Polygon

from app.core.config import get_settings
from app.services.forecast_client import ForecastEntry, ForecastResult

logger = logging.getLogger("marineguard.gis")


@dataclass
class BacktrackResult:
    origin_lon: float
    origin_lat: float
    estimated_time: str
    confidence: float
    geometry_wkt: str
    method: str


class GISClient:
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url

    async def backtrack(
        self,
        spill_geometry_wkt: str,
        centroid_lon: float,
        centroid_lat: float,
        detection_time: str,
    ) -> BacktrackResult:
        raise NotImplementedError("Real GIS client not yet implemented")

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


def build_gis_client() -> GISClient:
    settings = get_settings()
    if settings.USE_MOCK_SERVICES:
        return MockGISClient()
    return RealGISClient(base_url=settings.GIS_SERVICE_URL)


KM_PER_DEG_LAT = 111.32


def _uncertainty_polygon_wkt(lat: float, lon: float, uncertainty_km: float) -> str:
    """Build a MULTIPOLYGON WKT circle of radius uncertainty_km (WGS84, EPSG:4326)."""
    radius_deg = max(uncertainty_km, 0.5) / KM_PER_DEG_LAT
    cos_lat = max(0.1, abs(math.cos(math.radians(lat))))
    poly = _circle_points(lat, lon, radius_deg, cos_lat)
    exterior = list(poly.exterior.coords)
    coord_str = ", ".join(f"{x} {y}" for x, y in exterior)
    return f"MULTIPOLYGON ((({coord_str})))"


def _circle_points(lat: float, lon: float, radius_deg: float, cos_lat: float) -> Polygon:
    points = []
    for i in range(48):
        angle = 2 * math.pi * i / 48
        d_lat = radius_deg * math.sin(angle)
        d_lon = radius_deg * math.cos(angle) / cos_lat
        points.append((lon + d_lon, lat + d_lat))
    return Polygon(points)


class RealGISClient(GISClient):
    """HTTP adapter for Member 4's Flask GIS service (POST /backtrack, /forecast).

    Drift results arrive as WGS84 points + uncertainty; this adapter builds the
    required MULTIPOLYGON geometries from the uncertainty radius and validates
    every field before it is persisted.
    """

    def __init__(self, base_url: str = "http://localhost:5001", transport: Optional[httpx.AsyncBaseTransport] = None):
        super().__init__(base_url.rstrip("/"))
        self._transport = transport

    async def _post(self, path: str, payload: dict) -> dict:
        from app.core.exceptions import ErrorCode, ServiceUnavailableError
        timeout = httpx.Timeout(30.0)
        try:
            async with httpx.AsyncClient(transport=self._transport, timeout=timeout) as http:
                response = await http.post(f"{self.base_url}{path}", json=payload)
        except httpx.HTTPError:
            raise ServiceUnavailableError("GIS", ErrorCode.GIS_SERVICE_UNAVAILABLE)
        if response.status_code != 200:
            raise ServiceUnavailableError("GIS", ErrorCode.GIS_SERVICE_UNAVAILABLE)
        try:
            return response.json()
        except ValueError:
            raise ServiceUnavailableError("GIS", ErrorCode.GIS_SERVICE_UNAVAILABLE)

    @staticmethod
    def _validate_lat_lon(lat: float, lon: float) -> tuple[float, float]:
        lat, lon = float(lat), float(lon)
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError(f"coordinates out of range: {lat}, {lon}")
        return lat, lon

    async def backtrack(
        self,
        spill_geometry_wkt: str,
        centroid_lon: float,
        centroid_lat: float,
        detection_time: str,
        hours_back: Optional[float] = None,
        scenario: Optional[str] = None,
    ) -> BacktrackResult:
        from datetime import datetime, timezone
        from app.core.exceptions import AppException, ErrorCode, ServiceUnavailableError

        payload = {
            "detected_lat": centroid_lat,
            "detected_lon": centroid_lon,
            "detected_time": detection_time,
            "scenario": scenario or "arabian_sea_demo",
        }
        if hours_back is not None:
            payload["hours_back"] = hours_back

        body = await self._post("/backtrack", payload)

        if isinstance(body.get("data"), dict):
            body = body["data"]

        try:
            origin_lat, origin_lon = self._validate_lat_lon(
                body["origin_lat"], body["origin_lon"]
            )
            confidence = float(body["confidence"])
            if not 0.0 <= confidence <= 1.0:
                raise ValueError(f"confidence outside 0..1: {confidence}")
            uncertainty_km = float(body["uncertainty_km"])
            if uncertainty_km < 0:
                raise ValueError("uncertainty_km must be >= 0")
            origin_time = body["origin_time"]
            datetime.fromisoformat(origin_time.replace("Z", "+00:00"))
        except (KeyError, TypeError, ValueError) as exc:
            logger.error(f"Invalid GIS backtrack payload: {exc}")
            raise AppException(
                ErrorCode.GIS_SERVICE_UNAVAILABLE,
                f"GIS service returned invalid backtrack data: {exc}",
                status_code=502,
            )

        return BacktrackResult(
            origin_lon=round(origin_lon, 6),
            origin_lat=round(origin_lat, 6),
            estimated_time=origin_time,
            confidence=round(confidence, 2),
            geometry_wkt=_uncertainty_polygon_wkt(origin_lat, origin_lon, uncertainty_km),
            method=str(body.get("model") or "baseline_advection"),
        )

    async def forecast(
        self,
        spill_lon: float,
        spill_lat: float,
        spill_area_sq_km: float,
        current_wind_u: float = 0.0,
        current_wind_v: float = 0.0,
        current_current_u: float = 0.0,
        current_current_v: float = 0.0,
        origin_time: Optional[str] = None,
        hours_forward: float = 72,
        scenario: Optional[str] = None,
    ) -> ForecastResult:
        from datetime import datetime, timezone
        from app.core.exceptions import AppException, ErrorCode

        payload = {
            "origin_lat": spill_lat,
            "origin_lon": spill_lon,
            "origin_time": origin_time
            or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "hours_forward": hours_forward,
            "scenario": scenario or "arabian_sea_demo",
        }

        body = await self._post("/forecast", payload)

        if isinstance(body.get("data"), dict):
            body = body["data"]

        entries = []
        for index, point in enumerate(body.get("forecast_points") or []):
            try:
                lat, lon = self._validate_lat_lon(point["lat"], point["lon"])
                hours = int(point["hours"])
                if hours not in (24, 48, 72):
                    raise ValueError(f"unexpected forecast hour: {hours}")
                area = float(point["area_km2"])
                if area < 0:
                    raise ValueError("forecast area must be >= 0")
                uncertainty = float(point["uncertainty_km"])
                point_time = point["time"]
                datetime.fromisoformat(point_time.replace("Z", "+00:00"))
            except (KeyError, TypeError, ValueError) as exc:
                logger.error(f"Invalid GIS forecast point #{index}: {exc}")
                raise AppException(
                    ErrorCode.GIS_SERVICE_UNAVAILABLE,
                    f"GIS service returned an invalid forecast point: {exc}",
                    status_code=502,
                )

            entries.append(
                ForecastEntry(
                    hours=hours,
                    area_sq_km=round(area, 2),
                    geometry_wkt=_uncertainty_polygon_wkt(lat, lon, uncertainty),
                    center_lat=lat,
                    center_lon=lon,
                    uncertainty=round(uncertainty, 2),
                )
            )

        if not entries:
            from app.core.exceptions import AppException, ErrorCode
            raise AppException(
                ErrorCode.GIS_SERVICE_UNAVAILABLE,
                "GIS service returned no forecast points",
                status_code=502,
            )

        return ForecastResult(entries=entries)


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

    async def forecast(
        self,
        spill_lon: float,
        spill_lat: float,
        spill_area_sq_km: float,
        current_wind_u: float = 0.0,
        current_wind_v: float = 0.0,
        current_current_u: float = 0.0,
        current_current_v: float = 0.0,
        origin_time: Optional[str] = None,
        hours_forward: float = 72,
        scenario: Optional[str] = None,
    ) -> ForecastResult:
        from app.services.forecast_client import MockForecastClient

        return await MockForecastClient().forecast(
            spill_lon=spill_lon,
            spill_lat=spill_lat,
            spill_area_sq_km=spill_area_sq_km,
        )