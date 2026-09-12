import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import MapView from "./components/MapView";
import SpillOverview from "./components/SpillOverview";
import VesselList from "./components/VesselList";
import OriginPanel from "./components/OriginPanel";
import ForecastPanel from "./components/ForecastPanel";
import ImpactPanel from "./components/ImpactPanel";
import ActivityPanel from "./components/ActivityPanel";
import { spillData, vessels, originData, forecastData, impactData } from "./data/mockData";
import "./App.css";

export default function App() {
  const [active, setActive] = useState("dashboard");
  const [investigating, setInvestigating] = useState(false);

  const handleInvestigate = () => {
    setInvestigating(true);
    setTimeout(() => setInvestigating(false), 1800);
  };

  return (
    <div className="app">
      <Sidebar active={active} onNavigate={setActive} />

      <main className="main">
        <Header />

        {active === "dashboard" ? (
          <>
            <div className="toolbar">
              <select defaultValue="sentinel">
                <option value="sentinel">Sentinel-1 SAR</option>
                <option>Satellite Scene</option>
              </select>
              <select defaultValue="date">
                <option value="date">09 Sep 2026 • 12:00 UTC</option>
                <option>08 Sep 2026 • 12:00 UTC</option>
              </select>
              <div className="toolbar-status"><span /> Live analysis workspace</div>
            </div>

            <section className="hero-grid">
              <MapView spill={spillData} origin={originData} vessels={vessels} />
              <SpillOverview spill={spillData} onInvestigate={handleInvestigate} />
            </section>

            <section className="dashboard-grid">
              <VesselList vessels={vessels} />
              <OriginPanel origin={originData} />
              <ForecastPanel forecast={forecastData} />
              <ImpactPanel impact={impactData} />
              <ActivityPanel />
            </section>

            {investigating && (
              <div className="toast">
                <div className="spinner" />
                Investigation workflow started...
              </div>
            )}
          </>
        ) : (
          <div className="empty-page panel">
            <div className="empty-icon">◈</div>
            <h2>{active.charAt(0).toUpperCase() + active.slice(1)}</h2>
            <p>This section is ready for the next SIH feature.</p>
            <button className="primary-btn" onClick={() => setActive("dashboard")}>Back to Dashboard</button>
          </div>
        )}
      </main>
    </div>
  );
}