import React from "react";
import { Leaf, Fish, Waves } from "lucide-react";

function riskClass(risk) {
  const value = String(risk || "LOW").toUpperCase();

  if (value === "CRITICAL" || value === "HIGH") {
    return "text-danger";
  }

  if (value === "MEDIUM") {
    return "text-warning";
  }

  return "text-success";
}

export default function ImpactPanel({ impact }) {
  const marineRisk = impact?.marineRisk ?? "LOW";
  const fishingRisk = impact?.fishingRisk ?? "LOW";
  const coastalRisk = impact?.coastalRisk ?? "LOW";
  const affectedArea = Number(impact?.affectedAreaSqKm ?? 0).toFixed(1);

  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">ENVIRONMENT</span>
          <h2><Leaf size={19} /> Impact</h2>
        </div>
      </div>

      <div className="impact-list">
        <div>
          <span><Waves size={16} /> Marine risk</span>
          <strong className={riskClass(marineRisk)}>
            {marineRisk}
          </strong>
        </div>

        <div>
          <span><Fish size={16} /> Fishing risk</span>
          <strong className={riskClass(fishingRisk)}>
            {fishingRisk}
          </strong>
        </div>

        <div>
          <span><Leaf size={16} /> Coastal risk</span>
          <strong className={riskClass(coastalRisk)}>
            {coastalRisk}
          </strong>
        </div>
      </div>

      <div className="affected">
        <span>Affected area</span>
        <strong>{affectedArea} km²</strong>
      </div>
    </div>
  );
}
