# BlueGuard-AI Integration Flow

## End-to-End Pipeline

1. Satellite image is provided.
2. AI service detects the oil spill.
3. Spill polygon and confidence are generated.
4. GIS service estimates spill origin and source time.
5. AIS service searches for candidate vessels.
6. Vessel features are generated.
7. Attribution service ranks candidate vessels.
8. Forecast service predicts future spill movement.
9. Impact zones are generated.
10. Frontend dashboard displays the results.

## Service Flow

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
Impact
↓
Dashboard

## Main Integration IDs

- spillId
- detectionId
- analysisId
- vesselId

## Backend Role

The backend acts as the main integration layer between the different services and the frontend dashboard.

## Important Rule

The system is an investigation-support system.

A vessel ranking must not be treated as an automatic legal accusation.
