# BlueGuard-AI API Integration Matrix

## 1. Public Backend APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/spills/detect` | Submit satellite image and create spill detection |
| POST | `/api/v1/spills/{spillId}/analyze` | Run complete spill analysis workflow |
| GET | `/api/v1/spills/{spillId}` | Get spill details |
| GET | `/api/v1/spills/{spillId}/nearby-vessels` | Get nearby candidate vessels |
| GET | `/api/v1/vessels/{vesselId}/trajectory` | Get vessel trajectory |
| GET | `/api/v1/spills/{spillId}/origin` | Get estimated spill origin |
| GET | `/api/v1/spills/{spillId}/suspects` | Get ranked suspect vessels |
| GET | `/api/v1/spills/{spillId}/forecast` | Get spill movement forecast |
| GET | `/api/v1/spills/{spillId}/impact` | Get affected impact zones |
| GET | `/api/v1/dashboard/summary` | Get dashboard summary |
| GET | `/api/v1/spills/{spillId}/report` | Generate investigation report |

## 2. Internal Service Endpoints

| Service | Method | Endpoint | Input | Output |
|---|---|---|---|---|
| AI | POST | `/predict` | Image URI, model version | Mask URI, confidence, polygons |
| AIS | POST | `/candidate-vessels` | Origin, time window | Candidate vessels, trajectory features |
| GIS | POST | `/backtrack` | Spill geometry, environment | Origin, source time, uncertainty |
| GIS | POST | `/forecast` | Origin/spill, wind, current | Forecast points, GeoJSON, uncertainty |
| Attribution | POST | `/score` | Spill and vessel features | Ranked scores and evidence |

## 3. Integration Sequence

Satellite Image  
→ AI Detection  
→ Spill Geometry  
→ GIS Backtracking  
→ Estimated Origin and Source Time  
→ AIS Candidate Vessel Search  
→ Vessel Features  
→ Attribution Scoring  
→ Ranked Suspects  
→ Forecast  
→ Impact Zones  
→ Backend  
→ Dashboard

## 4. Service Communication

Frontend  
→ Backend

Backend  
→ AI Service  
→ AIS Service  
→ GIS Service  
→ Attribution Service

AI Service  
→ Returns spill detection results

GIS Service  
→ Returns origin, source time, confidence, uncertainty and forecast

AIS Service  
→ Returns candidate vessels and trajectory features

Attribution Service  
→ Returns evidence scores and ranked vessels

Backend  
→ Combines service results and returns a unified response to the frontend

## 5. Common Identifiers

The integrated system should use consistent identifiers:

- `spillId`
- `detectionId`
- `analysisId`
- `vesselId`

## 6. Standard Success Response

```text
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully"
}
```

## 7. Standard Error Response

```text
{
  "success": false,
  "errorCode": "ERROR_CODE",
  "message": "Error description"
}
```

## 8. Integration Rules

1. Backend acts as the main integration layer.
2. Frontend communicates with the backend rather than directly depending on internal services.
3. Internal services should return structured JSON responses.
4. Geographic outputs should use WGS84-compatible coordinates for web mapping.
5. Service URLs and ports should be configurable through environment variables.
6. Each service should provide a health endpoint.
7. Observed data, model-derived results and investigation hypotheses should remain distinguishable.
