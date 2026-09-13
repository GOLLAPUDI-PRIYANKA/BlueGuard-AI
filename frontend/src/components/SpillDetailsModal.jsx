import React from "react";
import {
  X,
  AlertTriangle,
  MapPin,
  Clock,
  ShieldCheck,
  Ship,
  Compass,
  FileText,
  Waves,
  Calendar,
  Layers,
  ArrowRight,
} from "lucide-react";

export default function SpillDetailsModal({
  spill,
  origin,
  suspects = [],
  forecast = [],
  impact = null,
  onClose,
  onInvestigateVessels,
  onViewReport,
}) {
  if (!spill) return null;

  const lat = spill.centroid?.lat || spill.latitude || 0;
  const lon = spill.centroid?.lon || spill.longitude || 0;
  const conf = Math.round(
    spill.confidence > 1 ? spill.confidence : spill.confidence * 100
  );

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-content panel"
        onClick={(e) => e.stopPropagation()}
      >
        {/* MODAL HEADER */}
        <div className="modal-header">
          <div>
            <div className="case-id-tag">
              CASE #{spill.spillId || spill.id}
            </div>
            <h2>{spill.title || "Spill Incident Details"}</h2>
            <p className="modal-sub">
              {spill.region || "Indian Exclusive Economic Zone (EEZ)"} • Detected via{" "}
              {spill.sensor || "Sentinel-1 SAR"}
            </p>
          </div>
          <button
            type="button"
            className="icon-close-btn"
            onClick={onClose}
            title="Close"
          >
            <X size={20} />
          </button>
        </div>

        {/* MODAL BODY */}
        <div className="modal-body">
          {/* TOP METRIC CARDS */}
          <div className="modal-metrics-grid">
            <div className="metric-card">
              <span className="metric-label">Affected Area</span>
              <strong className="metric-value">
                {spill.areaSqKm || spill.area} km²
              </strong>
              <small>Surface slick footprint</small>
            </div>
            <div className="metric-card">
              <span className="metric-label">AI Segmentation</span>
              <strong className="metric-value text-accent">{conf}%</strong>
              <small>{spill.modelVersion || "UNet_ResNet34_v1"}</small>
            </div>
            <div className="metric-card">
              <span className="metric-label">Severity</span>
              <strong
                className={`metric-value ${
                  spill.severity === "CRITICAL" || spill.severity === "HIGH"
                    ? "text-danger"
                    : "text-warning"
                }`}
              >
                {spill.severity}
              </strong>
              <small>Ecological risk index</small>
            </div>
            <div className="metric-card">
              <span className="metric-label">Status</span>
              <strong className="metric-value text-success">
                {spill.status?.replace("_", " ") || "Under Investigation"}
              </strong>
              <small>Real-time tracking</small>
            </div>
          </div>

          {/* DETAILED SECTIONS */}
          <div className="details-columns">
            {/* LEFT COLUMN: DETECTION & BACKTRACKING */}
            <div className="details-col">
              <div className="details-section">
                <h3>
                  <Layers size={18} /> Detection Telemetry
                </h3>
                <table className="details-table">
                  <tbody>
                    <tr>
                      <td>Coordinates</td>
                      <td>
                        <strong>
                          {lat.toFixed(4)}° N, {lon.toFixed(4)}° E
                        </strong>
                      </td>
                    </tr>
                    <tr>
                      <td>Acquisition Time</td>
                      <td>{spill.detectedAt || "Recent"}</td>
                    </tr>
                    <tr>
                      <td>Satellite Sensor</td>
                      <td>{spill.sensor || "Sentinel-1 SAR IW"}</td>
                    </tr>
                    <tr>
                      <td>Sensor Mode</td>
                      <td>C-band Synthetic Aperture Radar (VV/VH)</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div className="details-section">
                <h3>
                  <Compass size={18} /> Backtracking Origin
                </h3>
                {origin ? (
                  <table className="details-table">
                    <tbody>
                      <tr>
                        <td>Estimated Source Coordinates</td>
                        <td>
                          <strong className="text-cyan">
                            {(
                              origin.estimatedOrigin?.lat || origin.latitude
                            )?.toFixed(4)}
                            ° N,{" "}
                            {(
                              origin.estimatedOrigin?.lon || origin.longitude
                            )?.toFixed(4)}
                            ° E
                          </strong>
                        </td>
                      </tr>
                      <tr>
                        <td>Estimated Source Time</td>
                        <td>
                          {origin.estimatedTime || origin.time || "Unknown"}
                        </td>
                      </tr>
                      <tr>
                        <td>Uncertainty Radius</td>
                        <td>±{origin.uncertaintyKm || 12} km</td>
                      </tr>
                      <tr>
                        <td>Drift Physics Engine</td>
                        <td>Advection: Current + 3% Wind Vector</td>
                      </tr>
                    </tbody>
                  </table>
                ) : (
                  <p className="text-muted">No origin data computed yet.</p>
                )}
              </div>
            </div>

            {/* RIGHT COLUMN: SUSPECTS & ENVIRONMENTAL IMPACT */}
            <div className="details-col">
              <div className="details-section">
                <div className="section-head-flex">
                  <h3>
                    <Ship size={18} /> Top Suspect Vessel
                  </h3>
                  {onInvestigateVessels && (
                    <button
                      type="button"
                      className="text-btn"
                      onClick={() => {
                        onClose();
                        onInvestigateVessels();
                      }}
                    >
                      View all ({suspects.length}) →
                    </button>
                  )}
                </div>

                {suspects.length > 0 ? (
                  <div className="suspect-highlight-box">
                    <div className="suspect-top-row">
                      <div>
                        <strong>{suspects[0].name}</strong>
                        <span>
                          {suspects[0].vesselType || suspects[0].type} • MMSI:{" "}
                          {suspects[0].mmsi}
                        </span>
                      </div>
                      <div className="score-badge-large">
                        <strong>{suspects[0].score}%</strong>
                        <span>Attribution</span>
                      </div>
                    </div>
                    <p className="suspect-explanation">
                      {suspects[0].whySuspicious ||
                        "Vessel trajectory intersects estimated release location and time window."}
                    </p>
                  </div>
                ) : (
                  <p className="text-muted">No candidate vessels recorded.</p>
                )}
              </div>

              <div className="details-section">
                <h3>
                  <Waves size={18} /> Environmental Impact Exposure
                </h3>
                {impact ? (
                  <div className="impact-summary-grid">
                    <div className="impact-chip">
                      <span>Coastal Risk</span>
                      <strong className="text-danger">
                        {impact.coastalRisk || impact.coastal || "CRITICAL"}
                      </strong>
                    </div>
                    <div className="impact-chip">
                      <span>Marine Risk</span>
                      <strong className="text-warning">
                        {impact.marineRisk || impact.marine || "HIGH"}
                      </strong>
                    </div>
                    <div className="impact-chip">
                      <span>Fishing Risk</span>
                      <strong className="text-warning">
                        {impact.fishingRisk || impact.fishing || "MEDIUM"}
                      </strong>
                    </div>
                    <div className="impact-chip">
                      <span>Total Vulnerable Area</span>
                      <strong>
                        {impact.affectedAreaSqKm || impact.affectedArea || 42.6} km²
                      </strong>
                    </div>
                  </div>
                ) : (
                  <p className="text-muted">Impact zones not evaluated.</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* MODAL FOOTER */}
        <div className="modal-footer">
          <button
            type="button"
            className="secondary-btn"
            onClick={onClose}
          >
            Close
          </button>

          <div className="footer-actions-right">
            {onInvestigateVessels && (
              <button
                type="button"
                className="secondary-btn"
                onClick={() => {
                  onClose();
                  onInvestigateVessels();
                }}
              >
                <Ship size={15} /> Suspect Investigation
              </button>
            )}

            {onViewReport && (
              <button
                type="button"
                className="primary-btn"
                onClick={() => {
                  onClose();
                  onViewReport();
                }}
              >
                <FileText size={15} /> Open Investigation Report
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
