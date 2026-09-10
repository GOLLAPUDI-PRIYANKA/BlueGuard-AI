# BlueGuard-AI Backend

## Purpose

The backend acts as the main integration layer of the BlueGuard-AI system.

## Responsibilities

- Connect AI-based oil spill detection
- Connect GIS spill backtracking
- Connect AIS vessel analysis
- Connect vessel attribution and ranking
- Connect spill movement forecasting
- Connect impact analysis
- Provide APIs for the frontend dashboard

## API Base URL

/api/v1

## Main Workflow

Satellite Scene
→ AI Detection
→ Spill Analysis
→ GIS Backtracking
→ AIS Candidate Vessels
→ Attribution Ranking
→ Forecast
→ Impact Analysis
→ Dashboard

## Main API Endpoints

POST /api/v1/spills/detect

POST /api/v1/spills/{spillId}/analyze

GET /api/v1/spills/{spillId}

GET /api/v1/spills/{spillId}/nearby-vessels

GET /api/v1/vessels/{vesselId}/trajectory

GET /api/v1/spills/{spillId}/origin

GET /api/v1/spills/{spillId}/suspects

GET /api/v1/spills/{spillId}/forecast

GET /api/v1/spills/{spillId}/impact

GET /api/v1/dashboard/summary

GET /api/v1/spills/{spillId}/report

## Integration IDs

- spillId
- detectionId
- analysisId
- vesselId

## Important Note

The system is an investigation-support system.

Vessel rankings and attribution scores must not be treated as automatic legal accusations.
