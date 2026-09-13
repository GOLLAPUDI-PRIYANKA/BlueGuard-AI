import React from "react";
import { Leaf, Fish, Waves, AlertCircle } from "lucide-react";

export default function ImpactPanel({ impact, onViewReports = null }) {
  if (!impact) return null;

  const marine = impact.marineRisk || impact.marine || "HIGH";
  const fishing = impact.fishingRisk || impact.fishing || "MEDIUM";
  const coastal = impact.coastalRisk || impact.coastal || "CRITICAL";
  const area = impact.affectedAreaSqKm || impact.affectedArea || 42.6;

  const riskClass = (risk) => {
    switch (risk?.toUpperCase()) {
      case "CRITICAL":
        return "text-danger";
      case "HIGH":
        return "text-danger";
      case "MEDIUM":
        return "text-warning";
      case "LOW":
        return "text-success";
      default:
        return "text-muted";
    }
  };

  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">ENVIRONMENTAL ASSESSMENT</span>
          <h2>
            <Leaf size={19} /> Impact Exposure
          </h2>
        </div>
      </div>

      <div className="impact-list">
        <div>
          <span>
            <Waves size={16} /> Coastal Risk
          </span>
          <strong className={riskClass(coastal)}>{coastal}</strong>
        </div>
        <div>
          <span>
            <Fish size={16} /> Fishing Risk
          </span>
          <strong className={riskClass(fishing)}>{fishing}</strong>
        </div>
        <div>
          <span>
            <Leaf size={16} /> Marine Ecological Risk
          </span>
          <strong className={riskClass(marine)}>{marine}</strong>
        </div>
      </div>

      <div className="affected">
        <span>Vulnerable Area</span>
        <strong>{area} km²</strong>
      </div>
    </div>
  );
}