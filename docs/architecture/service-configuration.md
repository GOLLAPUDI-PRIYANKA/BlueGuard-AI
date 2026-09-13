# BlueGuard-AI Service Configuration

## 1. Service Overview

| Service | Responsibility | Default Port |
|---|---|---:|
| Backend | Central API and system integration | 8000 |
| AI Service | Oil-spill detection and segmentation | 5002 |
| AIS Service | Vessel candidate analysis and trajectory processing | 5003 |
| GIS Service | Backtracking, forecasting and geospatial processing | 5001 |
| Frontend | GIS dashboard and user interface | 3000 |

## 2. Service Communication

Frontend  
→ Backend API

Backend  
→ AI Service  
→ AIS Service  
→ GIS Service

AI Service  
→ Returns spill detection results

GIS Service  
→ Returns spill origin, uncertainty and forecast

AIS Service  
→ Returns candidate vessels and evidence scores

Backend  
→ Combines service results and provides data to frontend

## 3. Environment Configuration

Service URLs should be configurable through environment variables.

Example:

```text
BACKEND_URL=http://localhost:8000
AI_SERVICE_URL=http://localhost:5002
AIS_SERVICE_URL=http://localhost:5003
GIS_SERVICE_URL=http://localhost:5001
FRONTEND_URL=http://localhost:3000
```

## 4. API Versioning

Public backend APIs use:

```text
/api/v1
```

Internal service endpoints may use service-specific paths such as:

```text
/predict
/candidate-vessels
/backtrack
/forecast
```

## 5. Health Checks

Each deployed service should provide a health endpoint.

Example:

```text
GET /health
```

A healthy response should clearly indicate that the service is running.

## 6. Deployment Principle

Each service should be independently startable and configurable.

The final deployment should allow:

1. Frontend to communicate with the backend.
2. Backend to communicate with AI, AIS and GIS services.
3. Services to use configured environment variables.
4. Health checks to verify service availability.
5. Sample/demo data to be available for the final SIH demonstration.

## 7. MVP Integration

For the initial MVP, services may run locally on separate ports.

The same environment-variable structure can later be used when services are deployed using containers or separate hosts.

## 8. Configuration Notes

Ports and URLs are configuration defaults for the integration stage.

They can be changed during final deployment without changing the core service logic.
