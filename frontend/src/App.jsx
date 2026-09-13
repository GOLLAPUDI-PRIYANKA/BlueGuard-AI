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

import {
  spillData as mockSpill,
  vessels as mockVessels,
  originData as mockOrigin,
  forecastData as mockForecast,
  impactData as mockImpact,
} from "./data/mockData";

import "./App.css";

export default function App() {
  const [active, setActive] = useState("dashboard");
  const [investigating, setInvestigating] = useState(false);

  // --------------------------------------------------
  // DEMO MODE
  // --------------------------------------------------
  // PostgreSQL is not available yet, so the dashboard
  // currently uses the frontend mock data.
  //
  // Later, when M5 backend + PostgreSQL are ready,
  // we can enable the API integration again.
  // --------------------------------------------------

  const [spill] = useState(mockSpill);
  const [vessels] = useState(mockVessels);
  const [origin] = useState(mockOrigin);
  const [forecast] = useState(mockForecast);
  const [impact] = useState(mockImpact);

  const loading = false;
  const apiError = "";

  // --------------------------------------------------
  // INVESTIGATION BUTTON
  // --------------------------------------------------

  const handleInvestigate = () => {
    setInvestigating(true);

    setTimeout(() => {
      setInvestigating(false);
    }, 1800);
  };

  // --------------------------------------------------
  // DASHBOARD
  // --------------------------------------------------

  return (
    <div className="app">
      <Sidebar
        active={active}
        onNavigate={setActive}
      />

      <main className="main">
        <Header />

        {active === "dashboard" ? (
          <>
            {/* ---------------------------------------- */}
            {/* TOOLBAR */}
            {/* ---------------------------------------- */}

            <div className="toolbar">
              <select defaultValue="sentinel">
                <option value="sentinel">
                  Sentinel-1 SAR
                </option>

                <option value="satellite">
                  Satellite Scene
                </option>
              </select>

              <select defaultValue="date">
                <option value="date">
                  09 Sep 2026 • 12:00 UTC
                </option>

                <option>
                  08 Sep 2026 • 12:00 UTC
                </option>
              </select>

              <div className="toolbar-status">
                <span />

                {loading
                  ? "Loading..."
                  : "Demo data"}
              </div>
            </div>

            {/* ---------------------------------------- */}
            {/* MAIN DASHBOARD */}
            {/* ---------------------------------------- */}

            <section className="hero-grid">

              {/* GIS MAP */}
              <MapView
                spill={spill}
                origin={origin}
                vessels={vessels}
              />

              {/* SPILL OVERVIEW */}
              <SpillOverview
                spill={spill}
                onInvestigate={handleInvestigate}
              />

            </section>

            {/* ---------------------------------------- */}
            {/* DASHBOARD PANELS */}
            {/* ---------------------------------------- */}

            <section className="dashboard-grid">

              {/* VESSEL LIST */}
              <VesselList
                vessels={vessels}
              />

              {/* ORIGIN */}
              <OriginPanel
                origin={origin}
              />

              {/* FORECAST */}
              <ForecastPanel
                forecast={forecast}
              />

              {/* IMPACT */}
              <ImpactPanel
                impact={impact}
              />

              {/* ACTIVITY */}
              <ActivityPanel />

            </section>

            {/* ---------------------------------------- */}
            {/* INVESTIGATION NOTIFICATION */}
            {/* ---------------------------------------- */}

            {investigating && (
              <div className="toast">
                <div className="spinner" />

                Investigation workflow started...
              </div>
            )}
          </>
        ) : (
          /* ------------------------------------------ */
          /* OTHER SIDEBAR PAGES */
          /* ------------------------------------------ */

          <div className="empty-page panel">

            <div className="empty-icon">
              ◈
            </div>

            <h2>
              {active.charAt(0).toUpperCase() +
                active.slice(1)}
            </h2>

            <p>
              This section is ready for the next SIH feature.
            </p>

            <button
              className="primary-btn"
              onClick={() => setActive("dashboard")}
            >
              Back to Dashboard
            </button>

          </div>
        )}
      </main>
    </div>
  );
}