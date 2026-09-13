# BlueGuard-AI Fixed Demo Scenario

## 1. Scenario

Use a historical Arabian Sea oil-spill detection scenario for the final system demonstration.

The scenario provides a fixed input so all integrated services can be tested consistently.

## 2. Spill Detection Input

Detection location:

- Latitude: 15.201
- Longitude: 73.512

Detection timestamp:

```text
2026-08-29T10:00:00Z
```

AI service input:

- Satellite image
- Image metadata
- Model version

Expected AI outputs:

- Spill mask
- Spill confidence
- Spill polygons
- Number of detected regions

## 3. GIS Backtracking

Use the detected spill location and timestamp with environmental data.

Expected outputs:

- Estimated origin
- Estimated source time
- Confidence
- Uncertainty
- Backtracking GeoJSON

Reference origin for the demo scenario:

- Latitude: 15.201
- Longitude: 73.512
- Source time: 2026-08-28T23:40:00Z

## 4. AIS Candidate Analysis

Use the estimated spill origin and source time to search AIS vessel positions.

Demo search parameters:

- Spatial radius: 10 km
- Temporal window: 60 minutes

Expected outputs:

- Candidate vessels
- MMSI
- IMO number
- Vessel type
- Position
- Timestamp
- Distance from origin
- Time difference
- Heading consistency
- Route consistency
- AIS continuity
- Evidence score
- Investigation priority

## 5. Spill Forecast

Generate forward predictions from the estimated origin.

Required forecast horizons:

- 24 hours
- 48 hours
- 72 hours

Expected outputs:

- Forecast timestamp
- Predicted latitude
- Predicted longitude
- Estimated affected area
- Confidence
- Uncertainty
- Forecast GeoJSON

Reference forecast points:

| Horizon | Latitude | Longitude | Area (km²) |
|---|---:|---:|---:|
| 24 hours | 15.58 | 74.12 | 22.4 |
| 48 hours | 15.89 | 74.45 | 31.7 |
| 72 hours | 16.12 | 74.78 | 43.2 |

## 6. Dashboard Demonstration

The final dashboard should demonstrate the following sequence:

Satellite image  
→ Detect spill  
→ Display spill characteristics  
→ Estimate origin  
→ Display source time and uncertainty  
→ Load AIS vessel candidates  
→ Display vessel trajectories  
→ Show ranked candidate vessels  
→ Display evidence information  
→ Generate 24/48/72-hour forecast  
→ Display impact zones  
→ Generate investigation report

## 7. Investigation Principle

The demonstration should clearly distinguish:

- Observed data
- Model-derived results
- Investigation hypotheses

The system provides investigation-support information and does not automatically establish legal responsibility.

## 8. Demo Success Criteria

The complete scenario should be reproducible from the same input data.

The integrated system should allow the team to demonstrate:

- AI oil-spill detection
- GIS backtracking
- AIS candidate-vessel analysis
- Explainable vessel ranking
- Spill movement forecasting
- Uncertainty and confidence
- GIS visualization
- Investigation report generation
