// M5 FastAPI integration.
// Change this URL when your backend is ready.
const API_BASE_URL = "http://localhost:8000/api/v1";

export async function getSpill(spillId) {
  const response = await fetch(`${API_BASE_URL}/spills/${spillId}`);
  if (!response.ok) throw new Error("Unable to load spill");
  return response.json();
}

export async function getSuspects(spillId) {
  const response = await fetch(`${API_BASE_URL}/spills/${spillId}/suspects`);
  if (!response.ok) throw new Error("Unable to load suspects");
  return response.json();
}

export async function getOrigin(spillId) {
  const response = await fetch(`${API_BASE_URL}/spills/${spillId}/origin`);
  if (!response.ok) throw new Error("Unable to load origin");
  return response.json();
}

export async function getForecast(spillId) {
  const response = await fetch(`${API_BASE_URL}/spills/${spillId}/forecast`);
  if (!response.ok) throw new Error("Unable to load forecast");
  return response.json();
}

export async function getImpact(spillId) {
  const response = await fetch(`${API_BASE_URL}/spills/${spillId}/impact`);
  if (!response.ok) throw new Error("Unable to load impact");
  return response.json();
}