import React from "react";
import { MapPin, Clock3 } from "lucide-react";

export default function OriginPanel({ origin }) {
  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">BACKTRACKING</span>
          <h2><MapPin size={19} /> Origin</h2>
        </div>
      </div>

      <div className="origin-card">
        <span><Clock3 size={15} /> Estimated source time</span>
        <strong>{origin.time}</strong>
        <small>± 2 hours</small>
      </div>

      <div className="origin-card">
        <span>Possible source region</span>
        <strong>{origin.latitude}° N, {origin.longitude}° E</strong>
        <div className="confidence"><div style={{ width: `${origin.confidence}%` }} /></div>
        <small>{origin.confidence}% confidence</small>
      </div>
    </div>
  );
}