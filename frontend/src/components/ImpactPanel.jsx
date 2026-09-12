import React from "react";
import { Leaf, Fish, Waves } from "lucide-react";

export default function ImpactPanel({ impact }) {
  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">ENVIRONMENT</span>
          <h2><Leaf size={19} /> Impact</h2>
        </div>
      </div>

      <div className="impact-list">
        <div><span><Waves size={16} /> Marine risk</span><strong className="text-danger">{impact.marine}</strong></div>
        <div><span><Fish size={16} /> Fishing risk</span><strong className="text-warning">{impact.fishing}</strong></div>
        <div><span><Leaf size={16} /> Coastal risk</span><strong className="text-success">{impact.coastal}</strong></div>
      </div>

      <div className="affected">
        <span>Affected area</span>
        <strong>{impact.affectedArea} km²</strong>
      </div>
    </div>
  );
}