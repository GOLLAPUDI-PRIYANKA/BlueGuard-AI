# BlueGuard-AI Service Contracts

## Purpose

This document defines the internal communication contracts between the BlueGuard-AI services.

The backend acts as the main integration layer.

---

# 1. AI Detection Service

## Endpoint

POST /predict

## Input

```json
{
  "imageUri": "path/to/satellite/image",
  "modelVersion": "v1"
}
```

## Output

```json
{
  "mask": "path/to/mask",
  "confidence": 0.91,
  "polygons": [
    [[120, 80], [125, 85], [130, 90]]
  ]
}
```

## Notes

- polygons are initially image/pixel coordinates
- GIS georeferencing is handled by the GIS service
- confidence represents AI detection confidence

---

# 2. GIS Backtracking Service

## Endpoint

POST /backtrack

## Input

```json
{
  "spillGeometry": {},
  "environment": {
    "wind": {},
    "current": {}
  }
}
```

## Output

```json
{
  "originPolygon": {},
  "sourceTime": "2026-01-01T12:00:00Z"
}
```

---

# 3. AIS Candidate Vessel Service

## Endpoint

POST /candidate-vessels

## Input

```json
{
  "originPolygon": {},
  "timeWindow": {
    "start": "2026-01-01T00:00:00Z",
    "end": "2026-01-02T00:00:00Z"
  }
}
```

## Output

```json
{
  "vessels": [
    {
      "vesselId": "VESSEL-001",
      "features": {}
    }
  ]
}
```

---

# 4. Attribution Service

## Endpoint

POST /score

## Input

```json
{
  "spill": {},
  "vesselFeatures": {}
}
```

## Output

```json
{
  "rankedVessels": [
    {
      "vesselId": "VESSEL-001",
      "score": 0.87,
      "evidence": {}
    }
  ]
}
```

## Attribution Score

Recommended weighting:

- Spatial proximity: 30%
- Temporal proximity: 25%
- Trajectory consistency: 20%
- Source-region overlap: 15%
- AIS behavior signal: 10%

---

# 5. Forecast Service

## Endpoint

POST /forecast

## Input

```json
{
  "origin": {},
  "spill": {},
  "wind": {},
  "current": {}
}
```

## Output

```json
{
  "forecast": {
    "24h": {},
    "48h": {},
    "72h": {}
  },
  "uncertainty": "medium"
}
```

---

# Integration Order

The services should be connected in this order:

Satellite
↓
AI Detection
↓
GIS Backtracking
↓
AIS Candidate Search
↓
Attribution
↓
Forecast
↓
Impact Analysis
↓
Frontend Dashboard

---

# Integration IDs

The following IDs must remain consistent across services:

- spillId
- detectionId
- analysisId
- vesselId

---

# Important Rule

Attribution results are investigation-support information.

The system must not automatically treat a ranked vessel as legally responsible for an oil spill.
