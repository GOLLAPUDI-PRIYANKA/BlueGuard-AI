import React from "react";
import { AlertTriangle, MapPin, Clock, Activity } from "lucide-react";

export default function SpillOverview({ spill, onInvestigate }) {
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
        <div className="alert-icon"><AlertTriangle size={18} /></div>
        <div>
          <strong>High severity spill</strong>
          <span>Requires investigation</span>
        </div>
      </div>

      <div className="stat-grid">
        <div><span>Area</span><strong>{spill.area} km²</strong></div>
        <div><span>Confidence</span><strong>{spill.confidence}%</strong></div>
      </div>

      <div className="detail-list">
        <div><span><AlertTriangle size={15} /> Severity</span><strong className="text-danger">{spill.severity}</strong></div>
        <div><span><Clock size={15} /> Detected</span><strong>{spill.detectedAt}</strong></div>
        <div><span><MapPin size={15} /> Location</span><strong>{spill.latitude}° N, {spill.longitude}° E</strong></div>
      </div>

      <button className="primary-btn" onClick={onInvestigate}>Investigate Spill <span>→</span></button>
    </div>
  );
}