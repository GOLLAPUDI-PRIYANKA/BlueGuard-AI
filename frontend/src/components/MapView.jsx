import React from "react";
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const vesselIcon = new L.DivIcon({
  className: "vessel-marker",
  html: "🚢",
  iconSize: [28, 28],
  iconAnchor: [14, 14]
});

export default function MapView({ spill, origin, vessels }) {
  const center = [spill.latitude, spill.longitude];

  const vesselPoints = [
    [15.72, 80.05],
    [15.48, 80.62],
    [15.90, 80.42],
    [15.28, 80.08]
  ];

  return (
    <div className="map-wrap">
      <MapContainer center={center} zoom={7} className="map">
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <Circle
          center={center}
          radius={15000}
          pathOptions={{ color: "#ff4545", fillColor: "#ff4545", fillOpacity: 0.34, weight: 2 }}
        />

        <Circle
          center={center}
          radius={6500}
          pathOptions={{ color: "#ff9f43", fillColor: "#ff6b35", fillOpacity: 0.40, weight: 2 }}
        />

        <Marker position={center}>
          <Popup>
            <strong>Oil Spill Detected</strong><br />
            Area: {spill.area} km²<br />
            Confidence: {spill.confidence}%
          </Popup>
        </Marker>

        <Circle
          center={[origin.latitude, origin.longitude]}
          radius={10000}
          pathOptions={{ color: "#35d47a", fillColor: "#35d47a", fillOpacity: 0.20, dashArray: "8 8" }}
        />

        <Marker position={[origin.latitude, origin.longitude]}>
          <Popup>
            <strong>Estimated Origin</strong><br />
            Confidence: {origin.confidence}%
          </Popup>
        </Marker>

        {vesselPoints.map((point, i) => (
          <Marker key={i} position={point} icon={vesselIcon}>
            <Popup>
              <strong>{vessels[i]?.name || `Vessel ${i + 1}`}</strong><br />
              AIS position
            </Popup>
          </Marker>
        ))}

        <Polyline
          positions={[[15.72,80.05], [15.68,80.18], [15.62,80.31]]}
          pathOptions={{ color: "#3da5ff", dashArray: "8 8", weight: 3 }}
        />

        <Polyline
          positions={[[15.90,80.42], [15.80,80.38], [15.62,80.31]]}
          pathOptions={{ color: "#8c7cff", dashArray: "8 8", weight: 3 }}
        />
      </MapContainer>

      <div className="map-overlay map-title">
        <span className="danger-dot" />
        Spill #{spill.id}
        <span className="investigation-badge">Under Investigation</span>
      </div>

      <div className="map-overlay legend">
        <div><i className="legend-dot spill" /> Oil Spill</div>
        <div><i className="legend-dot origin" /> Possible Origin</div>
        <div><i className="legend-line" /> Vessel Trajectory</div>
        <div><i className="legend-dot vessel" /> AIS Vessel</div>
      </div>

      <div className="map-overlay map-tools">
        <button>+</button>
        <button>−</button>
        <button>⌖</button>
      </div>
    </div>
  );
}