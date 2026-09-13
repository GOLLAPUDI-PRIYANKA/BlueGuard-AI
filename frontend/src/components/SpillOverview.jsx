import React from "react";
import { AlertTriangle, MapPin, Clock, Activity, ExternalLink } from "lucide-react";

export default function SpillOverview({
  spill,
  onInvestigate,
  onViewDetails,
  investigating = false,
}) {
  if (!spill) return null;

  const lat = spill.centroid?.lat || spill.latitude || 15.462;
  const lon = spill.centroid?.lon || spill.longitude || 73.845;
  const conf = Math.round(
    spill.confidence > 1 ? spill.confidence : (spill.confidence || 0.91) * 100
  );
  const area = spill.areaSqKm || spill.area || 12.5;

  return (
    <div className="panel overview">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">ACTIVE CASE #{spill.spillId || spill.id || "SP101"}</span>
          <h2>Spill Overview</h2>
        </div>
        <Activity size={20} className="muted-icon" />
      </div>

      <div className="spill-alert">
        <div className="alert-icon">
          <AlertTriangle size={18} />
        </div>
        <div>
          <strong>{spill.severity || "HIGH"} Severity Slick</strong>
          <span>
            {spill.title || "Arabian Sea Incident"} • Action required
          </span>
        </div>
      </div>

      <div className="stat-grid">
        <div>
          <span>Estimated Slick Area</span>
          <strong>{area} km²</strong>
        </div>
        <div>
          <span>AI Detection Confidence</span>
          <strong className="text-accent">{conf}%</strong>
        </div>
      </div>

      <div className="detail-list">
        <div>
          <span>
            <AlertTriangle size={15} /> Severity
          </span>
          <strong
            className={
              spill.severity === "CRITICAL" || spill.severity === "HIGH"
                ? "text-danger"
                : "text-warning"
            }
          >
            {spill.severity || "HIGH"}
          </strong>
        </div>

        <div>
          <span>
            <Clock size={15} /> Detection Time
          </span>
          <strong>{spill.detectedAt || "2026-08-29 10:00 UTC"}</strong>
        </div>

        <div>
          <span>
            <MapPin size={15} /> Location
          </span>
          <strong>
            {lat.toFixed(3)}° N, {lon.toFixed(3)}° E
          </strong>
        </div>
      </div>

      <div className="overview-btn-group">
        <button
          type="button"
          className="primary-btn"
          onClick={onInvestigate}
          disabled={investigating}
        >
          {investigating ? (
            <>
              <span className="spinner-sm" /> Running Pipeline...
            </>
          ) : (
            <>
              Investigate Spill <span>→</span>
            </>
          )}
        </button>

        {onViewDetails && (
          <button
            type="button"
            className="secondary-btn"
            style={{ width: "100%", marginTop: "8px" }}
            onClick={() => onViewDetails(spill)}
          >
            Full Spill Telemetry <ExternalLink size={14} />
          </button>
        )}
      </div>
    </div>
  );
}