from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify, request
from flask_cors import CORS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtracking.drift_model import BacktrackingModel
from forecasting.drift_prediction import ForecastingModel
from spatial.geojson_builder import GeoJSONBuilder
from spatial.ai_adapter import parse_ai_detection, pixel_polygons_to_geojson
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


def resolve_detection(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Accept either direct GIS coordinates or the AI member's inference result.

    M2's current inference.py returns mask/confidence/polygons where polygon
    points are image pixels. Pixel polygons are NOT latitude/longitude.
    Therefore lat/lon and detection time still need to come from the upstream
    georeferencing/backend layer.
    """
    ai_detection = payload.get("ai_detection")
    if ai_detection is not None:
        parsed = parse_ai_detection(ai_detection)
    else:
        parsed = {
            "confidence": payload.get("confidence"),
            "polygons": payload.get("polygons", []),
            "num_regions": len(payload.get("polygons", [])),
        }

    try:
        lat = float(payload["detected_lat"])
        lon = float(payload["detected_lon"])
    except KeyError as exc:
        raise ValueError(
            f"Missing required field: {exc.args[0]}. M2 pixel polygons require detected_lat/detected_lon from the georeferencing or backend layer."
        )

    result = {
        "detected_lat": lat,
        "detected_lon": lon,
        "confidence": parsed.get("confidence"),
        "polygons": parsed.get("polygons", []),
        "num_regions": parsed.get("num_regions", 0),
    }

    # Optional image bounds allow M4 to turn M2's 256x256 pixel polygons into
    # a map polygon. Bounds are [[south, west], [north, east]].
    if payload.get("image_bounds") and result["polygons"]:
        result["polygon_geojson"] = pixel_polygons_to_geojson(
            result["polygons"], payload["image_bounds"]
        )

    return result


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "member4-gis"})


@app.post("/backtrack")
def backtrack():
    try:
        payload = required_json()
        detection = resolve_detection(payload)
        result = backtracker.estimate_source(
            detected_lat=detection["detected_lat"],
            detected_lon=detection["detected_lon"],
            detected_time=payload["detected_time"],
            environmental_data=payload.get("environmental_data", []),
            hours_back=payload.get("hours_back"),
            scenario=payload.get("scenario"),
        )

        origin_feature = builder.create_origin_feature(
            result["origin_lat"], result["origin_lon"],
            result["uncertainty_km"], result["confidence"]
        )
        trail = builder.create_line_feature(
            [(result["origin_lat"], result["origin_lon"]),
             (detection["detected_lat"], detection["detected_lon"])],
            {"type": "backtrack_trail"},
        )
        detection_feature = builder.create_point_feature(
            detection["detected_lat"], detection["detected_lon"],
            {"type": "detection_point", "spill_id": payload.get("spill_id", "unknown"),
             "ai_confidence": detection["confidence"]},
        )

        features = [origin_feature, trail, detection_feature]
        if detection.get("polygon_geojson"):
            features.append(detection["polygon_geojson"])
        result["geojson"] = builder.create_feature_collection(features)
        result["ai_detection"] = {k: detection[k] for k in ("confidence", "num_regions") if detection.get(k) is not None}
        return ok(result)

    except KeyError as exc:
        return fail(f"Missing required field: {exc.args[0]}")
    except (ValueError, TypeError) as exc:
        return fail(str(exc))
    except Exception:
        app.logger.exception("Backtrack endpoint failed")
        return fail("Internal GIS error", 500)


@app.post("/forecast")
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
        path_points = [(float(payload["origin_lat"]), float(payload["origin_lon"]))] + [(p["lat"], p["lon"]) for p in points]
        path = builder.create_forecast_path(path_points)
        corridor = builder.create_forecast_corridor(path_points, 3.0)
        point_features = [builder.create_point_feature(
            p["lat"], p["lon"],
            {"type": "forecast_point", "hours": p["hours"], "time": p["time"],
             "area_km2": p["area_km2"], "confidence": p["confidence"],
             "uncertainty_km": p["uncertainty_km"]}
        ) for p in points]
        result["geojson"] = builder.create_feature_collection([corridor, path] + point_features)
        return ok(result)

    except KeyError as exc:
        return fail(f"Missing required field: {exc.args[0]}")
    except (ValueError, TypeError) as exc:
        return fail(str(exc))
    except Exception:
        app.logger.exception("Forecast endpoint failed")
        return fail("Internal GIS error", 500)


# Backward-compatible aliases for anyone who already tested the earlier ZIP.
app.add_url_rule("/api/gis/backtrack", view_func=backtrack, methods=["POST"])
app.add_url_rule("/api/gis/forecast", view_func=forecast, methods=["POST"])


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=False)
