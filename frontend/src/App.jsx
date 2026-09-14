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
          "Backend API reached, but database tables are not initialized. Reverting to Arabian Sea
