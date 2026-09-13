// BlueGuard M6 Frontend → M5 FastAPI Backend Service Client
// Centralized API layer following team contracts

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const BACKEND_ROOT_URL =
  API_BASE_URL.replace(/\/api\/v1\/?$/, "");

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
    const errorMsg = result.message || `API error ${response.status}: ${response.statusText}`;
    const err = new Error(errorMsg);
    err.status = response.status;
    err.errorCode = result.errorCode;
    throw err;
  }

  return result;
}

export async function checkBackendHealth() {
  try {
    const response = await fetch(`${BACKEND_ROOT_URL}/health`, {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(3000),
    });
    if (!response.ok) return { online: false, status: response.statusText };
    const data = await response.json();
    return { online: true, status: data.status || "healthy" };
  } catch (err) {
    return { online: false, error: err.message };
  }
}

export const getDashboardSummary = () =>
  apiRequest("/dashboard/summary");

export const getSpill = (spillId) =>
  apiRequest(`/spills/${spillId}`);

export const getNearbyVessels = (spillId) =>
  apiRequest(`/spills/${spillId}/nearby-vessels`);

export const getVesselTrajectory = (vesselId) =>
  apiRequest(`/vessels/${vesselId}/trajectory`);

export const getOrigin = (spillId) =>
  apiRequest(`/spills/${spillId}/origin`);

export const getSuspects = (spillId) =>
  apiRequest(`/spills/${spillId}/suspects`);

export const getForecast = (spillId) =>
  apiRequest(`/spills/${spillId}/forecast`);

export const getImpact = (spillId) =>
  apiRequest(`/spills/${spillId}/impact`);

export const getReport = (spillId) =>
  apiRequest(`/spills/${spillId}/report`);

export const analyzeSpill = (spillId, options = {}) =>
  apiRequest(`/spills/${spillId}/analyze`, {
    method: "POST",
    body: JSON.stringify({
      includeForecast: options.includeForecast ?? true,
      includeImpact: options.includeImpact ?? true,
      aisHoursBefore: options.aisHoursBefore ?? 12,
      aisHoursAfter: options.aisHoursAfter ?? 12,
    }),
  });

export const detectSpill = (payload) =>
  apiRequest("/spills/detect", {
    method: "POST",
    body: JSON.stringify(payload),
  });
