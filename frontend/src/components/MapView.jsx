import React from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Circle,
  Polyline,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const vesselIcon = new L.DivIcon({
  className: "vessel-marker",
  html: "🚢",
  iconSize: [28, 28],
  iconAnchor: [14, 14],
});

export default function MapView({
  spill,
  origin,
  vessels = [],
  trajectories = {},
}) {
  const spillLat = spill?.centroid?.lat;
  const spillLon = spill?.centroid?.lon;

  const originLat = origin?.estimatedOrigin?.lat;
  const originLon = origin?.estimatedOrigin?.lon;

  const center =
    spillLat !== undefined && spillLon !== undefined
      ? [spillLat, spillLon]
      : [15.462, 73.845];

  const spillConfidence = Math.round((spill?.confidence ?? 0) * 100);
  const spillArea = Number(spill?.areaSqKm ?? 0).toFixed(1);
  const originConfidence = Math.round((origin?.confidence ?? 0) * 100);

  return (
    <div className="map-wrap">
      <MapContainer center={center} zoom={7} className="map">
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {spillLat !== undefined && spillLon !== undefined && (
          <>
            <Circle
              center={center}
              radius={15000}
              pathOptions={{
                color: "#ff4545",
                fillColor: "#ff4545",
                fillOpacity: 0.34,
                weight: 2,
              }}
            />

            <Circle
              center={center}
              radius={6500}
              pathOptions={{
                color: "#ff9f43",
                fillColor: "#ff6b35",
                fillOpacity: 0.40,
                weight: 2,
              }}
            />

            <Marker position={center}>
              <Popup>
                <strong>Oil Spill Detected</strong>
                <br />
                Area: {spillArea} km²
                <br />
                Confidence: {spillConfidence}%
              </Popup>
            </Marker>
          </>
        )}

        {originLat !== undefined && originLon !== undefined && (
          <>
            <Circle
              center={[originLat, originLon]}
              radius={10000}
              pathOptions={{
                color: "#35d47a",
                fillColor: "#35d47a",
                fillOpacity: 0.20,
                dashArray: "8 8",
              }}
            />

            <Marker position={[originLat, originLon]}>
              <Popup>
                <strong>Estimated Origin</strong>
                <br />
                Confidence: {originConfidence}%
              </Popup>
            </Marker>
          </>
        )}

        {vessels.map((v) => {
          const trajectory = trajectories[v.vesselId]?.path || [];

          if (trajectory.length === 0) {
            return null;
          }

          const latest = trajectory[trajectory.length - 1];

          if (
            latest?.lat === undefined ||
            latest?.lon === undefined
          ) {
            return null;
          }

          const positions = trajectory
            .filter(
              (point) =>
                point?.lat !== undefined &&
                point?.lon !== undefined
            )
            .map((point) => [point.lat, point.lon]);

          return (
            <React.Fragment key={v.vesselId}>
              <Marker
                position={[latest.lat, latest.lon]}
                icon={vesselIcon}
              >
                <Popup>
                  <strong>{v.name || "Unknown Vessel"}</strong>
                  <br />
                  Vessel ID: {v.vesselId}
                  <br />
                  Score: {Math.round(v.score ?? 0)}%
                </Popup>
              </Marker>

              {positions.length >= 2 && (
                <Polyline
                  positions={positions}
                  pathOptions={{
                    color: "#3da5ff",
                    dashArray: "8 8",
                    weight: 3,
                  }}
                />
              )}
            </React.Fragment>
          );
        })}
      </MapContainer>

      <div className="map-overlay map-title">
        <span className="danger-dot" />
        Spill #{spill?.spillId || "—"}
        <span className="investigation-badge">
          Under Investigation
        </span>
      </div>

      <div className="map-overlay legend">
        <div>
          <i className="legend-dot spill" /> Oil Spill
        </div>

        <div>
          <i className="legend-dot origin" /> Possible Origin
        </div>

        <div>
          <i className="legend-line" /> Vessel Trajectory
        </div>

        <div>
          <i className="legend-dot vessel" /> AIS Vessel
        </div>
      </div>

      <div className="map-overlay map-tools">
        <button>+</button>
        <button>−</button>
        <button>⌖</button>
      </div>
    </div>
  );
}
