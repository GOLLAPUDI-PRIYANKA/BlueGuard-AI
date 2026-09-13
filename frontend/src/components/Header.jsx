import React from "react";
import { Bell, Search, ShieldCheck, Activity, Radio } from "lucide-react";

export default function Header({
  activePage = "dashboard",
  backendOnline = false,
  isDemoMode = true,
  searchQuery = "",
  onSearchChange = null,
}) {
  const getPageTitle = () => {
    switch (activePage) {
      case "spills":
        return "Oil Spill Incident Registry";
      case "vessels":
        return "Suspect Vessel Attribution & Evidence";
      case "forecast":
        return "Spill Drift & Landfall Forecasting";
      case "reports":
        return "Investigation Dossier & Intelligence Report";
      case "settings":
        return "System Settings & Microservice Telemetry";
      default:
        return "Oil Spill Investigation Dashboard";
    }
  };

  return (
    <header className="header">
      <div className="header-left">
        <div className="breadcrumb">
          BlueGuard / Marine Intelligence /{" "}
          <span style={{ textTransform: "capitalize", color: "#3da5ff" }}>
            {activePage}
          </span>
        </div>

        <div className="title-row">
          <div className="title-icon">
            <ShieldCheck size={22} />
          </div>

          <div>
            <h1>{getPageTitle()}</h1>
            <p>
              AI-powered detection, backtracking & vessel attribution • SIH 26143
            </p>
          </div>
        </div>
      </div>

      <div className="header-actions">
        {/* BACKEND & DATASET BADGE */}
        <div className="system-status">
          <span
            className={`status-dot ${backendOnline ? "online" : "demo"}`}
          />
          <Activity size={15} />
          <span>
            {backendOnline
              ? "FastAPI Connected (8000)"
              : "Demo Mode (Arabian Sea SIH Data)"}
          </span>
        </div>

        {/* SEARCH INPUT */}
        <div className="search-box">
          <Search size={17} />
          <input
            type="text"
            placeholder="Search case, MMSI, vessel..."
            value={searchQuery}
            onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
          />
        </div>

        <button
          type="button"
          className="icon-btn"
          title="Active System Notifications"
        >
          <Bell size={19} />
          <span className="notification-dot" />
        </button>

        <div className="user">
          <div className="avatar">M6</div>
          <div>
            <strong>Member 6</strong>
            <span>Frontend & GIS</span>
          </div>
        </div>
      </div>
    </header>
  );
}