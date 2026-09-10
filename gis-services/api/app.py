from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify, request
from flask_cors import CORS

# Allow `python api/app.py` from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtracking.drift_model import BacktrackingModel, parse_iso_time
from forecasting.drift_prediction import ForecastingModel
from spatial.geojson_builder import GeoJSONBuilder
from data.adapters.environment_adapter import EnvironmentAdapter

app = Flask(__name__)
CORS(app)

backtracker = BacktrackingModel()
forecaster = ForecastingModel()
builder = GeoJSONBuilder()
environment = EnvironmentAdapter()


def ok(data: Dict[str, Any], status: int = 200):
    return jsonify({"success": True, "data": data}), status


def fail(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status


def required_json() -> Dict[str, Any]:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object")
    return payload


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "member4-gis"})


@app.post("/api/gis/backtrack")
def backtrack():
    try:
        payload = required_json()

        result = backtracker.estimate_source(
            detected_lat=payload["detected_lat"],
            detected_lon=payload["detected_lon"],
            detected_time=payload["detected_time"],
            environmental_data=payload.get("environmental_data", []),
            hours_back=payload.get("hours_back"),
            scenario=payload.get("scenario"),
        )

        origin_feature = builder.create_origin_feature(
            result["origin_lat"],
            result["origin_lon"],
            result["uncertainty_km"],
            result["confidence"],
        )

        trail = builder.create_line_feature(
            [
                (result["origin_lat"], result["origin_lon"]),
                (float(payload["detected_lat"]), float(payload["detected_lon"])),
            ],
            {"type": "backtrack_trail"},
        )

        detection = builder.create_point_feature(
            float(payload["detected_lat"]),
            float(payload["detected_lon"]),
            {
                "type": "detection_point",
                "spill_id": payload.get("spill_id", "unknown"),
            },
        )

        geojson = builder.create_feature_collection(
            [origin_feature, trail, detection]
        )

        result["geojson"] = geojson
        return ok(result)

    except KeyError as exc:
        return fail(f"Missing required field: {exc.args[0]}")
    except (ValueError, TypeError) as exc:
        return fail(str(exc))
    except Exception:
        app.logger.exception("Backtrack endpoint failed")
        return fail("Internal GIS error", 500)


@app.post("/api/gis/forecast")
def forecast():
    try:
        payload = required_json()

        result = forecaster.predict_drift(
            origin_lat=payload["origin_lat"],
            origin_lon=payload["origin_lon"],
            origin_time=payload["origin_time"],
            environmental_data=payload.get("environmental_data", []),
            hours_forward=payload.get("hours_forward", 72),
            scenario=payload.get("scenario"),
        )

        points = result["forecast_points"]
        path_points = [
            (float(payload["origin_lat"]), float(payload["origin_lon"]))
        ] + [(p["lat"], p["lon"]) for p in points]

        path = builder.create_forecast_path(path_points)
        corridor = builder.create_forecast_corridor(path_points, 3.0)

        point_features = [
            builder.create_point_feature(
                p["lat"],
                p["lon"],
                {
                    "type": "forecast_point",
                    "hours": p["hours"],
                    "time": p["time"],
                    "area_km2": p["area_km2"],
                    "confidence": p["confidence"],
                    "uncertainty_km": p["uncertainty_km"],
                },
            )
            for p in points
        ]

        result["geojson"] = builder.create_feature_collection(
            [corridor, path] + point_features
        )
        return ok(result)

    except KeyError as exc:
        return fail(f"Missing required field: {exc.args[0]}")
    except (ValueError, TypeError) as exc:
        return fail(str(exc))
    except Exception:
        app.logger.exception("Forecast endpoint failed")
        return fail("Internal GIS error", 500)


@app.post("/api/gis/complete")
def complete():
    try:
        payload = required_json()

        detected_lat = float(payload["detected_lat"])
        detected_lon = float(payload["detected_lon"])
        detected_time = payload["detected_time"]
        hours_back = payload.get("hours_back", 10 + 20 / 60)
        hours_forward = payload.get("hours_forward", 72)
        scenario = payload.get("scenario")

        backtrack_result = backtracker.estimate_source(
            detected_lat=detected_lat,
            detected_lon=detected_lon,
            detected_time=detected_time,
            environmental_data=payload.get("environmental_data", []),
            hours_back=hours_back,
            scenario=scenario,
        )

        forecast_result = forecaster.predict_drift(
            origin_lat=backtrack_result["origin_lat"],
            origin_lon=backtrack_result["origin_lon"],
            origin_time=backtrack_result["origin_time"],
            environmental_data=payload.get("environmental_data", []),
            hours_forward=hours_forward,
            scenario=scenario,
        )

        origin_feature = builder.create_origin_feature(
            backtrack_result["origin_lat"],
            backtrack_result["origin_lon"],
            backtrack_result["uncertainty_km"],
            backtrack_result["confidence"],
        )

        backtrack_trail = builder.create_line_feature(
            [
                (backtrack_result["origin_lat"], backtrack_result["origin_lon"]),
                (detected_lat, detected_lon),
            ],
            {"type": "backtrack_trail"},
        )

        detection = builder.create_point_feature(
            detected_lat,
            detected_lon,
            {"type": "detection_point", "spill_id": payload.get("spill_id", "unknown")},
        )

        forecast_points = forecast_result["forecast_points"]
        forecast_path_points = [
            (backtrack_result["origin_lat"], backtrack_result["origin_lon"])
        ] + [(p["lat"], p["lon"]) for p in forecast_points]

        corridor = builder.create_forecast_corridor(forecast_path_points, 3.0)
        forecast_path = builder.create_forecast_path(forecast_path_points)

        forecast_markers = [
            builder.create_point_feature(
                p["lat"],
                p["lon"],
                {
                    "type": "forecast_point",
                    "hours": p["hours"],
                    "time": p["time"],
                    "area_km2": p["area_km2"],
                    "confidence": p["confidence"],
                    "uncertainty_km": p["uncertainty_km"],
                },
            )
            for p in forecast_points
        ]

        combined_geojson = builder.create_feature_collection(
            [
                detection,
                origin_feature,
                backtrack_trail,
                corridor,
                forecast_path,
                *forecast_markers,
            ]
        )

        return ok(
            {
                "backtrack": backtrack_result,
                "forecast": forecast_result,
                "combined_geojson": combined_geojson,
            }
        )

    except KeyError as exc:
        return fail(f"Missing required field: {exc.args[0]}")
    except (ValueError, TypeError) as exc:
        return fail(str(exc))
    except Exception:
        app.logger.exception("Complete endpoint failed")
        return fail("Internal GIS error", 500)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=False)
