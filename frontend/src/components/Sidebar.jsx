import React from "react";
import {
  LayoutDashboard,
  Droplets,
  Ship,
  CloudSun,
  FileText,
  Settings,
} from "lucide-react";

export default function Sidebar({ active, onNavigate, activeSpillsCount = 1, candidateCount = 3 }) {
  const items = [
    { id: "dashboard", label: "Dashboard", Icon: LayoutDashboard },
    { id: "spills", label: "Spills", Icon: Droplets, badge: activeSpillsCount },
    { id: "vessels", label: "Vessels", Icon: Ship, badge: candidateCount },
    { id: "forecast", label: "Forecast", Icon: CloudSun },
    { id: "reports", label: "Reports", Icon: FileText },
    { id: "settings", label: "Settings", Icon: Settings },
  ];

  return (
    <aside className="sidebar">
      <div className="brand" onClick={() => onNavigate("dashboard")} style={{ cursor: "pointer" }}>
        <div className="brand-icon">
          <Droplets size={24} />
        </div>
        <div>
          <h2>BlueGuard</h2>
          <p>Oil Spill Intelligence</p>
        </div>
      </div>

      <nav className="nav">
        {items.map(({ id, label, Icon, badge }) => (
          <button
            key={id}
            type="button"
            className={`nav-item ${active === id ? "active" : ""}`}
            onClick={() => onNavigate(id)}
          >
            <Icon size={19} />
            <span>{label}</span>
            {badge !== undefined && (
              <span className="nav-badge">{badge}</span>
            )}
          </button>
        ))}
      </nav>

      <div className="sidebar-note">
        <div className="status-dot online" />
        <div>
          <strong>SIH 2026 • 26143</strong>
          <span>Maritime Intelligence Active</span>
        </div>
      </div>
    </aside>
  );
}