// BlueGuard Frontend API Service

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const BACKEND_ROOT_URL = "";

async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const result = await response.json();

  if (!response.ok || result.success === false) {
    throw new Error(
      result.message ||
        result.detail ||
        `API error ${response.status}`
    );
  }

  return result;
}

export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/dashboard/summary`, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });

    return {
      online: response.ok,
      status: response.ok ? "healthy" : "offline",
    };
  } catch (err) {
    return {
      online: false,
      error: err.message,
    };
  }
}

export async function uploadImage(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/spills/upload`, {
    method: "POST",
    body: formData,
  });

  const result = await response.json();

  if (!response.ok || result.success === false) {
    throw new Error(
      result.message ||
        result.detail ||
        `Upload failed: ${response.status}`
    );
  }

  return result;
}

export const getDashboardSummary = () =>
  apiRequest("/dashboard/summary");

export const analyzeSpill = (payload) =>
  apiRequest("/spills/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const detectSpill = (payload) =>
  apiRequest("/spills/detect", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const getSpills = () =>
  apiRequest("/spills");

export const getSpill = (id) =>
  apiRequest(`/spills/${id}`);

export const getVessels = () =>
  apiRequest("/vessels");

export const getForecast = (spillId) =>
  apiRequest(`/forecast/${spillId}`);

export const getImpact = (spillId) =>
  apiRequest(`/impact/${spillId}`);

export const getOrigin = (spillId) =>
  apiRequest(`/origin/${spillId}`);

export const getReports = () =>
  apiRequest("/reports");

export const getSettings = () =>
  apiRequest("/settings");
