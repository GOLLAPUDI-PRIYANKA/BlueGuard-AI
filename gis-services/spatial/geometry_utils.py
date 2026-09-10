from __future__ import annotations

import math
from typing import Iterable, List, Sequence, Tuple

Coordinate = Tuple[float, float]  # lon, lat


def destination_point(lat: float, lon: float, bearing_deg: float, distance_km: float) -> Coordinate:
    """Approximate destination point on Earth; suitable for demo-scale GeoJSON."""
    radius_km = 6371.0088
    bearing = math.radians(bearing_deg)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    angular = distance_km / radius_km

    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular)
        + math.cos(lat1) * math.sin(angular) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(angular) * math.cos(lat1),
        math.cos(angular) - math.sin(lat1) * math.sin(lat2),
    )

    return math.degrees(lon2), math.degrees(lat2)


def circle_polygon(lat: float, lon: float, radius_km: float, steps: int = 48) -> List[Coordinate]:
    """Create a closed approximate circular polygon around a WGS84 point."""
    if radius_km <= 0:
        raise ValueError("radius_km must be greater than 0")

    ring = [
        destination_point(lat, lon, bearing, radius_km)
        for bearing in [i * 360.0 / steps for i in range(steps)]
    ]
    ring.append(ring[0])
    return ring


def _bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Approximate bearing from point 1 to point 2."""
    y = math.sin(math.radians(lon2 - lon1)) * math.cos(math.radians(lat2))
    x = (
        math.cos(math.radians(lat1)) * math.sin(math.radians(lat2))
        - math.sin(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.cos(math.radians(lon2 - lon1))
    )
    return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0


def corridor_polygon(
    points: Sequence[Tuple[float, float]],
    radius_km: float = 3.0,
) -> List[Coordinate]:
    """
    Build a simple corridor around a path.

    Input points are (lat, lon); output GeoJSON coordinates are (lon, lat).
    """
    if len(points) < 2:
        raise ValueError("At least two path points are required")
    if radius_km <= 0:
        raise ValueError("radius_km must be greater than 0")

    left_side: List[Coordinate] = []
    right_side: List[Coordinate] = []

    for i, (lat, lon) in enumerate(points):
        if i == 0:
            bearing = _bearing_deg(lat, lon, *points[i + 1])
        elif i == len(points) - 1:
            bearing = _bearing_deg(*points[i - 1], lat, lon)
        else:
            b1 = _bearing_deg(*points[i - 1], lat, lon)
            b2 = _bearing_deg(lat, lon, *points[i + 1])
            bearing = (b1 + b2) / 2.0

        left_side.append(destination_point(lat, lon, (bearing - 90) % 360, radius_km))
        right_side.append(destination_point(lat, lon, (bearing + 90) % 360, radius_km))

    return left_side + list(reversed(right_side)) + [left_side[0]]
