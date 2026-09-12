import React from "react";
import { LayoutDashboard, Droplets, Ship, CloudSun, FileText, Settings } from "lucide-react";

export default function Sidebar({ active, onNavigate }) {
  const items = [
    ["dashboard", "Dashboard", LayoutDashboard],
    ["spills", "Spills", Droplets],
    ["vessels", "Vessels", Ship],
    ["forecast", "Forecast", CloudSun],
    ["reports", "Reports", FileText],
    ["settings", "Settings", Settings]
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon"><Droplets size={24} /></div>
        <div>
          <h2>BlueGuard</h2>
          <p>Oil Spill Investigation</p>
        </div>
      </div>

      <nav className="nav">
        {items.map(([id, label, Icon]) => (
          <button
            key={id}
            className={`nav-item ${active === id ? "active" : ""}`}
            onClick={() => onNavigate(id)}
          >
            <Icon size={19} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-note">
        <div className="status-dot" />
        <div>
          <strong>System Online</strong>
          <span>Monitoring services active</span>
        </div>
      </div>
    </aside>
  );
}