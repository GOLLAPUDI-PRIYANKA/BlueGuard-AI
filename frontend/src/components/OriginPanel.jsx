import React from "react";
import { MapPin, Clock3 } from "lucide-react";

export default function OriginPanel({ origin }) {
  const confidence = Math.round((origin?.confidence ?? 0) * 100);
  const latitude = origin?.estimatedOrigin?.lat;
  const longitude = origin?.estimatedOrigin?.lon;

  const estimatedTime = origin?.estimatedTime
    ? new Date(origin.estimatedTime).toLocaleString()
    : "Unknown";

  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">BACKTRACKING</span>
          <h2>
            <MapPin size={19} /> Origin
          </h2>
        </div>
      </div>

      <div className="origin-card">
        <span>
          <Clock3 size={15} /> Estimated source time
        </span>

        <strong>{estimatedTime}</strong>

        <small>Estimated by drift backtracking</small>
      </div>

      <div className="origin-card">
        <span>Possible source region</span>

        <strong>
          {latitude !== undefined && longitude !== undefined
            ? `${latitude.toFixed(4)}° N, ${longitude.toFixed(4)}° E`
            : "Unknown"}
        </strong>

        <div className="confidence">
          <div style={{ width: `${confidence}%` }} />
        </div>

        <small>{confidence}% confidence</small>
      </div>
    </div>
  );
}
