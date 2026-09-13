import React, { useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Circle,
  Polygon,
  Polyline,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Custom Leaflet DivIcons
const createVesselIcon = (color = "#3da5ff", isSelected = false) =>
  new L.DivIcon({
    className: "custom-vessel-icon",
    html: `
      <div style="
        background: ${isSelected ? "#ff9f43" : color};
        width: ${isSelected ? "32px" : "26px"};
        height: ${isSelected ? "32px" : "26px"};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: ${isSelected ? "16px" : "13px"};
        box-shadow: 0 0 12px ${isSelected ? "rgba(255, 159, 67, 0.8)" : "rgba(61, 165, 255, 0.6)"};
        border: 2px solid #ffffff;
        transition: all 0.2s ease;
      ">🚢</div>
    `,
    iconSize: isSelected ? [32, 32] : [26, 26],
    iconAnchor: isSelected ? [16, 16] : [13, 13],
  });

const originIcon = new L.DivIcon({
  className: "custom-origin-icon",
  html: `
    <div style="
      background: #00d2d3;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #0c1929;
      font-size: 13px;
      font-weight: bold;
      border: 2px solid white;
      box-shadow: 0 0 10px rgba(0, 210, 211, 0.8);
    ">⊙</div>
  `,
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

const spillCentroidIcon = new L.DivIcon({
  className: "custom-spill-icon",
  html: `
    <div style="
      background: #ff4757;
      width: 26px;
      height: 26px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 14px;
      border: 2px solid white;
      box-shadow: 0 0 12px rgba(255, 71, 87, 0.8);
      animation: pulse 2s infinite;
    ">⚠</div>
  `,
  iconSize: [26, 26],
  iconAnchor: [13, 13],
});

const forecastPointIcon = (hours) =>
  new L.DivIcon({
    className: "custom-forecast-icon",
    html: `
      <div style="
        background: #ff9f43;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #111;
        font-size: 10px;
        font-weight: 700;
        border: 2px solid white;
        box-shadow: 0 0 8px rgba(255, 159, 67, 0.8);
      ">+${hours}h</div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });

// Map Controller for interactive buttons
function MapControls({ center, onResetView }) {
  const map = useMap();

  return (
    <div className="map-overlay map-tools">
      <button
        type="button"
        title="Zoom In"
        onClick={() => map.zoomIn()}
      >
        +
      </button>
      <button
        type="button"
        title="Zoom Out"
        onClick={() => map.zoomOut()}
      >
        −
      </button>
      <button
        type="button"
        title="Fit All Features"
        onClick={() => {
          if (onResetView) onResetView(map);
          else map.setView(center, 9);
        }}
      >
        ⌖
      </button>
    </div>
  );
}

export default function MapView({
  spill,
  origin,
  vessels = [],
  forecast = [],
  impact = null,
  selectedVesselId = null,
  onSelectVessel = null,
  activeLayer = "all",
}) {
  const [layers, setLayers] = useState({
    spill: true,
    origin: true,
    vessels: true,
    forecast: true,
    impact: true,
  });

  const toggleLayer = (layerName) => {
    setLayers((prev) => ({ ...prev, [layerName]: !prev[layerName] }));
  };

  const centerLat = spill?.centroid?.lat || spill?.latitude || 15.462;
  const centerLon = spill?.centroid?.lon || spill?.longitude || 73.845;
  const center = [centerLat, centerLon];

  // Origin point
  const originLat = origin?.estimatedOrigin?.lat || origin?.latitude || 15.201;
  const originLon = origin?.estimatedOrigin?.lon || origin?.longitude || 73.512;
  const originCenter = [originLat, originLon];
  const originUncertaintyKm = origin?.uncertaintyKm || 12;

  // Backtrack trail line
  const backtrackTrail = origin?.trail || [
    [originLat, originLon],
    [centerLat, centerLon],
  ];

  // Colors for vessel trajectories
  const vesselColors = ["#ff9f43", "#3da5ff", "#a55eea", "#2ed573", "#e55039"];

  // Helper for map bounds reset
  const handleResetView = (map) => {
    const points = [
      center,
      originCenter,
      ...forecast.map((f) => [f.lat, f.lon]),
      ...vessels.flatMap((v) =>
        (v.trajectory || []).map((p) => [p.lat, p.lon])
      ),
    ].filter((p) => Boolean(p[0]) && Boolean(p[1]));

    if (points.length > 0) {
      const bounds = L.latLngBounds(points);
      map.fitBounds(bounds, { padding: [40, 40] });
    } else {
      map.setView(center, 8);
    }
  };

  return (
    <div className="map-wrap">
      <MapContainer
        center={center}
        zoom={8}
        className="map"
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* -------------------------------------------------- */}
        {/* SPILL DETECTION LAYER */}
        {/* -------------------------------------------------- */}
        {layers.spill && (
          <>
            {/* Spill polygon if available */}
            {spill?.polygon && spill.polygon.length > 0 ? (
              <Polygon
                positions={spill.polygon}
                pathOptions={{
                  color: "#ff4757",
                  fillColor: "#ff4757",
                  fillOpacity: 0.45,
                  weight: 2,
                }}
              >
                <Popup>
                  <div style={{ color: "#111" }}>
                    <strong>Detected Oil Spill Polygon</strong>
                    <br />
                    ID: <strong>{spill.spillId || spill.id}</strong>
                    <br />
                    Area: {spill.areaSqKm || spill.area} km²
                    <br />
                    Confidence: {Math.round((spill.confidence > 1 ? spill.confidence : spill.confidence * 100))}%
                    <br />
                    Severity: {spill.severity}
                  </div>
                </Popup>
              </Polygon>
            ) : (
              /* Spill Circles fallback */
              <>
                <Circle
                  center={center}
                  radius={Math.sqrt((spill?.areaSqKm || spill?.area || 12.5) / Math.PI) * 1000}
                  pathOptions={{
                    color: "#ff4757",
                    fillColor: "#ff4757",
                    fillOpacity: 0.35,
                    weight: 2,
                  }}
                />
                <Circle
                  center={center}
                  radius={2000}
                  pathOptions={{
                    color: "#ff6b81",
                    fillColor: "#ff4757",
                    fillOpacity: 0.6,
                    weight: 2,
                  }}
                />
              </>
            )}

            {/* Spill Centroid Marker */}
            <Marker position={center} icon={spillCentroidIcon}>
              <Popup>
                <div style={{ color: "#111" }}>
                  <strong>{spill?.title || "Oil Spill Detected"}</strong>
                  <br />
                  ID: <strong>{spill?.spillId || spill?.id}</strong>
                  <br />
                  Area: {spill?.areaSqKm || spill?.area} km²
                  <br />
                  Confidence: {Math.round((spill?.confidence > 1 ? spill?.confidence : spill?.confidence * 100))}%
                  <br />
                  Severity: <strong>{spill?.severity}</strong>
                  <br />
                  Location: {centerLat.toFixed(3)}° N, {centerLon.toFixed(3)}° E
                </div>
              </Popup>
            </Marker>
          </>
        )}

        {/* -------------------------------------------------- */}
        {/* ORIGIN & BACKTRACKING LAYER */}
        {/* -------------------------------------------------- */}
        {layers.origin && origin && (
          <>
            {/* Uncertainty Ellipse / Circle */}
            <Circle
              center={originCenter}
              radius={originUncertaintyKm * 1000}
              pathOptions={{
                color: "#00d2d3",
                fillColor: "#00d2d3",
                fillOpacity: 0.2,
                weight: 2,
                dashArray: "6 6",
              }}
            >
              <Popup>
                <div style={{ color: "#111" }}>
                  <strong>Estimated Spill Origin Area</strong>
                  <br />
                  Source Time: {origin.estimatedTime || origin.time}
                  <br />
                  Uncertainty Radius: ±{originUncertaintyKm} km
                  <br />
                  Confidence: {Math.round((origin.confidence > 1 ? origin.confidence : origin.confidence * 100))}%
                  <br />
                  Method: Advection Backtracking
                </div>
              </Popup>
            </Circle>

            {/* Origin Center Point Marker */}
            <Marker position={originCenter} icon={originIcon}>
              <Popup>
                <div style={{ color: "#111" }}>
                  <strong>Origin Hypocenter</strong>
                  <br />
                  Coordinates: {originLat.toFixed(3)}° N, {originLon.toFixed(3)}° E
                  <br />
                  Estimated Time: {origin.estimatedTime || origin.time}
                </div>
              </Popup>
            </Marker>

            {/* Backtracking Drift Line */}
            <Polyline
              positions={backtrackTrail}
              pathOptions={{
                color: "#ff6b81",
                weight: 3,
                dashArray: "6 8",
                opacity: 0.85,
              }}
            >
              <Popup>
                <div style={{ color: "#111" }}>
                  <strong>Backtracking Advection Vector</strong>
                  <br />
                  Simulated ocean drift trajectory from origin to detection
                </div>
              </Popup>
            </Polyline>
          </>
        )}

        {/* -------------------------------------------------- */}
        {/* FORECAST DRIFT LAYER */}
        {/* -------------------------------------------------- */}
        {layers.forecast && forecast && forecast.length > 0 && (
          <>
            {/* Forecast trajectory line */}
            <Polyline
              positions={[
                center,
                ...forecast.map((f) => [f.lat, f.lon]),
              ]}
              pathOptions={{
                color: "#ff9f43",
                weight: 3,
                dashArray: "4 6",
                opacity: 0.9,
              }}
            />

            {/* Forecast points and dispersion circles */}
            {forecast.map((f, idx) => (
              <React.Fragment key={`forecast-${f.hours || idx}`}>
                <Circle
                  center={[f.lat, f.lon]}
                  radius={Math.sqrt((f.areaSqKm || f.area || 20) / Math.PI) * 1000}
                  pathOptions={{
                    color: "#ff9f43",
                    fillColor: "#ff9f43",
                    fillOpacity: 0.25 - idx * 0.05,
                    weight: 1.5,
                  }}
                />
                <Marker
                  position={[f.lat, f.lon]}
                  icon={forecastPointIcon(f.hours)}
                >
                  <Popup>
                    <div style={{ color: "#111" }}>
                      <strong>+{f.hours}h Drift Forecast</strong>
                      <br />
                      Predicted Location: {f.lat.toFixed(3)}° N, {f.lon.toFixed(3)}° E
                      <br />
                      Predicted Area: {f.areaSqKm || f.area} km²
                      <br />
                      Horizon Time: {f.time}
                      <br />
                      Status: {f.status || "Active Forecast"}
                    </div>
                  </Popup>
                </Marker>
              </React.Fragment>
            ))}
          </>
        )}

        {/* -------------------------------------------------- */}
        {/* CANDIDATE VESSELS & TRAJECTORIES LAYER */}
        {/* -------------------------------------------------- */}
        {layers.vessels &&
          vessels.map((v, i) => {
            const isSelected = selectedVesselId === (v.vesselId || v.mmsi || v.id);
            const color = vesselColors[i % vesselColors.length];
            const trajectoryPoints = (v.trajectory || []).map((p) => [p.lat, p.lon]);
            const currentPosition =
              trajectoryPoints.length > 0
                ? trajectoryPoints[trajectoryPoints.length - 1]
                : [centerLat + (i + 1) * 0.04, centerLon - (i + 1) * 0.05];

            return (
              <React.Fragment key={v.vesselId || v.mmsi || i}>
                {/* Historical AIS Trajectory Polyline */}
                {trajectoryPoints.length > 1 && (
                  <Polyline
                    positions={trajectoryPoints}
                    pathOptions={{
                      color: isSelected ? "#ff9f43" : color,
                      weight: isSelected ? 5 : 2.5,
                      opacity: isSelected ? 1 : 0.75,
                      dashArray: isSelected ? undefined : "6 6",
                    }}
                    eventHandlers={{
                      click: () => onSelectVessel && onSelectVessel(v.vesselId || v.mmsi || v.id),
                    }}
                  >
                    <Popup>
                      <div style={{ color: "#111" }}>
                        <strong>{v.name}</strong> ({v.vesselType || v.type})
                        <br />
                        MMSI: {v.mmsi}
                        <br />
                        Suspect Score: <strong>{v.score}%</strong>
                        <br />
                        Waypoint Count: {trajectoryPoints.length}
                      </div>
                    </Popup>
                  </Polyline>
                )}

                {/* Vessel Position Marker */}
                <Marker
                  position={currentPosition}
                  icon={createVesselIcon(color, isSelected)}
                  eventHandlers={{
                    click: () => onSelectVessel && onSelectVessel(v.vesselId || v.mmsi || v.id),
                  }}
                >
                  <Popup>
                    <div style={{ color: "#111" }}>
                      <strong>{v.name}</strong>
                      <br />
                      Type: {v.vesselType || v.type} | MMSI: {v.mmsi}
                      <br />
                      Attribution Score: <strong>{v.score}%</strong>
                      <br />
                      {v.evidence?.distanceKm !== undefined && (
                        <>Distance to Origin: {v.evidence.distanceKm} km<br /></>
                      )}
                      {v.evidence?.investigationPriority && (
                        <>Priority: <strong>{v.evidence.investigationPriority}</strong><br /></>
                      )}
                      <button
                        type="button"
                        style={{
                          marginTop: "6px",
                          padding: "4px 8px",
                          background: "#0052cc",
                          color: "white",
                          border: "none",
                          borderRadius: "4px",
                          cursor: "pointer",
                          fontSize: "11px",
                        }}
                        onClick={() => onSelectVessel && onSelectVessel(v.vesselId || v.mmsi || v.id)}
                      >
                        Investigate Vessel →
                      </button>
                    </div>
                  </Popup>
                </Marker>
              </React.Fragment>
            );
          })}

        {/* -------------------------------------------------- */}
        {/* IMPACT ZONES LAYER */}
        {/* -------------------------------------------------- */}
        {layers.impact && impact?.zones && (
          <>
            {/* Visual representation of coastal impact along Goa coastline */}
            <Polygon
              positions={[
                [15.65, 73.72],
                [15.45, 73.78],
                [15.20, 73.92],
                [15.10, 73.98],
                [15.10, 74.05],
                [15.65, 73.85],
              ]}
              pathOptions={{
                color: "#ff4757",
                fillColor: "#ff4757",
                fillOpacity: 0.15,
                weight: 1.5,
                dashArray: "4 4",
              }}
            >
              <Popup>
                <div style={{ color: "#111" }}>
                  <strong>Vulnerable Coastal Zone</strong>
                  <br />
                  Risk Level: <strong style={{ color: "#d63031" }}>CRITICAL</strong>
                  <br />
                  Affected Shoreline: Goa Beaches & Touristic Fairways
                </div>
              </Popup>
            </Polygon>
          </>
        )}

        <MapControls center={center} onResetView={handleResetView} />
      </MapContainer>

      {/* -------------------------------------------------- */}
      {/* OVERLAY BADGES & TOOLS */}
      {/* -------------------------------------------------- */}
      <div className="map-overlay map-title">
        <span className="danger-dot" />
        Case #{spill?.spillId || spill?.id || "SP101"}
        <span className="investigation-badge">
          {spill?.status || "Under Investigation"}
        </span>
      </div>

      {/* Layer Toggles */}
      <div className="map-overlay layer-toggles">
        <button
          type="button"
          className={`layer-btn ${layers.spill ? "active" : ""}`}
          onClick={() => toggleLayer("spill")}
        >
          Spill Polygon
        </button>
        <button
          type="button"
          className={`layer-btn ${layers.origin ? "active" : ""}`}
          onClick={() => toggleLayer("origin")}
        >
          Origin & Drift
        </button>
        <button
          type="button"
          className={`layer-btn ${layers.vessels ? "active" : ""}`}
          onClick={() => toggleLayer("vessels")}
        >
          Vessels & Tracks
        </button>
        <button
          type="button"
          className={`layer-btn ${layers.forecast ? "active" : ""}`}
          onClick={() => toggleLayer("forecast")}
        >
          Forecast (+72h)
        </button>
        <button
          type="button"
          className={`layer-btn ${layers.impact ? "active" : ""}`}
          onClick={() => toggleLayer("impact")}
        >
          Impact Zones
        </button>
      </div>

      {/* Interactive Legend */}
      <div className="map-overlay legend">
        <div title="Observed slick detection centroid and contour">
          <i className="legend-dot spill" /> Oil Spill Area
        </div>
        <div title="Backtracked source region within 12km uncertainty radius">
          <i className="legend-dot origin" /> Estimated Origin (±12km)
        </div>
        <div title="Simulated advection drift vector">
          <i className="legend-line-backtrack" /> Backtrack Trail
        </div>
        <div title="Vessel position and historical voyage track">
          <i className="legend-dot vessel" /> AIS Vessel Track
        </div>
        <div title="Predicted movement across 24h/48h/72h horizons">
          <i className="legend-dot forecast" /> Forecast Trajectory
        </div>
      </div>
    </div>
  );
}