import React from "react";
import { CloudSun, ChevronRight } from "lucide-react";

export default function ForecastPanel({ forecast = [], onViewForecast = null }) {
  return (
    <div className="panel">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">OCEAN DRIFT MODEL</span>
          <h2>
            <CloudSun size={19} /> Spill Forecast
          </h2>
        </div>
        {onViewForecast && (
          <button
            type="button"
            className="text-btn"
            onClick={onViewForecast}
          >
            Detailed View →
          </button>
        )}
      </div>

      <div className="forecast-list">
        {forecast.map((item, index) => (
          <div
            className={`forecast-item f${index}`}
            key={item.hours}
            onClick={onViewForecast}
            style={{ cursor: onViewForecast ? "pointer" : "default" }}
          >
            <div className="forecast-hour">+{item.hours}h</div>
            <div>
              <strong>
                {item.status || `Predicted Spread: ${item.areaSqKm || item.area} km²`}
              </strong>
              <span>
                {item.lat && item.lon
                  ? `${item.lat.toFixed(2)}° N, ${item.lon.toFixed(2)}° E`
                  : `Estimated Area: ${item.areaSqKm || item.area} km²`}
              </span>
            </div>
            {onViewForecast && <ChevronRight size={14} className="text-muted" />}
          </div>
        ))}
      </div>
    </div>
  );
}
