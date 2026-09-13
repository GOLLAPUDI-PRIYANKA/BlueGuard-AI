import React from "react";
import { Bell, Search, ShieldCheck, Activity } from "lucide-react";

export default function Header() {
  return (
    <header className="header">
      <div className="header-left">
        <div className="breadcrumb">
          BlueGuard / Marine Intelligence / Investigation
        </div>

        <div className="title-row">
          <div className="title-icon">
            <ShieldCheck size={22} />
          </div>

          <div>
            <h1>Oil Spill Investigation Dashboard</h1>
            <p>
              AI-powered detection, backtracking & vessel attribution
            </p>
          </div>
        </div>
      </div>

      <div className="header-actions">
        <div className="system-status">
          <span className="status-dot"></span>
          <Activity size={15} />
          System Operational
        </div>

        <div className="search-box">
          <Search size={17} />
          <input
            type="text"
            placeholder="Search spill or vessel..."
          />
        </div>

        <button className="icon-btn" title="Notifications">
          <Bell size={19} />
          <span className="notification-dot"></span>
        </button>

        <div className="user">
          <div className="avatar">I</div>

          <div>
            <strong>Investigator</strong>
            <span>Marine Analyst</span>
          </div>
        </div>
      </div>
    </header>
  );
}