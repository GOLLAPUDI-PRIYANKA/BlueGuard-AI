import React from "react";
import { CheckCircle2, CircleDot, Clock } from "lucide-react";

export default function ActivityPanel({
  investigationCompleted = true,
  onNavigateTo = null,
}) {
  const events = [
    {
      time: "10:00 UTC",
      text: "Sentinel-1 SAR image acquired & preprocessed",
      done: true,
    },
    {
      time: "10:05 UTC",
      text: "AI U-Net segmentation: 12.5 km² slick identified (91% conf)",
      done: true,
    },
    {
      time: "10:12 UTC",
      text: "Backtracking advection model estimated origin (15.201° N, 73.512° E)",
      done: true,
    },
    {
      time: "10:18 UTC",
      text: "AIS candidate correlation: 3 vessels identified in ±60m window",
      done: true,
    },
    {
      time: "10:24 UTC",
      text: "Attribution engine ranked MV Ocean Pioneer (#1 with 92.4% score)",
      done: true,
    },
    {
      time: "10:30 UTC",
      text: "+24h, +48h, +72h hydrodynamic drift forecast computed",
      done: investigationCompleted,
    },
  ];

  return (
    <div className="panel activity">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">WORKFLOW PROGRESSION</span>
          <h2>Investigation Pipeline</h2>
        </div>
        <span className="text-muted text-sm">
          <Clock size={13} /> Active Case
        </span>
      </div>

      <div className="timeline">
        {events.map((event, i) => (
          <div className="timeline-item" key={i}>
            <div className="timeline-marker">
              {event.done ? (
                <CheckCircle2 size={16} className="text-success" />
              ) : (
                <CircleDot size={16} className="text-muted" />
              )}
            </div>
            <div>
              <span>{event.time}</span>
              <p>{event.text}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}