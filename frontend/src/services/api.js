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

  // Safely parse JSON — guard against empty or non-JSON bodies
  let result = null;
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    try {
      result = await response.json();
    } catch {
      throw new Error(`Server returned an invalid response (status ${response.status})`);
    }
  } else {
    // Non-JSON body (HTML error pages, empty responses, etc.)
    const text = await response.text().catch(() => "");
    if (!response.ok) {
      throw new Error(text || `Server error (status ${response.status})`);
    }
  }

  if (!response.ok || result?.success === false) {
    throw new Error(
      result?.message ||
        result?.detail ||
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
    // Do NOT set Content-Type — browser sets it automatically with the multipart boundary
  });

  // Safely parse JSON — guard against empty or non-JSON error bodies
  let result = null;
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    try {
      result = await response.json();
    } catch {
      throw new Error(`Server returned an invalid response (status ${response.status})`);
    }
  } else {
    const text = await response.text().catch(() => "");
    throw new Error(text || `Upload failed with status ${response.status}`);
  }

  if (!response.ok || result?.success === false) {
    throw new Error(
      result?.message ||
        result?.detail ||
        `Upload failed: ${response.status}`
    );
  }

  return result;
}

export const getDashboardSummary = () =>
  apiRequest("/dashboard/summary");

export const analyzeSpill = (spillId, payload = {}) =>
  apiRequest(`/spills/${spillId}/analyze`, {
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
  apiRequest(`/spills/${spillId}/forecast`);

export const getImpact = (spillId) =>
  apiRequest(`/spills/${spillId}/impact`);

export const getOrigin = (spillId) =>
  apiRequest(`/spills/${spillId}/origin`);

export const getSuspects = (spillId) =>
  apiRequest(`/spills/${spillId}/suspects`);

export const getVesselTrajectory = (vesselId) =>
  apiRequest(`/vessels/${vesselId}/trajectory`);

export const getReports = () =>
  apiRequest("/reports");

export const getSettings = () =>
  apiRequest("/settings");
