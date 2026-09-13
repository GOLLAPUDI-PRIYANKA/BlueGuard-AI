"""Adapter for Member 2's current inference.py output.

M2 returns polygon points in 256x256 image pixel coordinates. Those are not
GeoJSON coordinates. This module validates that output and optionally converts
pixel polygons to WGS84 GeoJSON when the caller supplies image bounds.
"""
from __future__ import annotations

from typing import Any, Dict, List


def parse_ai_detection(ai_result: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(ai_result, dict):
        raise ValueError("ai_detection must be a JSON object")

    confidence = ai_result.get("confidence")
    if confidence is not None:
        confidence = float(confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("AI confidence must be between 0 and 1")

    polygons = ai_result.get("polygons", [])
    if polygons is None:
        polygons = []
    if not isinstance(polygons, list):
        raise ValueError("AI polygons must be a list")

    clean: List[List[List[float]]] = []
    for polygon in polygons:
        if not isinstance(polygon, list) or len(polygon) < 3:
            continue
        points = []
        for point in polygon:
            if not isinstance(point, (list, tuple)) or len(point) != 2:
                raise ValueError("Each AI polygon point must be [x, y]")
            x, y = float(point[0]), float(point[1])
            if not (0 <= x <= 255 and 0 <= y <= 255):
                raise ValueError("AI polygon pixel coordinates must be in the 256x256 image range")
            points.append([x, y])
        if len(points) >= 3:
            clean.append(points)

    return {
        "confidence": confidence,
        "polygons": clean,
        "num_regions": int(ai_result.get("num_regions", len(clean))),
    }


def pixel_polygons_to_geojson(
    polygons: List[List[List[float]]],
    image_bounds: List[List[float]],
) -> Dict[str, Any]:
    """Convert 256x256 pixel polygons to a GeoJSON MultiPolygon.

    image_bounds = [[south, west], [north, east]].
    Pixel origin is assumed to be top-left, matching standard image arrays.
    """
    if not isinstance(image_bounds, list) or len(image_bounds) != 2:
        raise ValueError("image_bounds must be [[south, west], [north, east]]")
    (south, west), (north, east) = image_bounds
    south, west, north, east = map(float, (south, west, north, east))
    if not (-90 <= south < north <= 90 and -180 <= west < east <= 180):
        raise ValueError("Invalid image_bounds")

    rings = []
    for polygon in polygons:
        ring = []
        for x, y in polygon:
            lon = west + (x / 255.0) * (east - west)
            lat = north - (y / 255.0) * (north - south)
            ring.append([lon, lat])
        if ring and ring[0] != ring[-1]:
            ring.append(ring[0])
        if len(ring) >= 4:
            rings.append([ring])

    return {
        "type": "Feature",
        "properties": {"type": "ai_detected_spill_polygon"},
        "geometry": {"type": "MultiPolygon", "coordinates": rings},
    }
