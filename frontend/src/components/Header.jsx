import React from "react";
import { Bell, Search } from "lucide-react";

export default function Header() {
  return (
    <header className="header">
      <div>
        <div className="breadcrumb">Marine Intelligence / Investigation</div>
        <h1>Oil Spill Investigation Dashboard</h1>
      </div>

      <div className="header-actions">
        <div className="search-box">
          <Search size={17} />
          <input placeholder="Search spill or vessel..." />
        </div>
        <button className="icon-btn"><Bell size={19} /><span className="notification-dot" /></button>
        <div className="user">
          <div className="avatar">I</div>
          <div>
            <strong>Investigator</strong>
            <span>Analyst</span>
          </div>
        </div>
      </div>
    </header>
  );
}