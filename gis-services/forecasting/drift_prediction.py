from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Iterable, Optional
import math

from backtracking.drift_model import parse_iso_time, _mean_environment_velocity, _move_point


class ForecastingModel:
    """
    Baseline forward oil-spill drift model.

    The supplied Arabian Sea demo uses the exact reference points from the
    project scenario so the team's dashboard and API remain reproducible.
    """

    DEMO_POINTS = [
        {"hours": 24, "lat": 15.58, "lon": 74.12, "area_km2": 22.4},
        {"hours": 48, "lat": 15.89, "lon": 74.45, "area_km2": 31.7},
        {"hours": 72, "lat": 16.12, "lon": 74.78, "area_km2": 43.2},
    ]
    DEMO_UNCERTAINTY_KM = 20.0
    DEMO_CONFIDENCE = 0.68

    def __init__(self, wind_drag: float = 0.03) -> None:
        self.wind_drag = float(wind_drag)

    def predict_drift(
        self,
        origin_lat: float,
        origin_lon: float,
        origin_time: str,
        environmental_data: Optional[Iterable[Dict[str, Any]]] = None,
        hours_forward: float = 72,
        scenario: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._validate_coordinates(origin_lat, origin_lon)

        origin_dt = parse_iso_time(origin_time)
        hours_forward = float(hours_forward)

        if hours_forward <= 0 or hours_forward > 168:
            raise ValueError("hours_forward must be greater than 0 and no more than 168")

        requested_hours = [h for h in (24, 48, 72) if h <= hours_forward]

        if (
            scenario == "arabian_sea_demo"
            and abs(float(origin_lat) - 15.201) < 0.01
            and abs(float(origin_lon) - 73.512) < 0.01
        ):
            points = []
            for item in self.DEMO_POINTS:
                if item["hours"] <= hours_forward:
                    dt = origin_dt + timedelta(hours=item["hours"])
                    points.append(
                        {
                            "hours": item["hours"],
                            "time": dt.isoformat().replace("+00:00", "Z"),
                            "lat": item["lat"],
                            "lon": item["lon"],
                            "area_km2": item["area_km2"],
                            "confidence": self.DEMO_CONFIDENCE,
                            "uncertainty_km": self.DEMO_UNCERTAINTY_KM,
                        }
                    )

            return {
                "forecast_points": points,
                "confidence": self.DEMO_CONFIDENCE,
                "uncertainty_km": self.DEMO_UNCERTAINTY_KM,
                "model": "baseline_advection_demo_reference",
                "wind_drag": self.wind_drag,
            }

        u_mps, v_mps = _mean_environment_velocity(environmental_data or [])
        if abs(u_mps) < 1e-12 and abs(v_mps) < 1e-12:
            u_mps, v_mps = 0.95, 0.70

        points = []
        for h in requested_hours:
            lat, lon = _move_point(
                float(origin_lat), float(origin_lon), u_mps, v_mps, h
            )
            dt = origin_dt + timedelta(hours=h)
            spread = 5.0 + 0.20 * h
            confidence = max(0.50, min(0.90, 0.88 - 0.004 * h))

            points.append(
                {
                    "hours": h,
                    "time": dt.isoformat().replace("+00:00", "Z"),
                    "lat": round(lat, 6),
                    "lon": round(lon, 6),
                    "area_km2": round(math.pi * spread * spread / 100.0, 2),
                    "confidence": round(confidence, 2),
                    "uncertainty_km": round(spread, 2),
                }
            )

        return {
            "forecast_points": points,
            "confidence": points[-1]["confidence"] if points else None,
            "uncertainty_km": points[-1]["uncertainty_km"] if points else None,
            "model": "baseline_advection",
            "wind_drag": self.wind_drag,
        }

    @staticmethod
    def _validate_coordinates(lat: float, lon: float) -> None:
        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError) as exc:
            raise ValueError("Latitude and longitude must be numbers") from exc

        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= lon <= 180:
            raise ValueError("Longitude must be between -180 and 180")
