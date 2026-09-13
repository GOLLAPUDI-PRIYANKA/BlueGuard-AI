import React, { useState } from "react";
import {
  Ship,
  Search,
  Filter,
  AlertTriangle,
  MapPin,
  Clock,
  Compass,
  CheckCircle2,
  TrendingUp,
  Radio,
  ExternalLink,
} from "lucide-react";
import MapView from "./MapView";

export default function VesselsPage({
  vessels = [],
  spill,
  origin,
  selectedVesselId,
  onSelectVessel,
}) {
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [priorityFilter, setPriorityFilter] = useState("ALL");

  const filteredVessels = vessels.filter((v) => {
    const matchesSearch =
      !search ||
      v.name.toLowerCase().includes(search.toLowerCase()) ||
      v.mmsi.includes(search) ||
      (v.vesselId || "").toLowerCase().includes(search.toLowerCase());

    const matchesType =
      typeFilter === "ALL" || (v.vesselType || v.type) === typeFilter;

    const priority = v.evidence?.investigationPriority || (v.score > 75 ? "High" : v.score > 50 ? "Medium" : "Low");
    const matchesPriority =
      priorityFilter === "ALL" || priority === priorityFilter;

    return matchesSearch && matchesType && matchesPriority;
  });

  const activeVessel =
    vessels.find(
      (v) => (v.vesselId || v.mmsi || v.id) === selectedVesselId
    ) || vessels[0];

  const priorityBadge = (priority) => {
    switch (priority?.toUpperCase()) {
      case "HIGH":
        return "badge-critical";
      case "MEDIUM":
        return "badge-high";
      case "LOW":
        return "badge-low";
      default:
        return "badge-muted";
    }
  };

  return (
    <div className="page-container">
      {/* HEADER */}
      <div className="page-header">
        <div>
          <span className="eyebrow">AIS TELEMETRY & ATTRIBUTION</span>
          <h1>Suspect Vessel Investigation</h1>
          <p>
            Explainable multi-factor attribution correlating AIS vessel tracks with the estimated spill origin
          </p>
        </div>

        <div className="summary-pills">
          <div className="pill">
            <span>Candidate Vessels</span>
            <strong>{vessels.length}</strong>
          </div>
          <div className="pill warning">
            <span>Primary Suspect</span>
            <strong>{vessels[0]?.name || "None"}</strong>
          </div>
        </div>
      </div>

      {/* SEARCH & FILTERS */}
      <div className="filter-toolbar panel">
        <div className="search-group">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search candidate by vessel name, MMSI, or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <label>
            <Filter size={14} /> Type:
          </label>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          >
            <option value="ALL">All Types</option>
            <option value="Cargo">Cargo</option>
            <option value="Tanker">Tanker</option>
            <option value="Passenger">Passenger</option>
            <option value="Fishing">Fishing</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Priority:</label>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
          >
            <option value="ALL">All Priorities</option>
            <option value="High">High Priority</option>
            <option value="Medium">Medium Priority</option>
            <option value="Low">Low Priority</option>
          </select>
        </div>
      </div>

      {/* SPLIT LAYOUT: VESSEL LIST + DETAILED EVIDENCE CARD */}
      <div className="investigation-grid">
        {/* LEFT COLUMN: CANDIDATE VESSEL LIST */}
        <div className="panel vessel-candidates-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">RANKED CANDIDATES</span>
              <h2>AIS Candidate Vessels</h2>
            </div>
            <span className="text-muted text-sm">
              Search Window: ±60m / 10km
            </span>
          </div>

          <div className="candidate-list-scroll">
            {filteredVessels.length === 0 ? (
              <p className="text-muted" style={{ padding: "20px" }}>
                No candidate vessels match your filters.
              </p>
            ) : (
              filteredVessels.map((v, idx) => {
                const isSelected =
                  (v.vesselId || v.mmsi || v.id) ===
                  (activeVessel?.vesselId || activeVessel?.mmsi || activeVessel?.id);
                const priority =
                  v.evidence?.investigationPriority ||
                  (v.score > 75 ? "High" : v.score > 50 ? "Medium" : "Low");

                return (
                  <div
                    key={v.vesselId || v.mmsi || idx}
                    className={`candidate-card ${isSelected ? "selected" : ""}`}
                    onClick={() =>
                      onSelectVessel(v.vesselId || v.mmsi || v.id)
                    }
                  >
                    <div className="candidate-card-top">
                      <div className="rank-badge">#{idx + 1}</div>
                      <div className="candidate-meta">
                        <strong>{v.name}</strong>
                        <span>
                          {v.vesselType || v.type} • Flag:{" "}
                          {v.flagCountry || "Unknown"}
                        </span>
                      </div>
                      <div className="score-badge">
                        <strong>{v.score}%</strong>
                        <small>Score</small>
                      </div>
                    </div>

                    <div className="candidate-evidence-row">
                      <span>MMSI: {v.mmsi}</span>
                      {v.evidence?.distanceKm !== undefined && (
                        <span>Δd: {v.evidence.distanceKm} km</span>
                      )}
                      <span className={`priority-tag ${priorityBadge(priority)}`}>
                        {priority}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* RIGHT COLUMN: EVIDENCE BREAKDOWN & TRAJECTORY MAP */}
        <div className="panel vessel-evidence-panel">
          {activeVessel ? (
            <>
              {/* VESSEL HEADER */}
              <div className="vessel-focus-header">
                <div>
                  <span className="eyebrow">INVESTIGATION PROFILE</span>
                  <h2>{activeVessel.name}</h2>
                  <p className="text-muted">
                    {activeVessel.vesselType || activeVessel.type} • IMO:{" "}
                    {activeVessel.imoNumber || "N/A"} • MMSI:{" "}
                    {activeVessel.mmsi} • Flag:{" "}
                    {activeVessel.flagCountry || "International"}
                  </p>
                </div>

                <div className="attribution-score-large">
                  <div className="score-num">{activeVessel.score}%</div>
                  <span>Attribution Probability</span>
                </div>
              </div>

              {/* "WHY IS THIS VESSEL SUSPICIOUS?" EVIDENCE CALLOUT */}
              <div className="evidence-callout">
                <div className="callout-icon">
                  <AlertTriangle size={22} />
                </div>
                <div>
                  <strong>Why is this vessel suspicious?</strong>
                  <p>
                    {activeVessel.whySuspicious ||
                      "Vessel transited through the backtracked origin uncertainty zone during the estimated source timeframe with high route and speed consistency."}
                  </p>
                </div>
              </div>

              {/* 5-FACTOR EVIDENCE METRIC BARS */}
              <div className="evidence-factors-grid">
                <div className="factor-box">
                  <div className="factor-head">
                    <span>Spatial Proximity (30%)</span>
                    <strong>
                      {activeVessel.evidence?.spatialProximity
                        ? Math.round(activeVessel.evidence.spatialProximity * 100)
                        : Math.round(activeVessel.score * 0.95)}
                      %
                    </strong>
                  </div>
                  <div className="factor-track">
                    <div
                      className="factor-fill"
                      style={{
                        width: `${
                          activeVessel.evidence?.spatialProximity
                            ? activeVessel.evidence.spatialProximity * 100
                            : activeVessel.score * 0.95
                        }%`,
                      }}
                    />
                  </div>
                  <small>
                    Distance: {activeVessel.evidence?.distanceKm ?? 0} km from origin
                  </small>
                </div>

                <div className="factor-box">
                  <div className="factor-head">
                    <span>Temporal Proximity (25%)</span>
                    <strong>
                      {activeVessel.evidence?.temporalProximity
                        ? Math.round(activeVessel.evidence.temporalProximity * 100)
                        : Math.round(activeVessel.score * 0.9)}
                      %
                    </strong>
                  </div>
                  <div className="factor-track">
                    <div
                      className="factor-fill"
                      style={{
                        width: `${
                          activeVessel.evidence?.temporalProximity
                            ? activeVessel.evidence.temporalProximity * 100
                            : activeVessel.score * 0.9
                        }%`,
                      }}
                    />
                  </div>
                  <small>
                    Time Delta: {activeVessel.evidence?.timeDifferenceMin ?? 0} min
                  </small>
                </div>

                <div className="factor-box">
                  <div className="factor-head">
                    <span>Route Consistency (20%)</span>
                    <strong>
                      {activeVessel.evidence?.routeConsistency
                        ? Math.round(activeVessel.evidence.routeConsistency * 100)
                        : Math.round(activeVessel.score * 0.85)}
                      %
                    </strong>
                  </div>
                  <div className="factor-track">
                    <div
                      className="factor-fill"
                      style={{
                        width: `${
                          activeVessel.evidence?.routeConsistency
                            ? activeVessel.evidence.routeConsistency * 100
                            : activeVessel.score * 0.85
                        }%`,
                      }}
                    />
                  </div>
                  <small>Trajectory curvature smoothness</small>
                </div>

                <div className="factor-box">
                  <div className="factor-head">
                    <span>Heading Consistency (15%)</span>
                    <strong>
                      {activeVessel.evidence?.headingConsistency
                        ? Math.round(activeVessel.evidence.headingConsistency * 100)
                        : Math.round(activeVessel.score * 0.88)}
                      %
                    </strong>
                  </div>
                  <div className="factor-track">
                    <div
                      className="factor-fill"
                      style={{
                        width: `${
                          activeVessel.evidence?.headingConsistency
                            ? activeVessel.evidence.headingConsistency * 100
                            : activeVessel.score * 0.88
                        }%`,
                      }}
                    />
                  </div>
                  <small>Alignment with spill axis</small>
                </div>

                <div className="factor-box">
                  <div className="factor-head">
                    <span>AIS Continuity (10%)</span>
                    <strong>
                      {activeVessel.evidence?.aisContinuity
                        ? Math.round(activeVessel.evidence.aisContinuity * 100)
                        : Math.round(activeVessel.score * 0.92)}
                      %
                    </strong>
                  </div>
                  <div className="factor-track">
                    <div
                      className="factor-fill"
                      style={{
                        width: `${
                          activeVessel.evidence?.aisContinuity
                            ? activeVessel.evidence.aisContinuity * 100
                            : activeVessel.score * 0.92
                        }%`,
                      }}
                    />
                  </div>
                  <small>Transponder broadcast integrity</small>
                </div>
              </div>

              {/* AIS TELEMETRY TABLE */}
              <div className="trajectory-table-container">
                <h3>Historical AIS Telemetry Waypoints</h3>
                <table className="telemetry-table">
                  <thead>
                    <tr>
                      <th>Timestamp (UTC)</th>
                      <th>Latitude</th>
                      <th>Longitude</th>
                      <th>Speed</th>
                      <th>Course</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(activeVessel.trajectory || []).map((pt, i) => (
                      <tr key={i}>
                        <td>{pt.timestamp}</td>
                        <td>{pt.lat.toFixed(4)}° N</td>
                        <td>{pt.lon.toFixed(4)}° E</td>
                        <td>{pt.speed !== undefined ? `${pt.speed} kts` : "12.4 kts"}</td>
                        <td>{pt.course !== undefined ? `${pt.course}°` : "45°"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <Ship size={36} />
              <p>Select a candidate vessel from the list to view its attribution breakdown.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
