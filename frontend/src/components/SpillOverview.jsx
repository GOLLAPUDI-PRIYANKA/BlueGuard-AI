import React from "react";
import { AlertTriangle, MapPin, Clock, Activity } from "lucide-react";

export default function SpillOverview({ spill, onInvestigate, investigating }) {
  const confidence = Math.round((spill?.confidence ?? 0) * 100);
  const area = Number(spill?.areaSqKm ?? 0).toFixed(1);
  const severity = spill?.severity ?? "UNKNOWN";
  const detectedAt = spill?.detectedAt
    ? new Date(spill.detectedAt).toLocaleString()
    : "Unknown";
  const latitude = spill?.centroid?.lat;
  const longitude = spill?.centroid?.lon;

  return (
    <div className="panel overview">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">CURRENT CASE</span>
          <h2>Spill Overview</h2>
        </div>
        <Activity size={20} className="muted-icon" />
      </div>

      <div className="spill-alert">
        <div className="alert-icon">
          <AlertTriangle size={18} />
        </div>
        <div>
          <strong>{severity} severity spill</strong>
          <span>Requires investigation</span>
        </div>
      </div>

      <div className="stat-grid">
        <div>
          <span>Area</span>
          <strong>{area} km²</strong>
        </div>

        <div>
          <span>Confidence</span>
          <strong>{confidence}%</strong>
        </div>
      </div>

      <div className="detail-list">
        <div>
          <span>
            <AlertTriangle size={15} /> Severity
          </span>
          <strong className="text-danger">{severity}</strong>
        </div>

        <div>
          <span>
            <Clock size={15} /> Detected
          </span>
          <strong>{detectedAt}</strong>
        </div>

        <div>
          <span>
            <MapPin size={15} /> Location
          </span>
          <strong>
            {latitude !== undefined && longitude !== undefined
              ? `${latitude.toFixed(4)}° N, ${longitude.toFixed(4)}° E`
              : "Unknown"}
          </strong>
        </div>
      </div>

      <button
        className="primary-btn"
        onClick={onInvestigate}
        disabled={investigating}
      >
        {investigating ? "Analyzing..." : "Investigate Spill"}{" "}
        <span>→</span>
      </button>
    </div>
  );
}
