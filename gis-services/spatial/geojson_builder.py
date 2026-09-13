from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence, Tuple

from spatial.geometry_utils import circle_polygon, corridor_polygon


def _feature(geometry: Dict[str, Any], properties: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "Feature",
        "properties": properties,
        "geometry": geometry,
    }


class GeoJSONBuilder:
    """Create map-ready GeoJSON using WGS84 coordinates in [longitude, latitude]."""

    def create_origin_feature(
        self,
        lat: float,
        lon: float,
        uncertainty_km: float,
        confidence: float | None = None,
    ) -> Dict[str, Any]:
        properties = {
            "type": "origin_uncertainty",
            "uncertainty_km": uncertainty_km,
        }
        if confidence is not None:
            properties["confidence"] = confidence

        return _feature(
            {
                "type": "Polygon",
                "coordinates": [circle_polygon(lat, lon, uncertainty_km)],
            },
            properties,
        )

    def create_point_feature(
        self,
        lat: float,
        lon: float,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        return _feature(
            {"type": "Point", "coordinates": [lon, lat]},
            properties,
        )

    def create_line_feature(
        self,
        points: Sequence[Tuple[float, float]],
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        coordinates = [[lon, lat] for lat, lon in points]
        return _feature(
            {"type": "LineString", "coordinates": coordinates},
            properties,
        )

    def create_forecast_corridor(
        self,
        points: Sequence[Tuple[float, float]],
        radius_km: float = 3.0,
    ) -> Dict[str, Any]:
        return _feature(
            {
                "type": "Polygon",
                "coordinates": [corridor_polygon(points, radius_km)],
            },
            {
                "type": "forecast_corridor",
                "spread_radius_km": radius_km,
                "hours_forward": 72,
            },
        )

    def create_forecast_path(
        self,
        points: Sequence[Tuple[float, float]],
    ) -> Dict[str, Any]:
        return self.create_line_feature(
            points,
            {"type": "forecast_path"},
        )

    def create_feature_collection(
        self,
        features: Iterable[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "type": "FeatureCollection",
            "features": list(features),
        }
