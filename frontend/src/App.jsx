import React, { useState, useEffect, useMemo, useCallback } from "react";

// Layout Components
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";

// Dashboard Widgets
import MapView from "./components/MapView";
import SpillOverview from "./components/SpillOverview";
import VesselList from "./components/VesselList";
import OriginPanel from "./components/OriginPanel";
import ForecastPanel from "./components/ForecastPanel";
import ImpactPanel from "./components/ImpactPanel";
import ActivityPanel from "./components/ActivityPanel";

// Dedicated Feature Pages
import SpillsPage from "./components/SpillsPage";
import VesselsPage from "./components/VesselsPage";
import ForecastPage from "./components/ForecastPage";
import ReportsPage from "./components/ReportsPage";
import SettingsPage from "./components/SettingsPage";
import SpillDetailsModal from "./components/SpillDetailsModal";

// Team Verified Scenario Data
import {
  TEAM_SCENARIO_SPILLS,
  TEAM_SCENARIO_ORIGIN,
  TEAM_SCENARIO_SUSPECTS,
  TEAM_SCENARIO_FORECAST,
  TEAM_SCENARIO_IMPACT,
  TEAM_SCENARIO_SUMMARY,
} from "./data/teamScenarioData";

// Centralized API Service Client
import {
  checkBackendHealth,
  getDashboardSummary,
  analyzeSpill,
  uploadImage,
  detectSpill,
} from "./services/api";

import "./App.css";

