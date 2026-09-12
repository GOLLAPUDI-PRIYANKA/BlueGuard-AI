# BlueGuard-AI Data Flow

## 1. Overall System Flow

Satellite Image
→ Image Validation and Georeferencing
→ AI Spill Detection
→ Spill Geometry and Characteristics
→ GIS Backtracking
→ Estimated Spill Origin and Source Time
→ AIS Candidate Vessel Search
→ Vessel Trajectory and Evidence Analysis
→ Suspect Vessel Ranking
→ Spill Movement Forecast
→ Impact Zone Generation
→ Backend API
→ GIS Dashboard
→ Investigation Report

## 2. Member 2 — AI/ML Data Flow

### Input

- Satellite image
- Image metadata
- Model version

### Processing

The AI service performs image preprocessing and oil-spill segmentation.

### Output

- Spill mask
- Detection confidence
- Spill polygons
- Number of detected regions

Note: AI polygon coordinates are image/pixel coordinates until georeferenced.

## 3. Georeferencing

### Input

- AI spill polygons
- Satellite image metadata
- Image geographic bounds

### Processing

Pixel coordinates are converted into geographic coordinates.

### Output

- Geographic spill polygon
- Spill centroid
- Spill area
- Geographic spill location

## 4. Member 4 — GIS Backtracking

### Input

- Spill location
- Detection timestamp
- Wind data
- Ocean current data

### Processing

The GIS backtracking model estimates where and when the spill may have originated.

### Output

- Estimated origin latitude
- Estimated origin longitude
- Estimated source time
- Confidence
- Uncertainty
- GeoJSON representation

## 5. Member 3 — AIS Candidate Analysis

### Input

- Estimated spill origin
- Spill/source timestamp
- AIS vessel positions
- Spatial search radius
- Temporal search window

### Processing

The AIS service:

1. Builds vessel trajectories.
2. Filters positions by spatial and temporal proximity.
3. Calculates spatial proximity.
4. Calculates temporal proximity.
5. Calculates heading consistency.
6. Calculates route consistency.
7. Calculates AIS continuity.
8. Calculates an evidence score.
9. Ranks candidate vessels.

### Output

- Candidate rank
- MMSI
- IMO number
- Vessel type
- Vessel position
- Timestamp
- Distance from origin
- Time difference
- Evidence factors
- Evidence score
- Investigation priority

## 6. Forecasting

### Input

- Estimated spill origin
- Origin time
- Wind data
- Ocean current data

### Processing

The GIS forecasting model predicts the forward movement of the spill.

### Output

- 24-hour forecast
- 48-hour forecast
- 72-hour forecast
- Predicted locations
- Estimated affected area
- Confidence
- Uncertainty
- GeoJSON forecast representation

## 7. Backend Integration

The backend acts as the central integration layer.

### Main sequence

AI Detection
→ GIS Backtracking
→ AIS Candidate Analysis
→ Vessel Attribution
→ Forecasting
→ Impact Analysis
→ Dashboard

### Common Identifiers

- `spillId`
- `detectionId`
- `analysisId`
- `vesselId`

## 8. Frontend Data Flow

The dashboard receives processed results from the backend and displays:

- Detected spill
- Spill characteristics
- Estimated origin
- Vessel trajectories
- Ranked candidate vessels
- Evidence information
- Forecast movement
- Impact zones
- Confidence and uncertainty

## 9. Investigation Principle

The system provides investigation-support information.

Observed data, model-derived results, and investigation hypotheses should be clearly distinguished in the final dashboard and report.
