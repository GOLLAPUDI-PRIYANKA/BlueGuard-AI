import React from "react";
import { Ship, ChevronRight } from "lucide-react";

export default function VesselList({ vessels = [] }) {
  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">AIS ANALYSIS</span>
          <h2><Ship size={19} /> Potential Vessels</h2>
        </div>
        <button className="text-btn">View all →</button>
      </div>

      <div className="table-head">
        <span># / Vessel</span>
        <span>Vessel ID</span>
        <span>Score</span>
      </div>

      {vessels.length === 0 ? (
        <div className="empty-state">No candidate vessels available.</div>
      ) : (
        vessels.map((v, index) => (
          <div className="vessel-row" key={v.vesselId || index}>
            <div className="vessel-name">
              <div className="rank">{index + 1}</div>
              <div>
                <strong>{v.name || "Unknown Vessel"}</strong>
                <span>
                  {v.evidence
                    ? `${Number(v.evidence.distanceKm ?? 0).toFixed(1)} km from source`
                    : "AIS candidate"}
                </span>
              </div>
            </div>

            <span className="mmsi">{v.vesselId || "Unknown"}</span>

            <div className="score-cell">
              <strong>{Math.round(v.score ?? 0)}%</strong>
              <div className="score-track">
                <div style={{ width: `${Math.min(100, Math.max(0, v.score ?? 0))}%` }} />
              </div>
            </div>

            <ChevronRight size={16} className="chevron" />
          </div>
        ))
      )}
    </div>
  );
}