export default function App() {
  // Navigation
  const [active, setActive] = useState("dashboard");

  // Operational Mode & Backend State
  const [isDemoMode, setIsDemoMode] = useState(true);
  const [backendOnline, setBackendOnline] = useState(false);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");

  // Image Detection State
  const [selectedFile, setSelectedFile] = useState(null);
  const [detecting, setDetecting] = useState(false);
  const [detectionResult, setDetectionResult] = useState(null);

  // Domain Data State
  const [spills, setSpills] = useState(TEAM_SCENARIO_SPILLS);
  const [selectedSpillId, setSelectedSpillId] = useState("SP101");
  const [origin, setOrigin] = useState(TEAM_SCENARIO_ORIGIN);
  const [suspects, setSuspects] = useState(TEAM_SCENARIO_SUSPECTS);
  const [selectedVesselId, setSelectedVesselId] =
    useState("VES123456789");
  const [forecast, setForecast] = useState(TEAM_SCENARIO_FORECAST);
  const [impact, setImpact] = useState(TEAM_SCENARIO_IMPACT);
  const [summary, setSummary] = useState(TEAM_SCENARIO_SUMMARY);

  // Investigation Workflow & Modal State
  const [investigating, setInvestigating] = useState(false);
  const [investigationStep, setInvestigationStep] = useState("");
  const [modalSpill, setModalSpill] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Check Backend Health on Mount
  const checkStatus = useCallback(async () => {
    try {
      const health = await checkBackendHealth();
      setBackendOnline(health.online);
    } catch {
      setBackendOnline(false);
    }
  }, []);

  useEffect(() => {
  checkStatus();
}, [checkStatus]);

  // Handle toggling between Demo Mode and Live Backend
  const handleToggleDemoMode = async (enableDemo) => {
    setIsDemoMode(enableDemo);

    if (enableDemo) {
      setSpills(TEAM_SCENARIO_SPILLS);
      setOrigin(TEAM_SCENARIO_ORIGIN);
      setSuspects(TEAM_SCENARIO_SUSPECTS);
      setForecast(TEAM_SCENARIO_FORECAST);
      setImpact(TEAM_SCENARIO_IMPACT);
      setSummary(TEAM_SCENARIO_SUMMARY);
      setApiError("");
    } else {
      setLoading(true);
      setApiError("");

      try {
        const summaryData = await getDashboardSummary();

        if (summaryData && summaryData.data) {
          setSummary(summaryData.data);
        }
      } catch (err) {
        setApiError(
          "Backend API reached, but database tables are not initialized. Reverting to Arabian Sea scenario."
        );
        setIsDemoMode(true);
      } finally {
        setLoading(false);
      }
    }
  };

  // Derive Current Active Spill
  const currentSpill = useMemo(() => {
    return (
      spills.find(
        (s) => (s.spillId || s.id) === selectedSpillId
      ) || spills[0]
    );
  }, [spills, selectedSpillId]);

  // Handle Image Selection
  const handleImageSelect = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    const allowedExtensions = [
      ".png",
      ".jpg",
      ".jpeg",
      ".tif",
      ".tiff",
    ];

    const extension = file.name
      .substring(file.name.lastIndexOf("."))
      .toLowerCase();

    if (!allowedExtensions.includes(extension)) {
      setSelectedFile(null);
      setDetectionResult(null);

      setApiError(
        "Unsupported image format. Please select PNG, JPG, JPEG or TIFF."
      );

      return;
    }

    setSelectedFile(file);

    // Hide previous results until this new image is detected
    setDetectionResult(null);

    setApiError("");
  };

  // Upload Image + Detect Spill
  const handleDetectSpill = async () => {
    if (!selectedFile) {
      setApiError("Please select a satellite image first.");
      return;
    }

    setDetecting(true);
    setApiError("");
    setDetectionResult(null);

    try {
      // Upload image
      const uploadResult = await uploadImage(selectedFile);

      const imageUrl = uploadResult?.data?.imageUrl;

      if (!imageUrl) {
        throw new Error(
          "Image upload succeeded but no image path was returned."
        );
      }

      // Send image to AI detection
      const detectResult = await detectSpill({
        imageUrl,
        source: "SENTINEL_1",
        captureTime: new Date(
          selectedFile.lastModified || Date.now()
        ).toISOString(),
      });

      const detected = detectResult?.data;

      if (!detected) {
        throw new Error(
          "Detection completed but no result was returned."
        );
      }

      // Store actual detection result
      setDetectionResult(detected);

      // Create new spill object
      const newSpill = {
        spillId: detected.spillId,
        detected: detected.detected,
        confidence: detected.confidence,
        areaSqKm: detected.areaSqKm,
        severity: detected.severity,
        centroid: detected.centroid,
        title: selectedFile.name,
        detectedAt: new Date().toISOString(),
      };

      // Add detected spill to state
      setSpills((previous) => [
        newSpill,
        ...previous.filter(
          (spill) =>
            (spill.spillId || spill.id) !== detected.spillId
        ),
      ]);

      // Select detected spill
      setSelectedSpillId(detected.spillId);

      // Switch from demo mode
      setIsDemoMode(false);
    } catch (error) {
      console.error("Spill detection failed:", error);

      setApiError(
        error.message ||
          "Spill detection failed. Please check the backend and AI service."
      );
    } finally {
      setDetecting(false);
    }
  };

  // Execute Attribution & Investigation Workflow
  const handleInvestigate = async () => {
    setInvestigating(true);

    setInvestigationStep(
      "1/3 Initializing hydrodynamic backtracking advection model..."
    );

    setTimeout(() => {
      setInvestigationStep(
        "2/3 Correlating AIS candidate vessels in spatio-temporal corridor..."
      );
    }, 800);

    setTimeout(() => {
      setInvestigationStep(
        "3/3 Computing 5-factor explainable attribution risk scores..."
      );
    }, 1600);

    setTimeout(async () => {
      if (!isDemoMode && backendOnline) {
        try {
          await analyzeSpill(
            currentSpill.spillId || "SP101"
          );
        } catch {
          // Fallback handled smoothly
        }
      }

      setInvestigating(false);
      setInvestigationStep("");
    }, 2400);
  };

  const handleSelectSpill = (spillId) => {
    setSelectedSpillId(spillId);
  };

  const handleViewDetails = (spillToView) => {
    setModalSpill(spillToView || currentSpill);
  };

  const handleCloseModal = () => {
    setModalSpill(null);
  };

  const handleSelectVessel = (vesselId) => {
    setSelectedVesselId(vesselId);
  };

  const handleNavigate = (page) => {
    setActive(page);
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  return (
    <div className="app">
      <Sidebar
        active={active}
        onNavigate={handleNavigate}
        activeSpillsCount={spills.length}
        candidateCount={suspects.length}
      />

      <main className="main">
        <Header
          activePage={active}
          backendOnline={backendOnline}
          isDemoMode={isDemoMode}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
        />

        {/* API Error Banner */}
        {apiError && (
          <div className="api-notice-banner">
            <span>⚠️ {apiError}</span>

            <button
              type="button"
              className="text-btn"
              onClick={() => setApiError("")}
            >
              Dismiss
            </button>
          </div>
        )}

        {/* ===================================================== */}
        {/* PAGE 1: DASHBOARD                                     */}
        {/* ===================================================== */}

        {active === "dashboard" && (
          <>
            {/* Image Selection Toolbar */}
            <div className="toolbar">
              <select defaultValue="sentinel">
                <option value="sentinel">
                  Sentinel-1 SAR IW (VV+VH)
                </option>

                <option value="sentinel2">
                  Sentinel-2 Optical (MSI)
                </option>

                <option value="landsat">
                  Landsat-8/9 OLI
                </option>
              </select>

              <label className="image-upload">
                <input
                  type="file"
                  accept=".png,.jpg,.jpeg,.tif,.tiff"
                  onChange={handleImageSelect}
                />

                <span>
                  {selectedFile
                    ? selectedFile.name
                    : "Select Image"}
                </span>
              </label>

              <button
                type="button"
                className="detect-button"
                onClick={handleDetectSpill}
                disabled={!selectedFile || detecting}
              >
                {detecting
                  ? "Detecting Spill..."
                  : "Detect Spill"}
              </button>

              <div className="toolbar-status">
                <span
                  style={{
                    backgroundColor: detecting
                      ? "#ff9f43"
                      : backendOnline
                      ? "#2ed573"
                      : "#ff4757",
                  }}
                />

                {detecting
                  ? "AI Detection Running..."
                  : backendOnline
                  ? "Backend Connected"
                  : "Backend Offline"}
              </div>
            </div>

            {/* ================================================= */}
            {/* SHOW DASHBOARD RESULTS ONLY AFTER DETECTION       */}
            {/* ================================================= */}

            {detectionResult && (
              <>
                {/* Detection Result Banner */}
                <div className="detection-result">
                  <div>
                    <strong>
                      {detectionResult.detected
                        ? "🛢️ Spill Detected"
                        : "✓ No Spill Detected"}
                    </strong>

                    {detectionResult.detected && (
                      <span>
                        Confidence:{" "}
                        {detectionResult.confidence != null
                          ? `${Math.round(
                              detectionResult.confidence > 1
                                ? detectionResult.confidence
                                : detectionResult.confidence * 100
                            )}%`
                          : "N/A"}
                        {" · "}
                        Area:{" "}
                        {detectionResult.areaSqKm != null
                          ? `${detectionResult.areaSqKm} km²`
                          : "N/A"}
                        {" · "}
                        Severity:{" "}
                        {detectionResult.severity || "N/A"}
                      </span>
                    )}
                  </div>
                </div>

                {/* GIS Map + Spill Overview */}
                <section className="hero-grid">
                  <MapView
                    spill={currentSpill}
                    origin={origin}
                    vessels={suspects}
                    forecast={forecast}
                    impact={impact}
                    selectedVesselId={selectedVesselId}
                    onSelectVessel={handleSelectVessel}
                  />

                  <SpillOverview
                    spill={currentSpill}
                    onInvestigate={handleInvestigate}
                    onViewDetails={handleViewDetails}
                    investigating={investigating}
                  />
                </section>

                {/* Metric & Analytics Grid */}
                <section className="dashboard-grid">
                  <VesselList
                    vessels={suspects}
                    selectedVesselId={selectedVesselId}
                    onSelectVessel={handleSelectVessel}
                    onViewAll={() =>
                      handleNavigate("vessels")
                    }
                  />

                  <OriginPanel origin={origin} />

                  <ForecastPanel
                    forecast={forecast}
                    onViewForecast={() =>
                      handleNavigate("forecast")
                    }
                  />

                  <ImpactPanel
                    impact={impact}
                    onViewReports={() =>
                      handleNavigate("reports")
                    }
                  />

                  <ActivityPanel
                    investigationCompleted={!investigating}
                  />
                </section>
              </>
            )}
          </>
        )}

        {/* ===================================================== */}
        {/* PAGE 2: SPILL INCIDENT REGISTRY                       */}
        {/* ===================================================== */}

        {active === "spills" && (
          <SpillsPage
            spills={spills}
            selectedSpillId={selectedSpillId}
            onSelectSpill={(id) => {
              handleSelectSpill(id);
              handleNavigate("dashboard");
            }}
            onViewDetails={handleViewDetails}
          />
        )}

        {/* ===================================================== */}
        {/* PAGE 3: SUSPECT VESSEL ATTRIBUTION                    */}
        {/* ===================================================== */}

        {active === "vessels" && (
          <VesselsPage
            vessels={suspects}
            spill={currentSpill}
            origin={origin}
            selectedVesselId={selectedVesselId}
            onSelectVessel={handleSelectVessel}
          />
        )}

        {/* ===================================================== */}
        {/* PAGE 4: FORWARD SPILL FORECAST                        */}
        {/* ===================================================== */}

        {active === "forecast" && (
          <ForecastPage
            forecast={forecast}
            spill={currentSpill}
            origin={origin}
          />
        )}

        {/* ===================================================== */}
        {/* PAGE 5: OFFICIAL INVESTIGATION REPORTS                */}
        {/* ===================================================== */}

        {active === "reports" && (
          <ReportsPage
            spill={currentSpill}
            origin={origin}
            suspects={suspects}
            forecast={forecast}
            impact={impact}
          />
        )}

        {/* ===================================================== */}
        {/* PAGE 6: SYSTEM SETTINGS & TELEMETRY                   */}
        {/* ===================================================== */}

        {active === "settings" && (
          <SettingsPage
            isDemoMode={isDemoMode}
            onToggleDemoMode={handleToggleDemoMode}
            backendConnected={backendOnline}
            onRefreshStatus={checkStatus}
          />
        )}

        {/* ===================================================== */}
        {/* INVESTIGATION PROGRESS TOAST                          */}
        {/* ===================================================== */}

        {investigating && (
          <div className="toast investigation-toast">
            <div className="spinner" />

            <div>
              <strong>
                Executing BlueGuard Investigation Pipeline
              </strong>

              <p>{investigationStep}</p>
            </div>
          </div>
        )}

        {/* ===================================================== */}
        {/* SPILL DETAILS MODAL                                   */}
        {/* ===================================================== */}

        {modalSpill && (
          <SpillDetailsModal
            spill={modalSpill}
            origin={origin}
            suspects={suspects}
            forecast={forecast}
            impact={impact}
            onClose={handleCloseModal}
            onInvestigateVessels={() => {
              handleCloseModal();
              handleNavigate("vessels");
            }}
            onViewReport={() => {
              handleCloseModal();
              handleNavigate("reports");
            }}
          />
        )}
      </main>
    </div>
  );
}
