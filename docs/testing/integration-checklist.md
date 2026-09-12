# BlueGuard-AI Integration Checklist

## 1. Repository and Branch Setup

- [x] Main project folder structure created
- [x] `develop` branch created
- [x] Member feature branches created
- [x] Common project IDs defined
- [x] API base path defined as `/api/v1`

## 2. Member 2 — AI/ML

- [x] Oil-spill segmentation model implemented
- [x] Image preprocessing implemented
- [x] Model evaluation implemented
- [x] Inference output implemented
- [ ] Train/validation/test split verified
- [ ] Final model artifact available for deployment
- [ ] AI service API connected to backend

Expected AI output:
- Spill mask
- Confidence
- Spill polygons
- Number of detected regions

## 3. Member 3 — AIS

- [x] AIS candidate-vessel analysis implemented
- [x] Vessel trajectory processing implemented
- [x] Spatial proximity calculated
- [x] Temporal proximity calculated
- [x] Heading consistency calculated
- [x] Route consistency calculated
- [x] AIS continuity calculated
- [x] Candidate vessels ranked by evidence
- [ ] AIS service API connected to backend

Expected AIS output:
- Vessel ID / MMSI
- IMO number
- Vessel type
- Position
- Timestamp
- Distance from estimated origin
- Time difference
- Evidence score
- Investigation priority

## 4. Member 4 — GIS

- [x] Spill backtracking implemented
- [x] Wind/current environmental inputs supported
- [x] Source time estimation implemented
- [x] Confidence and uncertainty returned
- [x] 24-hour forecast implemented
- [x] 48-hour forecast implemented
- [x] 72-hour forecast implemented
- [x] GeoJSON output implemented
- [x] GIS API endpoints implemented
- [ ] GIS service connected to backend

Expected GIS output:
- Estimated origin
- Origin time
- Confidence
- Uncertainty
- Forecast points
- Forecast GeoJSON

## 5. Member 5 — Backend

- [ ] Database models finalized
- [ ] Database connection configured
- [ ] Backend APIs finalized
- [ ] AI service integration completed
- [ ] GIS service integration completed
- [ ] AIS service integration completed
- [ ] Attribution workflow integrated
- [ ] Forecast workflow integrated
- [ ] Error handling completed
- [ ] Health checks completed

## 6. Member 6 — Frontend

- [ ] Dashboard created
- [ ] Spill map created
- [ ] Spill detection displayed
- [ ] Spill origin displayed
- [ ] Vessel trajectories displayed
- [ ] Suspect vessel ranking displayed
- [ ] Forecast displayed
- [ ] Impact zones displayed
- [ ] Confidence and uncertainty displayed
- [ ] Backend APIs connected
- [ ] Loading and error states handled

## 7. End-to-End Integration

- [ ] Satellite image submitted
- [ ] AI detects spill
- [ ] Spill geometry generated
- [ ] Spill origin estimated
- [ ] Source time estimated
- [ ] AIS candidate vessels retrieved
- [ ] Vessel evidence calculated
- [ ] Suspect vessels ranked
- [ ] Spill forecast generated
- [ ] Impact zones generated
- [ ] Results displayed on dashboard
- [ ] Investigation report generated

## 8. Testing

- [ ] AI model tested on held-out data
- [ ] GIS coordinate handling tested
- [ ] Backtracking tested
- [ ] Forecasting tested
- [ ] AIS timestamps validated
- [ ] AIS duplicate records checked
- [ ] Backend API tests completed
- [ ] Frontend integration tests completed
- [ ] Complete fixed demo scenario tested

## 9. Deployment

- [ ] Environment variables configured
- [ ] Dependencies documented
- [ ] Services start successfully
- [ ] Health endpoints verified
- [ ] API communication verified
- [ ] Database connection verified
- [ ] Frontend-backend connection verified
- [ ] Demo data available
- [ ] Deployment instructions documented

## 10. Final SIH Demo

- [ ] Historical satellite scene loaded
- [ ] Spill detected
- [ ] Spill characteristics displayed
- [ ] Origin investigation demonstrated
- [ ] AIS vessels displayed
- [ ] Ranked vessel evidence displayed
- [ ] 24/48/72-hour forecast demonstrated
- [ ] Impact zones displayed
- [ ] Uncertainty/confidence explained
- [ ] Final report demonstrated
