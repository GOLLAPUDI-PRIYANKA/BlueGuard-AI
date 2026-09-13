import React, { useState, useMemo } from "react";
import {
  Droplets,
  AlertTriangle,
  Clock,
  MapPin,
  Search,
  Filter,
  ArrowRight,
  ShieldAlert,
  ChevronRight,
} from "lucide-react";

export default function SpillsPage({
  spills = [],
  selectedSpillId,
  onSelectSpill,
  onViewDetails,
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [regionFilter, setRegionFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");

  const filteredSpills = useMemo(() => {
    return spills.filter((s) => {
      const matchesSearch =
        !searchQuery ||
        (s.title || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
        (s.spillId || s.id || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
        (s.region || "").toLowerCase().includes(searchQuery.toLowerCase());

      const matchesSeverity =
        severityFilter === "ALL" || s.severity === severityFilter;

      const matchesRegion =
        regionFilter === "ALL" ||
        (s.region || "").toLowerCase().includes(regionFilter.toLowerCase());

      const matchesStatus =
        statusFilter === "ALL" || s.status === statusFilter;

      return matchesSearch && matchesSeverity && matchesRegion && matchesStatus;
    });
  }, [spills, searchQuery, severityFilter, regionFilter, statusFilter]);

  const severityBadgeClass = (severity) => {
    switch (severity?.toUpperCase()) {
      case "CRITICAL":
        return "badge-critical";
      case "HIGH":
        return "badge-high";
      case "MEDIUM":
        return "badge-medium";
      case "LOW":
        return "badge-low";
      default:
        return "badge-muted";
    }
  };

  const statusBadgeClass = (status) => {
    switch (status) {
      case "UNDER_INVESTIGATION":
        return "status-investigating";
      case "ANALYSIS_COMPLETE":
        return "status-complete";
      case "CLOSED":
        return "status-closed";
      default:
        return "status-detected";
    }
  };

  return (
    <div className="page-container">
      {/* -------------------------------------------------- */}
      {/* PAGE HEADER & FILTERS */}
      {/* -------------------------------------------------- */}
      <div className="page-header">
        <div>
          <span className="eyebrow">CASE REGISTRY</span>
          <h1>Oil Spill Records & Cases</h1>
          <p>
            Historical and active satellite-detected marine oil spill incidents across monitoring sectors
          </p>
        </div>

        <div className="summary-pills">
          <div className="pill">
            <span>Total Spills</span>
            <strong>{spills.length}</strong>
          </div>
          <div className="pill warning">
            <span>Active Cases</span>
            <strong>
              {spills.filter((s) => s.status !== "CLOSED").length}
            </strong>
          </div>
        </div>
      </div>

      {/* FILTER BAR */}
      <div className="filter-toolbar panel">
        <div className="search-group">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search by Spill ID, name, or region..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <label>
            <Filter size={14} /> Severity:
          </label>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Region:</label>
          <select
            value={regionFilter}
            onChange={(e) => setRegionFilter(e.target.value)}
          >
            <option value="ALL">All Regions</option>
            <option value="Arabian Sea">Arabian Sea</option>
            <option value="Bay of Bengal">Bay of Bengal</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Status:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="ALL">All Statuses</option>
            <option value="UNDER_INVESTIGATION">Under Investigation</option>
            <option value="ANALYSIS_COMPLETE">Analysis Complete</option>
            <option value="DETECTED">Detected</option>
            <option value="CLOSED">Closed</option>
          </select>
        </div>
      </div>

      {/* -------------------------------------------------- */}
      {/* SPILL TABLE / LIST */}
      {/* -------------------------------------------------- */}
      {filteredSpills.length === 0 ? (
        <div className="empty-state panel">
          <AlertTriangle size={36} className="text-warning" />
          <h3>No Spills Found</h3>
          <p>No spill records match your search or filter criteria.</p>
          <button
            type="button"
            className="secondary-btn"
            onClick={() => {
              setSearchQuery("");
              setSeverityFilter("ALL");
              setRegionFilter("ALL");
              setStatusFilter("ALL");
            }}
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="spills-grid">
          {filteredSpills.map((spill) => {
            const isSelected = selectedSpillId === (spill.spillId || spill.id);
            const lat = spill.centroid?.lat || spill.latitude || 0;
            const lon = spill.centroid?.lon || spill.longitude || 0;
            const conf = Math.round(
              spill.confidence > 1 ? spill.confidence : spill.confidence * 100
            );

            return (
              <div
                key={spill.spillId || spill.id}
                className={`spill-card panel ${isSelected ? "selected-case" : ""}`}
                onClick={() => onSelectSpill(spill.spillId || spill.id)}
              >
                <div className="spill-card-header">
                  <div>
                    <span className="case-id">
                      {spill.spillId || spill.id}
                    </span>
                    <h3>{spill.title || `Incident ${spill.spillId || spill.id}`}</h3>
                  </div>
                  <span
                    className={`severity-badge ${severityBadgeClass(
                      spill.severity
                    )}`}
                  >
                    {spill.severity}
                  </span>
                </div>

                <div className="spill-card-body">
                  <div className="metric-row">
                    <div className="metric-box">
                      <span>Area</span>
                      <strong>{spill.areaSqKm || spill.area} km²</strong>
                    </div>
                    <div className="metric-box">
                      <span>AI Confidence</span>
                      <strong className="text-accent">{conf}%</strong>
                    </div>
                    <div className="metric-box">
                      <span>Sensor</span>
                      <strong>{spill.sensor || "Sentinel-1"}</strong>
                    </div>
                  </div>

                  <div className="spill-info-list">
                    <div>
                      <Clock size={14} />
                      <span>
                        Detected:{" "}
                        <strong>{spill.detectedAt || "Recent"}</strong>
                      </span>
                    </div>
                    <div>
                      <MapPin size={14} />
                      <span>
                        {spill.region || "Indian EEZ"} (
                        {lat.toFixed(3)}° N, {lon.toFixed(3)}° E)
                      </span>
                    </div>
                  </div>

                  {spill.notes && (
                    <p className="spill-notes">{spill.notes}</p>
                  )}
                </div>

                <div className="spill-card-footer">
                  <span
                    className={`status-pill ${statusBadgeClass(
                      spill.status
                    )}`}
                  >
                    {spill.status?.replace("_", " ") || "Active"}
                  </span>

                  <button
                    type="button"
                    className="primary-btn-sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectSpill(spill.spillId || spill.id);
                      if (onViewDetails) onViewDetails(spill);
                    }}
                  >
                    Investigate Case <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
