import React from "react";
import { CloudSun } from "lucide-react";

export default function ForecastPanel({ forecast }) {
  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">DRIFT MODEL</span>
          <h2><CloudSun size={19} /> Forecast</h2>
        </div>
        <button className="text-btn">View →</button>
      </div>

      <div className="forecast-list">
        {forecast.map((item, index) => (
          <div className={`forecast-item f${index}`} key={item.hours}>
            <div className="forecast-hour">{item.hours}h</div>
            <div><strong>Predicted spread</strong><span>Estimated area: {item.area} km²</span></div>
          </div>
        ))}
      </div>
    </div>
  );
}