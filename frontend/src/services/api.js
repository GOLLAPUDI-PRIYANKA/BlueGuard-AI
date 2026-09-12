// BlueGuard M6 Frontend → M5 FastAPI Backend

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

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
    throw new Error(result.message || "API request failed");
  }

  return result;
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

export const analyzeSpill = (spillId) =>
  apiRequest(`/spills/${spillId}/analyze`, {
    method: "POST",
    body: JSON.stringify({
      includeForecast: true,
      includeImpact: true,
      aisHoursBefore: 12,
      aisHoursAfter: 12,
    }),
  });