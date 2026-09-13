import React, { useState, useEffect } from "react";
import {
  Settings as SettingsIcon,
  Server,
  Database,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  RefreshCw,
  Cpu,
  Layers,
  Globe,
  Radio,
  ExternalLink,
} from "lucide-react";
import { checkBackendHealth, API_BASE_URL, BACKEND_ROOT_URL } from "../services/api";

export default function SettingsPage({
  isDemoMode,
  onToggleDemoMode,
  backendConnected,
  onRefreshStatus,
}) {
  const [testingHealth, setTestingHealth] = useState(false);
  const [healthResult, setHealthResult] = useState(null);

  const runHealthCheck = async () => {
    setTestingHealth(true);
    try {
      const res = await checkBackendHealth();
      setHealthResult(res);
    } catch (e) {
      setHealthResult({ online: false, error: e.message });
    } finally {
      setTestingHealth(false);
    }
  };

  useEffect(() => {
    runHealthCheck();
  }, []);

  return (
    <div className="page-container">
      {/* HEADER */}
      <div className="page-header">
        <div>
          <span className="eyebrow">CONFIGURATION & DIAGNOSTICS</span>
          <h1>System Settings & Connectivity</h1>
          <p>
            Review local microservice connections, database telemetry status, and dataset operational mode
          </p>
        </div>

        <div className="summary-pills">
          <button
            type="button"
            className="secondary-btn"
            onClick={() => {
              runHealthCheck();
              if (onRefreshStatus) onRefreshStatus();
            }}
            disabled={testingHealth}
          >
            <RefreshCw
              size={15}
              className={testingHealth ? "spin" : ""}
            />{" "}
            Test Connection
          </button>
        </div>
      </div>

      <div className="settings-grid">
        {/* BACKEND STATUS PANEL */}
        <div className="panel settings-card">
          <div className="settings-card-header">
            <Server size={22} className="text-accent" />
            <div>
              <h3>FastAPI Backend Gateway</h3>
              <span>Central orchestration & REST endpoints</span>
            </div>
          </div>

          <div className="settings-card-body">
            <div className="status-indicator-box">
              <div className="indicator-row">
                <span>Service URL:</span>
                <code>{API_BASE_URL}</code>
              </div>
              <div className="indicator-row">
                <span>Health Endpoint:</span>
                <code>{BACKEND_ROOT_URL}/health</code>
              </div>
              <div className="indicator-row">
                <span>Live Connection:</span>
                {healthResult?.online ? (
                  <span className="status-badge-online">
                    <CheckCircle2 size={14} /> ONLINE ({healthResult.status})
                  </span>
                ) : (
                  <span className="status-badge-offline">
                    <XCircle size={14} /> OFFLINE / UNREACHABLE
                  </span>
                )}
              </div>
            </div>

            <p className="text-muted text-sm" style={{ marginTop: "12px" }}>
              The FastAPI backend runs locally on port 8000 and exposes endpoints under <code>/api/v1/</code> for spill tracking, vessel queries, and investigation workflows.
            </p>
          </div>
        </div>

        {/* DATABASE & POSTGIS STATUS */}
        <div className="panel settings-card">
          <div className="settings-card-header">
            <Database size={22} className="text-warning" />
            <div>
              <h3>PostgreSQL & PostGIS Database</h3>
              <span>Relational & spatial data persistence</span>
            </div>
          </div>

          <div className="settings-card-body">
            <div className="status-indicator-box">
              <div className="indicator-row">
                <span>Target Database:</span>
                <code>marineguard_db (localhost:5432)</code>
              </div>
              <div className="indicator-row">
                <span>PostgreSQL Version:</span>
                <strong>PostgreSQL 18.6 (Local)</strong>
              </div>
              <div className="indicator-row">
                <span>PostGIS Spatial Ext:</span>
                <span className="status-badge-offline">
                  <AlertTriangle size={14} /> Missing (Pending PostGIS installer)
                </span>
              </div>
              <div className="indicator-row">
                <span>Schema Migration:</span>
                <span className="text-muted">Alembic 0001_initial (Blocked by PostGIS)</span>
              </div>
            </div>

            <div className="notice-box-warning" style={{ marginTop: "12px" }}>
              <AlertTriangle size={16} />
              <div>
                <strong>PostGIS Blocker Documented:</strong>
                <p>
                  Local PostgreSQL 18.6 requires the PostGIS binary extension package before running <code>alembic upgrade head</code>. The frontend operates seamlessly via verified team sample data.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* DATASET OPERATIONAL MODE TOGGLE */}
        <div className="panel settings-card">
          <div className="settings-card-header">
            <Layers size={22} className="text-success" />
            <div>
              <h3>Data Source & Demo Mode</h3>
              <span>Manage runtime data provider</span>
            </div>
          </div>

          <div className="settings-card-body">
            <div className="mode-toggle-box">
              <div className="mode-info">
                <strong>Current Mode:</strong>
                <p>
                  {isDemoMode
                    ? "Verified Arabian Sea SIH Scenario (Official Team Sample & Precomputed GIS Data)"
                    : "Live Backend API Mode (Direct REST calls to localhost:8000)"}
                </p>
              </div>

              <div className="toggle-action-row">
                <button
                  type="button"
                  className={`toggle-mode-btn ${
                    isDemoMode ? "active-demo" : ""
                  }`}
                  onClick={() => onToggleDemoMode(true)}
                >
                  <CheckCircle2 size={16} /> Use Verified SIH Demo Scenario
                </button>

                <button
                  type="button"
                  className={`toggle-mode-btn ${
                    !isDemoMode ? "active-live" : ""
                  }`}
                  onClick={() => onToggleDemoMode(false)}
                >
                  <Server size={16} /> Connect to Live Backend API
                </button>
              </div>
            </div>

            <p className="text-muted text-sm" style={{ marginTop: "12px" }}>
              In Verified Demo Mode, all coordinates, vessel tracks, backtracking, and forecast values are pulled directly from Member 4 (GIS) and Member 3 (AIS) reference datasets (Arabian Sea Off Goa).
            </p>
          </div>
        </div>

        {/* MICROSERVICE INTEGRATION MATRIX */}
        <div className="panel settings-card">
          <div className="settings-card-header">
            <Cpu size={22} className="text-accent" />
            <div>
              <h3>Microservices Topology</h3>
              <span>Internal service contract registry</span>
            </div>
          </div>

          <div className="settings-card-body">
            <table className="microservice-table">
              <thead>
                <tr>
                  <th>Service</th>
                  <th>Member</th>
                  <th>Port</th>
                  <th>Contract Endpoint</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>AI Spill Detection</td>
                  <td>Member 2</td>
                  <td><code>8001</code></td>
                  <td><code>POST /predict</code></td>
                </tr>
                <tr>
                  <td>AIS Candidate Search</td>
                  <td>Member 3</td>
                  <td><code>8002</code></td>
                  <td><code>POST /candidate-vessels</code></td>
                </tr>
                <tr>
                  <td>GIS Backtracking</td>
                  <td>Member 4</td>
                  <td><code>5001</code></td>
                  <td><code>POST /backtrack</code></td>
                </tr>
                <tr>
                  <td>GIS Forward Forecast</td>
                  <td>Member 4</td>
                  <td><code>5001</code></td>
                  <td><code>POST /forecast</code></td>
                </tr>
                <tr>
                  <td>FastAPI Gateway</td>
                  <td>Member 5</td>
                  <td><code>8000</code></td>
                  <td><code>/api/v1/*</code></td>
                </tr>
                <tr>
                  <td>React GIS Dashboard</td>
                  <td>Member 6</td>
                  <td><code>5173</code></td>
                  <td>Frontend Dashboard</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
