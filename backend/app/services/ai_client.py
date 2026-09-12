import logging
import math
import random
from dataclasses import dataclass
from typing import Optional

import httpx
from shapely.geometry import MultiPolygon, Polygon

from app.core.config import get_settings

logger = logging.getLogger("marineguard.ai")


@dataclass
class AIDetectionResult:
    detected: bool
    confidence: float
    area_sq_km: float
    severity: str
    centroid_lat: float
    centroid_lon: float
    geometry_wkt: str
    mask_uri: str
    model_version: str


class AIClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url

    async def detect(
        self, image_uri: str, model_version: str = "unet_v1", image_bounds: Optional[list[list[float]]] = None
    ) -> AIDetectionResult:
        raise NotImplementedError("Real AI client not yet implemented")


def build_ai_client() -> AIClient:
    settings = get_settings()
    if settings.USE_MOCK_SERVICES:
        return MockAIClient()
    return RealAIClient(base_url=settings.AI_SERVICE_URL)


class RealAIClient(AIClient):
    """HTTP adapter for the AI inference service (POST /predict).

    The AI service works in 256x256 pixel space (see ai-services/src/inference.py),
    so this client georeferences pixel polygons onto a demo tile centered on the
    detection area. Swap the georeferencing once the GIS service provides real
    scene bounds.
    """

    TILE_CENTER_LAT = 15.462
    TILE_CENTER_LON = 73.845
    TILE_SPAN_DEG = 0.3
    TILE_PIXELS = 256

    def __init__(self, base_url: str = "http://localhost:8001", transport: Optional[httpx.AsyncBaseTransport] = None):
        super().__init__(base_url.rstrip("/"))
        self._transport = transport

    async def _post_predict(self, image_uri: str, model_version: str) -> dict:
        from app.core.exceptions import ErrorCode, ServiceUnavailableError
        timeout = httpx.Timeout(30.0)
        try:
            async with httpx.AsyncClient(transport=self._transport, timeout=timeout) as http:
                response = await http.post(
                    f"{self.base_url}/predict",
                    json={"imageUri": image_uri, "modelVersion": model_version},
                )
        except httpx.HTTPError:
            raise ServiceUnavailableError("AI", ErrorCode.AI_SERVICE_UNAVAILABLE)

        if response.status_code != 200:
            raise ServiceUnavailableError("AI", ErrorCode.AI_SERVICE_UNAVAILABLE)
        try:
            return response.json()
        except ValueError:
            from app.core.exceptions import ErrorCode, ServiceUnavailableError
            raise ServiceUnavailableError("AI", ErrorCode.AI_SERVICE_UNAVAILABLE)

    @classmethod
    def _georef_pixels(
        cls,
        polygons: list[list[list[float]]],
        image_bounds: Optional[list[list[float]]] = None,
    ) -> MultiPolygon:
        """Map 256x256 pixel polygons to WGS84.

        image_bounds = [[south, west], [north, east]] with the pixel origin at
        top-left, matching the GIS member's pixel_polygons_to_geojson().
        Falls back to a demo tile centered on the detection area when bounds
        are not supplied.
        """
        if image_bounds is not None:
            if not isinstance(image_bounds, list) or len(image_bounds) != 2:
                raise ValueError("image_bounds must be [[south, west], [north, east]]")
            (south, west), (north, east) = (
                [float(v) for v in point] for point in image_bounds
            )
            if not (-90 <= south < north <= 90 and -180 <= west < east <= 180):
                raise ValueError("Invalid image_bounds")
            min_lon, max_lon = west, east
            max_lat, min_lat = north, south
        else:
            min_lon = cls.TILE_CENTER_LON - cls.TILE_SPAN_DEG / 2
            max_lon = cls.TILE_CENTER_LON + cls.TILE_SPAN_DEG / 2
            min_lat = cls.TILE_CENTER_LAT - cls.TILE_SPAN_DEG / 2
            max_lat = cls.TILE_CENTER_LAT + cls.TILE_SPAN_DEG / 2

        def to_lon_lat(x: float, y: float) -> tuple[float, float]:
            lon = min_lon + (x / (cls.TILE_PIXELS - 1)) * (max_lon - min_lon)
            lat = max_lat - (y / (cls.TILE_PIXELS - 1)) * (max_lat - min_lat)
            return lon, lat

        polys = []
        for contour in polygons:
            if len(contour) < 3:
                continue
            poly = Polygon([to_lon_lat(x, y) for x, y in contour])
            if poly.is_valid and not poly.is_empty:
                polys.append(poly)
        return MultiPolygon(polys) if polys else MultiPolygon()

    @staticmethod
    def _validate_polygons(polygons) -> list[list[list[float]]]:
        """Validate the AI service polygon payload (pixel space 0..255)."""
        if not isinstance(polygons, list):
            raise ValueError("AI polygons must be a list")
        clean = []
        for contour in polygons:
            if not isinstance(contour, list) or len(contour) < 3:
                continue
            points = []
            for point in contour:
                if not isinstance(point, (list, tuple)) or len(point) != 2:
                    raise ValueError("Each AI polygon point must be [x, y]")
                x, y = float(point[0]), float(point[1])
                if not (0 <= x <= 255 and 0 <= y <= 255):
                    raise ValueError("AI polygon pixel coordinates must be in the 256x256 range")
                points.append([x, y])
            if len(points) >= 3:
                clean.append(points)
        return clean

    async def detect(
        self,
        image_uri: str,
        model_version: str = "unet_v1",
        image_bounds: Optional[list[list[float]]] = None,
    ) -> AIDetectionResult:
        from app.core.exceptions import AppException, ErrorCode, ServiceUnavailableError
        payload = await self._post_predict(image_uri, model_version)

        try:
            detected = bool(payload.get("detected", False))
            confidence = float(payload.get("confidence", 0.0))
            if not 0.0 <= confidence <= 1.0:
                raise ValueError(f"AI confidence outside 0..1: {confidence}")
            polygons = self._validate_polygons(payload.get("polygons") or [])
            if image_bounds is not None:
                self._georef_pixels([[[0, 0], [255, 0], [255, 255], [0, 255], [0, 0]]], image_bounds)
        except (TypeError, ValueError) as exc:
            logger.error(f"Invalid AI service payload for {image_uri}: {exc}")
            raise AppException(
                ErrorCode.MODEL_INFERENCE_FAILED,
                f"AI service returned invalid detection data: {exc}",
                status_code=502,
            )

        mask_uri = payload.get("maskUri") or f"results/masks/{image_uri.replace('/', '_').replace('.', '_')}.tif"

        if detected and polygons:
            geometry = self._georef_pixels(polygons, image_bounds)
            if not geometry.is_empty:
                area = self._area_sq_km(geometry)
                centroid = geometry.centroid
                return AIDetectionResult(
                    detected=True,
                    confidence=confidence,
                    area_sq_km=area,
                    severity=self._severity_for(area),
                    centroid_lat=round(centroid.y, 6),
                    centroid_lon=round(centroid.x, 6),
                    geometry_wkt=geometry.wkt,
                    mask_uri=mask_uri,
                    model_version=payload.get("modelVersion") or model_version,
                )

        fallback_geometry = self._georef_pixels(
            [[[0, 0], [255, 0], [255, 255], [0, 255], [0, 0]]],
            image_bounds,
        )
        fallback_centroid = (
            fallback_geometry.centroid
            if not fallback_geometry.is_empty
            else (self.TILE_CENTER_LAT, self.TILE_CENTER_LON)
        )
        return AIDetectionResult(
            detected=False,
            confidence=confidence,
            area_sq_km=0.0,
            severity="LOW",
            centroid_lat=round(fallback_centroid.y, 6),
            centroid_lon=round(fallback_centroid.x, 6),
            geometry_wkt=fallback_geometry.wkt,
            mask_uri=mask_uri,
            model_version=payload.get("modelVersion") or model_version,
        )

    @staticmethod
    def _area_sq_km(geometry: MultiPolygon) -> float:
        if geometry.is_empty:
            return 0.0
        centroid = geometry.centroid
        km_per_deg_lat = 110.94
        km_per_deg_lon = 111.32 * abs(math.cos(math.radians(centroid.y)))
        area = geometry.area * km_per_deg_lat * km_per_deg_lon
        return round(area, 2)

    @staticmethod
    def _severity_for(area_sq_km: float) -> str:
        if area_sq_km > 25:
            return "HIGH"
        if area_sq_km > 10:
            return "MEDIUM"
        return "LOW"


