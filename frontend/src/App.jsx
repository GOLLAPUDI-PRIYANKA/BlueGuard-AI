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
  uploadImage,
  detectSpill,
  analyzeSpill,
  getSpill,
  getOrigin,
  getSuspects,
  getForecast,
  getImpact,
  getVesselTrajectory,
} from "./services/api";

import "./App.css";

export default function App() {
  const [active, setActive] = useState("dashboard");

  const [selectedFile, setSelectedFile] = useState(null);
  const [spill, setSpill] = useState(null);
  const [origin, setOrigin] = useState(null);
  const [vessels, setVessels] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [impact, setImpact] = useState(null);
  const [trajectories, setTrajectories] = useState({});

  const [loading, setLoading] = useState(false);
  const [investigating, setInvestigating] = useState(false);
  const [apiError, setApiError] = useState("");
  const [status, setStatus] = useState("Select a satellite image");

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      setSelectedFile(null);
      setStatus("Select a satellite image");
      return;
    }

    const extension = file.name.split(".").pop()?.toLowerCase();

    const allowedExtensions = [
      "png",
      "jpg",
      "jpeg",
      "tif",
      "tiff",
    ];

    if (!allowedExtensions.includes(extension)) {
      setSelectedFile(null);
      setApiError(
        "Unsupported image format. Please select PNG, JPG, JPEG or TIFF."
      );
      setStatus("Invalid image");
      return;
    }

    setApiError("");
    setSelectedFile(file);
    setStatus(`Selected: ${file.name}`);
  };

  const handleDetect = async () => {
    if (!selectedFile) {
      setApiError("Please select a satellite image first.");
      return;
    }

    setLoading(true);
    setApiError("");
    setStatus("Uploading image...");

    try {
      const uploadResult = await uploadImage(selectedFile);
      const imageUrl = uploadResult?.data?.imageUrl;

      if (!imageUrl) {
        throw new Error("Upload succeeded but no image path was returned.");
      }

      setStatus("Running AI detection...");

      const detectResult = await detectSpill(
        imageUrl,
        "SENTINEL_1",
        new Date().toISOString()
      );

      const detectedSpill = detectResult?.data;

      if (!detectedSpill?.spillId) {
        throw new Error("Detection did not return a spill ID.");
      }

      const spillResult = await getSpill(detectedSpill.spillId);

      const actualSpill = spillResult?.data || {
        spillId: detectedSpill.spillId,
        areaSqKm: detectedSpill.areaSqKm,
        severity: detectedSpill.severity,
        confidence: detectedSpill.confidence,
        detectedAt: new Date().toISOString(),
        centroid: detectedSpill.centroid,
      };

      setSpill(actualSpill);
      setOrigin(null);
      setVessels([]);
      setForecast([]);
      setImpact(null);
      setTrajectories({});

      setStatus(
        detectedSpill.detected
          ? `Spill detected: ${detectedSpill.spillId}`
          : `No spill detected: ${detectedSpill.spillId}`
      );
    } catch (error) {
      setApiError(error.message || "Detection failed.");
      setStatus("Detection failed");
    } finally {
      setLoading(false);
    }
  };

  const handleInvestigate = async () => {
    if (!spill?.spillId) {
      setApiError("Detect a spill before starting the investigation.");
      return;
    }

    setInvestigating(true);
    setApiError("");
    setStatus("Running investigation...");

    try {
      await analyzeSpill(spill.spillId);

      setStatus("Loading investigation results...");

      const [
        spillResult,
        originResult,
        suspectsResult,
        forecastResult,
        impactResult,
      ] = await Promise.all([
        getSpill(spill.spillId),
        getOrigin(spill.spillId),
        getSuspects(spill.spillId),
        getForecast(spill.spillId),
        getImpact(spill.spillId),
      ]);

      const updatedSpill = spillResult?.data;
      const updatedOrigin = originResult?.data;
      const updatedSuspects = suspectsResult?.data?.suspects || [];
      const updatedForecast = forecastResult?.data?.forecast || [];
      const updatedImpact = impactResult?.data;

      setSpill(updatedSpill || spill);
      setOrigin(updatedOrigin || null);
      setVessels(updatedSuspects);
      setForecast(updatedForecast);
      setImpact(updatedImpact);

      setStatus("Loading AIS trajectories...");

      const trajectoryEntries = await Promise.all(
        updatedSuspects.map(async (vessel) => {
          try {
            const result = await getVesselTrajectory(vessel.vesselId);
            return [vessel.vesselId, result?.data || null];
          } catch {
            return [vessel.vesselId, null];
          }
        })
      );

      setTrajectories(Object.fromEntries(trajectoryEntries));
      setStatus("Investigation complete");
    } catch (error) {
      setApiError(error.message || "Investigation failed.");
      setStatus("Investigation failed");
    } finally {
      setInvestigating(false);
    }
  };

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
            <div className="toolbar">
              <select defaultValue="sentinel">
                <option value="sentinel">Sentinel-1 SAR</option>
                <option value="satellite">Satellite Scene</option>
              </select>

              <label className="primary-btn upload-btn">
                Select Image
                <input
                  type="file"
                  accept=".png,.jpg,.jpeg,.tif,.tiff,image/png,image/jpeg,image/tiff"
                  onChange={handleFileChange}
                  hidden
                />
              </label>

              <button
                className="primary-btn"
                onClick={handleDetect}
                disabled={loading || investigating || !selectedFile}
              >
                {loading ? "Detecting..." : "Detect Spill"}
              </button>

              <div className="toolbar-status">
                <span />
                {status}
              </div>
            </div>

            {apiError && (
              <div className="panel error-panel">
                {apiError}
              </div>
            )}

            {spill ? (
              <>
                <section className="hero-grid">
                  <MapView
                    spill={spill}
                    origin={origin}
                    vessels={vessels}
                    trajectories={trajectories}
                  />

                  <SpillOverview
                    spill={spill}
                    onInvestigate={handleInvestigate}
                    investigating={investigating}
                  />
                </section>

                <section className="dashboard-grid">
                  <VesselList vessels={vessels} />

                  <OriginPanel origin={origin} />

                  <ForecastPanel forecast={forecast} />

                  <ImpactPanel impact={impact} />

                  <ActivityPanel />
                </section>
              </>
            ) : (
              <div className="panel empty-page">
                <div className="empty-icon">◈</div>
                <h2>Satellite Analysis</h2>
                <p>
                  Select a supported satellite image and start detection.
                </p>
              </div>
            )}
          </>
        ) : (
          <div className="empty-page panel">
            <div className="empty-icon">◈</div>

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
