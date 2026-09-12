export const spillData = {
  id: "SP-2026-001",
  area: 12.4,
  severity: "High",
  confidence: 91,
  detectedAt: "09 Sep 2026, 12:15 UTC",
  latitude: 15.62,
  longitude: 80.31
};

export const vessels = [
  { id: 1, name: "Ocean Star", mmsi: "563421000", score: 91, type: "Tanker" },
  { id: 2, name: "Blue Horizon", mmsi: "477321300", score: 76, type: "Cargo" },
  { id: 3, name: "Marine Quest", mmsi: "636729100", score: 54, type: "Tanker" },
  { id: 4, name: "Coral Dawn", mmsi: "352001874", score: 38, type: "Cargo" },
  { id: 5, name: "Atlantic Wind", mmsi: "563214780", score: 21, type: "Fishing" }
];

export const originData = {
  time: "10 Sep 2026, 04:30 UTC",
  confidence: 82,
  latitude: 14.80,
  longitude: 79.90
};

export const forecastData = [
  { hours: 24, area: 18.6 },
  { hours: 48, area: 27.3 },
  { hours: 72, area: 34.7 }
];

export const impactData = {
  marine: "High",
  fishing: "Medium",
  coastal: "Low",
  affectedArea: 42.6
};