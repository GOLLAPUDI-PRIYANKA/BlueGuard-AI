import React, { useEffect, useState } from "react";
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
        width: ${isSelected ? "18px" : "14px"};
        height: ${isSelected ? "18px" : "14px"};
        border-radius: 50%;
        box-shadow: 0 0 0 4px ${isSelected ? "rgba(255, 159, 67, 0.28)" : "rgba(61, 165, 255, 0.2)"};
        border: 2px solid #ffffff;
        transition: all 0.2s ease;
      "></div>
    `,
    iconSize: isSelected ? [18, 18] : [14, 14],
    iconAnchor: isSelected ? [9, 9] : [7, 7],
  });

const originIcon = new L.DivIcon({
  className: "custom-origin-icon",
  html: `
    <div style="
      background: #00d2d3;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 0 0 5px rgba(0, 210, 211, 0.22);
    "></div>
  `,
  iconSize: [16, 16],
  iconAnchor: [8, 8],
});

const spillCentroidIcon = new L.DivIcon({
  className: "custom-spill-icon",
  html: `
    <div style="
      background: #ff4757;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 0 0 6px rgba(255, 71, 87, 0.24);
      animation: pulse 2s infinite;
    "></div>
  `,
  iconSize: [18, 18],
  iconAnchor: [9, 9],
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

// Impact zone color by type
const impactZoneStyle = (zoneType) => {
  switch ((zoneType || "").toUpperCase()) {
    case "COASTAL":
      return { color: "#f39c12", fillColor: "#f39c12", fillOpacity: 0.18, weight: 2, dashArray: "5 5" };
    case "FISHING":
      return { color: "#27ae60", fillColor: "#27ae60", fillOpacity: 0.18, weight: 2, dashArray: "5 5" };
    case "ENVIRONMENTAL":
    default:
      return { color: "#8e44ad", fillColor: "#8e44ad", fillOpacity: 0.18, weight: 2, dashArray: "5 5" };
  }
};

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

function MapViewport({ center, resetKey, onResetView }) {
  const map = useMap();

  useEffect(() => {
    if (onResetView) {
      onResetView(map);
    } else {
      map.setView(center, 10);
    }
  }, [center, map, onResetView, resetKey]);

  return null;
}

export default function MapView({
  spill,
  origin,
  vessels = [],
  forecast = [],
  impact = null,
  selectedVesselId = null,
  onSelectVessel = null,
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

  const centerLat = Number(spill?.centroid?.lat ?? spill?.latitude);
  const centerLon = Number(spill?.centroid?.lon ?? spill?.longitude);

  if (!Number.isFinite(centerLat) || !Number.isFinite(centerLon)) {
    return (
      <div className="map-wrap map-empty">
        <div>
          <strong>No mapped spill location yet</strong>
          <span>Upload an image and run AI detection to center the live map.</span>
        </div>
      </div>
    );
  }

  const center = [centerLat, centerLon];

  // Origin point
  const originLat = Number(origin?.estimatedOrigin?.lat ?? origin?.latitude);
  const originLon = Number(origin?.estimatedOrigin?.lon ?? origin?.longitude);
  const hasOrigin =
    origin &&
    Number.isFinite(originLat) &&
    Number.isFinite(originLon);
  const originCenter = [originLat, originLon];
  const originUncertaintyKm = origin?.uncertaintyKm || 2;

  // Backtrack trail line
  const backtrackTrail = origin?.trail || (hasOrigin ? [originCenter, center] : []);

  // Colors for vessel trajectories
  const vesselColors = ["#ff9f43", "#3da5ff", "#a55eea", "#2ed573", "#e55039"];

  // Helper for map bounds reset
  const handleResetView = (map) => {
    const points = [
      center,
      ...(hasOrigin ? [originCenter] : []),
      ...forecast
        .filter((f) => Number.isFinite(f.lat) && Number.isFinite(f.lon))
        .map((f) => [f.lat, f.lon]),
      ...vessels.flatMap((v) =>
        (v.trajectory || []).map((p) => [Number(p.lat), Number(p.lon)])
      ),
    ].filter((p) => Number.isFinite(p[0]) && Number.isFinite(p[1]));

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
        zoom={10}
        className="map"
        scrollWheelZoom={true}
      >
        {/* Real OpenStreetMap tile layer — no API key required */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />
        <MapViewport
          center={center}
          resetKey={spill?.spillId || spill?.id}
          onResetView={handleResetView}
        />

        {/* -------------------------------------------------- */}
        {/* SPILL DETECTION LAYER                               */}
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
              /* Spill circles fallback */
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
                  Location: {centerLat.toFixed(4)}° N, {centerLon.toFixed(4)}° E
                </div>
              </Popup>
            </Marker>
          </>
        )}

        {/* -------------------------------------------------- */}
        {/* ORIGIN & BACKTRACKING LAYER                         */}
        {/* -------------------------------------------------- */}
        {layers.origin && hasOrigin && (
          <>
            {/* Uncertainty circle */}
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

            {/* Origin center point */}
            <Marker position={originCenter} icon={originIcon}>
              <Popup>
                <div style={{ color: "#111" }}>
                  <strong>Origin Hypocenter</strong>
                  <br />
                  {originLat.toFixed(4)}° N, {originLon.toFixed(4)}° E
                  <br />
                  Estimated Time: {origin.estimatedTime || origin.time}
                </div>
              </Popup>
            </Marker>

            {/* Backtracking drift line */}
            {backtrackTrail.length >= 2 && (
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
            )}
          </>
        )}

        {/* -------------------------------------------------- */}
        {/* FORECAST DRIFT LAYER                                */}
        {/* -------------------------------------------------- */}
        {layers.forecast && forecast && forecast.length > 0 && (
          <>
            {/* Forecast trajectory line */}
            <Polyline
              positions={[
                center,
                ...forecast
                  .filter((f) => Number.isFinite(Number(f.lat)) && Number.isFinite(Number(f.lon)))
                  .map((f) => [Number(f.lat), Number(f.lon)]),
              ]}
              pathOptions={{
                color: "#ff9f43",
                weight: 3,
                dashArray: "4 6",
                opacity: 0.9,
              }}
            />

            {/* Forecast points and dispersion circles */}
            {forecast
              .filter((f) => Number.isFinite(Number(f.lat)) && Number.isFinite(Number(f.lon)))
              .map((f, idx) => (
                <React.Fragment key={`forecast-${f.hours || idx}`}>
                  <Circle
                    center={[Number(f.lat), Number(f.lon)]}
                    radius={Math.sqrt((f.areaSqKm || f.area || 20) / Math.PI) * 1000}
                    pathOptions={{
                      color: "#ff9f43",
                      fillColor: "#ff9f43",
                      fillOpacity: Math.max(0.05, 0.25 - idx * 0.05),
                      weight: 1.5,
                    }}
                  />
                  <Marker
                    position={[Number(f.lat), Number(f.lon)]}
                    icon={forecastPointIcon(f.hours)}
                  >
                    <Popup>
                      <div style={{ color: "#111" }}>
                        <strong>+{f.hours}h Drift Forecast</strong>
                        <br />
                        Predicted Location: {Number(f.lat).toFixed(4)}° N, {Number(f.lon).toFixed(4)}° E
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
        {/* CANDIDATE VESSELS & TRAJECTORIES LAYER              */}
        {/* -------------------------------------------------- */}
        {layers.vessels &&
          vessels.map((v, i) => {
            const isSelected = selectedVesselId === (v.vesselId || v.mmsi || v.id);
            const color = vesselColors[i % vesselColors.length];
            const trajectoryPoints = (v.trajectory || [])
              .map((p) => [Number(p.lat), Number(p.lon)])
              .filter((p) => Number.isFinite(p[0]) && Number.isFinite(p[1]));
            const currentPosition =
              trajectoryPoints.length > 0
                ? trajectoryPoints[trajectoryPoints.length - 1]
                : null;

            if (!currentPosition) return null;

            return (
              <React.Fragment key={v.vesselId || v.mmsi || i}>
                {/* Historical AIS trajectory polyline */}
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
                        <strong>{v.name}</strong> ({v.vesselType || v.vessel_type || v.type || "Unknown"})
                        <br />
                        MMSI: {v.mmsi}
                        <br />
                        Suspect Score: <strong>{v.score}%</strong>
                        <br />
                        Waypoints: {trajectoryPoints.length}
                      </div>
                    </Popup>
                  </Polyline>
                )}

                {/* Vessel position marker */}
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
                      Type: {v.vesselType || v.vessel_type || v.type || "Unknown"} | MMSI: {v.mmsi}
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
        {/* IMPACT ZONES LAYER                                  */}
        {/* -------------------------------------------------- */}
        {layers.impact && impact && (
          <>
            {/* Coastal risk zone */}
            {impact.coastalRisk && impact.coastalRisk !== "LOW" && (
              <Circle
                center={center}
                radius={Math.sqrt((impact.affectedAreaSqKm || 20) / Math.PI) * 1000 * 1.4}
                pathOptions={impactZoneStyle("COASTAL")}
              >
                <Popup>
                  <div style={{ color: "#111" }}>
                    <strong>Coastal Impact Zone</strong>
                    <br />
                    Risk Level: <strong>{impact.coastalRisk}</strong>
                    <br />
                    Affected Area: {impact.affectedAreaSqKm} km²
                  </div>
                </Popup>
              </Circle>
            )}

            {/* Fishing ground risk zone */}
            {impact.fishingRisk && impact.fishingRisk !== "LOW" && (
              <Circle
                center={center}
                radius={Math.sqrt((impact.affectedAreaSqKm || 20) / Math.PI) * 1000 * 1.2}
                pathOptions={impactZoneStyle("FISHING")}
              >
                <Popup>
                  <div style={{ color: "#111" }}>
                    <strong>Fishing Ground Impact Zone</strong>
                    <br />
                    Risk Level: <strong>{impact.fishingRisk}</strong>
                    <br />
                    Affected Area: {impact.affectedAreaSqKm} km²
                  </div>
                </Popup>
              </Circle>
            )}

            {/* Marine / environmental risk zone */}
            {impact.marineRisk && impact.marineRisk !== "LOW" && (
              <Circle
                center={center}
                radius={Math.sqrt((impact.affectedAreaSqKm || 20) / Math.PI) * 1000}
                pathOptions={impactZoneStyle("ENVIRONMENTAL")}
              >
                <Popup>
                  <div style={{ color: "#111" }}>
                    <strong>Marine Environmental Zone</strong>
                    <br />
                    Risk Level: <strong>{impact.marineRisk}</strong>
                    <br />
                    Affected Area: {impact.affectedAreaSqKm} km²
                  </div>
                </Popup>
              </Circle>
            )}
          </>
        )}

        <MapControls center={center} onResetView={handleResetView} />
      </MapContainer>

      {/* -------------------------------------------------- */}
      {/* OVERLAY BADGES & TOOLS                              */}
      {/* -------------------------------------------------- */}
      <div className="map-overlay map-title">
        <span className="danger-dot" />
        Case #{spill?.spillId || spill?.id || "—"}
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
        <div title="Backtracked source region within uncertainty radius">
          <i className="legend-dot origin" /> Estimated Origin
        </div>
        <div title="Simulated advection drift vector">
          <i className="legend-line-backtrack" /> Backtrack Trail
        </div>
        <div title="Vessel position and historical AIS voyage track">
          <i className="legend-dot vessel" /> AIS Vessel Track
        </div>
        <div title="Predicted movement across 24h/48h/72h horizons">
          <i className="legend-dot forecast" /> Forecast Trajectory
        </div>
        <div title="Environmental, coastal and fishing impact zones">
          <i className="legend-dot impact" /> Impact Zones
        </div>
      </div>
    </div>
  );
}
