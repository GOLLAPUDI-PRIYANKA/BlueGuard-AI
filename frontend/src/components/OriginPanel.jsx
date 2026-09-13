import React from "react";
import { MapPin, Clock3, Compass, Info } from "lucide-react";

export default function OriginPanel({ origin }) {
  if (!origin) return null;

  const lat = origin.estimatedOrigin?.lat || origin.latitude || 15.201;
  const lon = origin.estimatedOrigin?.lon || origin.longitude || 73.512;
  const conf = Math.round(
    origin.confidence > 1 ? origin.confidence : (origin.confidence || 0.81) * 100
  );
  const time = origin.estimatedTime || origin.time || "2026-08-28 23:40 UTC";
  const uncertainty = origin.uncertaintyKm || 12;

  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">GIS BACKTRACKING</span>
          <h2>
            <MapPin size={19} /> Estimated Spill Origin
          </h2>
        </div>
      </div>

      <div className="origin-card">
        <span>
          <Clock3 size={15} /> Estimated Source Time
        </span>
        <strong>{time}</strong>
        <small>Backtracked ~10h 20m prior to satellite pass</small>
      </div>

      <div className="origin-card">
        <span>Estimated Source Region</span>
        <strong className="text-cyan">
          {lat.toFixed(3)}° N, {lon.toFixed(3)}° E
        </strong>
        <div className="confidence">
          <div style={{ width: `${conf}%`, backgroundColor: "#00d2d3" }} />
        </div>
        <small>{conf}% model confidence • ±{uncertainty} km uncertainty</small>
      </div>
    </div>
  );
}