class MockAIClient(AIClient):
    async def detect(
        self, image_uri: str, model_version: str = "unet_v1", image_bounds: Optional[list[list[float]]] = None
    ) -> AIDetectionResult:
        detected = True
        confidence = round(random.uniform(0.75, 0.98), 2)
        area = round(random.uniform(5.0, 40.0), 1)
        severity = "HIGH" if area > 25 else "MEDIUM" if area > 10 else "LOW"

        base_lat = 15.462
        base_lon = 73.845

        half_size = 0.05
        poly_coords = [
            (base_lon - half_size, base_lat - half_size),
            (base_lon + half_size, base_lat - half_size),
            (base_lon + half_size, base_lat + half_size),
            (base_lon - half_size, base_lat + half_size),
            (base_lon - half_size, base_lat - half_size),
        ]
        coord_str = ", ".join(f"{lon} {lat}" for lon, lat in poly_coords)
        geometry_wkt = f"MULTIPOLYGON ((({coord_str})))"

        return AIDetectionResult(
            detected=detected,
            confidence=confidence,
            area_sq_km=area,
            severity=severity,
            centroid_lat=base_lat,
            centroid_lon=base_lon,
            geometry_wkt=geometry_wkt,
            mask_uri=f"results/masks/{image_uri.replace('/', '_').replace('.', '_')}.tif",
            model_version=model_version,
        )
