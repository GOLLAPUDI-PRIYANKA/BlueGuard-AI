import React from "react";
import { Ship, ChevronRight } from "lucide-react";

export default function VesselList({ vessels }) {
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
        <span># / Vessel</span><span>MMSI</span><span>Score</span>
      </div>

      {vessels.map((v, index) => (
        <div className="vessel-row" key={v.id}>
          <div className="vessel-name">
            <div className="rank">{index + 1}</div>
            <div><strong>{v.name}</strong><span>{v.type}</span></div>
          </div>
          <span className="mmsi">{v.mmsi}</span>
          <div className="score-cell">
            <strong>{v.score}%</strong>
            <div className="score-track"><div style={{ width: `${v.score}%` }} /></div>
          </div>
          <ChevronRight size={16} className="chevron" />
        </div>
      ))}
    </div>
  );
}