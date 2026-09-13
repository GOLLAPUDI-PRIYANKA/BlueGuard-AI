import React from "react";
import { Ship, ChevronRight, AlertCircle } from "lucide-react";

export default function VesselList({
  vessels = [],
  selectedVesselId = null,
  onSelectVessel = null,
  onViewAll = null,
}) {
  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">AIS ATTRIBUTION</span>
          <h2>
            <Ship size={19} /> Ranked Candidate Vessels
          </h2>
        </div>
        {onViewAll && (
          <button
            type="button"
            className="text-btn"
            onClick={onViewAll}
          >
            Investigate all ({vessels.length}) →
          </button>
        )}
      </div>

      <div className="table-head">
        <span># / Vessel</span>
        <span>MMSI</span>
        <span>Attribution</span>
      </div>

      {vessels.length === 0 ? (
        <p className="text-muted" style={{ padding: "16px 0" }}>
          No candidate vessels correlated for this sector.
        </p>
      ) : (
        vessels.slice(0, 5).map((v, index) => {
          const isSelected =
            selectedVesselId === (v.vesselId || v.mmsi || v.id);
          const score = Math.round(v.score || 0);
          const priority =
            v.evidence?.investigationPriority ||
            (score > 75 ? "High" : score > 50 ? "Medium" : "Low");

          return (
            <div
              className={`vessel-row ${isSelected ? "selected-row" : ""}`}
              key={v.vesselId || v.mmsi || index}
              onClick={() =>
                onSelectVessel &&
                onSelectVessel(v.vesselId || v.mmsi || v.id)
              }
              title="Click to highlight track on GIS map"
            >
              <div className="vessel-name">
                <div className={`rank ${index === 0 ? "rank-top" : ""}`}>
                  {index + 1}
                </div>
                <div>
                  <strong>{v.name}</strong>
                  <span>
                    {v.vesselType || v.type || "Cargo"} • {priority} Priority
                  </span>
                </div>
              </div>

              <span className="mmsi">{v.mmsi}</span>

              <div className="score-cell">
                <strong
                  className={
                    score > 75
                      ? "text-danger"
                      : score > 50
                      ? "text-warning"
                      : "text-muted"
                  }
                >
                  {score}%
                </strong>
                <div className="score-track">
                  <div
                    style={{
                      width: `${score}%`,
                      backgroundColor:
                        score > 75
                          ? "#ff4757"
                          : score > 50
                          ? "#ff9f43"
                          : "#3da5ff",
                    }}
                  />
                </div>
              </div>

              <ChevronRight size={16} className="chevron" />
            </div>
          );
        })
      )}
    </div>
  );
}