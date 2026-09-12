import React from "react";
import { CheckCircle2, CircleDot } from "lucide-react";

const events = [
  ["12:15", "Spill detected from satellite image", true],
  ["12:45", "AI segmentation completed", true],
  ["13:10", "Backtracking analysis completed", true],
  ["14:00", "AIS vessel matching completed", true],
  ["14:30", "Investigation workflow started", false]
];

export default function ActivityPanel() {
  return (
    <div className="panel activity">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">WORKFLOW</span>
          <h2>Recent Activity</h2>
        </div>
      </div>

      <div className="timeline">
        {events.map(([time, text, done], i) => (
          <div className="timeline-item" key={i}>
            <div className="timeline-marker">{done ? <CheckCircle2 size={16} /> : <CircleDot size={16} />}</div>
            <div><span>{time}</span><p>{text}</p></div>
          </div>
        ))}
      </div>
    </div>
  );
}