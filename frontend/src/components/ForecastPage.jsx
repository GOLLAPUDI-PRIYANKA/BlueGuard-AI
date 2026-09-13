import React, { useState } from "react";
import {
  CloudSun,
  Wind,
  Compass,
  AlertTriangle,
  Clock,
  Waves,
  Calendar,
  Layers,
} from "lucide-react";
import MapView from "./MapView";

export default function ForecastPage({
  forecast = [],
  spill,
  origin,
}) {
  const [selectedHorizon, setSelectedHorizon] = useState("all");

  const displayedForecast =
    selectedHorizon === "all"
      ? forecast
      : forecast.filter((f) => f.hours === Number(selectedHorizon));

  const activeForecastItem =
    forecast.find((f) => f.hours === Number(selectedHorizon)) || forecast[0];

  return (
    <div className="page-container">
      {/* HEADER */}
      <div className="page-header">
        <div>
          <span className="eyebrow">OCEAN DRIFT MODELING</span>
          <h1>Forward Oil Spill Drift Forecast</h1>
          <p>
            Hydrodynamic advection simulation predicting slick trajectory, expansion, and coastal impact across 24h, 48h, and 72h horizons
          </p>
        </div>

        <div className="summary-pills">
          <div className="pill">
            <span>Forecast Model</span>
            <strong>Baseline Advection (M4)</strong>
          </div>
          <div className="pill warning">
            <span>Max Horizon</span>
            <strong>+72 Hours</strong>
          </div>
        </div>
      </div>

      {/* HORIZON SELECTOR TABS */}
      <div className="forecast-tabs panel">
        <button
          type="button"
          className={`forecast-tab-btn ${
            selectedHorizon === "all" ? "active" : ""
          }`}
          onClick={() => setSelectedHorizon("all")}
        >
          All Horizons (24h, 48h, 72h)
        </button>
        {forecast.map((f) => (
          <button
            key={f.hours}
            type="button"
            className={`forecast-tab-btn ${
              selectedHorizon === String(f.hours) ? "active" : ""
            }`}
            onClick={() => setSelectedHorizon(String(f.hours))}
          >
            +{f.hours} Hours Horizon
          </button>
        ))}
      </div>

      {/* FORECAST CARDS GRID */}
      <div className="forecast-grid">
        {forecast.map((f) => (
          <div
            key={f.hours}
            className={`forecast-card panel ${
              selectedHorizon === String(f.hours) || selectedHorizon === "all"
                ? "active-card"
                : "dimmed"
            }`}
            onClick={() => setSelectedHorizon(String(f.hours))}
          >
            <div className="forecast-card-head">
              <div className="horizon-badge">+{f.hours}h</div>
              <div>
                <h4>{f.status || `+${f.hours}h Prediction`}</h4>
                <span>{f.time}</span>
              </div>
            </div>

            <div className="forecast-metric-row">
              <div className="forecast-stat">
                <span>Predicted Area</span>
                <strong>{f.areaSqKm} km²</strong>
              </div>
              <div className="forecast-stat">
                <span>Model Confidence</span>
                <strong className="text-accent">
                  {Math.round(f.confidence * 100)}%
                </strong>
              </div>
              <div className="forecast-stat">
                <span>Uncertainty</span>
                <strong>±{f.uncertaintyKm} km</strong>
              </div>
            </div>

            <div className="forecast-coords">
              <Compass size={14} />
              <span>
                Coordinates: <strong>{f.lat.toFixed(3)}° N, {f.lon.toFixed(3)}° E</strong>
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* EMBEDDED MAP & DRIFT PARAMETERS */}
      <div className="forecast-map-layout">
        <div className="panel forecast-map-container">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">GEOSPATIAL PROJECTION</span>
              <h2>Forecast Trajectory & Dispersion Corridor</h2>
            </div>
            <span className="text-muted text-sm">
              Showing {displayedForecast.length} Forecast Horizon(s)
            </span>
          </div>

          <MapView
            spill={spill}
            origin={origin}
            forecast={displayedForecast}
            vessels={[]}
          />
        </div>

        {/* DRIFT PHYSICS PARAMETERS PANEL */}
        <div className="panel forecast-physics-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">SIMULATION COEFFICIENTS</span>
              <h2>MetOcean Parameters</h2>
            </div>
          </div>

          <div className="physics-param-list">
            <div className="param-item">
              <div className="param-title">
                <Wind size={16} /> Wind Drag Coefficient
              </div>
              <strong>3.0% (0.03)</strong>
              <small>Empirical coastal slick drift factor</small>
            </div>

            <div className="param-item">
              <div className="param-title">
                <Waves size={16} /> Surface Ocean Currents
              </div>
              <strong>0.45 m/s • East-Northeast</strong>
              <small>CMEMS Arabian Sea hydrodynamic baseline</small>
            </div>

            <div className="param-item">
              <div className="param-title">
                <Clock size={16} /> Advection Timestep
              </div>
              <strong>Δt = 1 hour</strong>
              <small>Euler forward integration step</small>
            </div>

            <div className="param-item alert-box">
              <AlertTriangle size={18} className="text-warning" />
              <div>
                <strong>Shoreline Impact Alert</strong>
                <p>
                  At +72h (area 43.2 km²), the northern periphery of the dispersion corridor is predicted to make landfall along the Goa-Maharashtra coastal boundary.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
