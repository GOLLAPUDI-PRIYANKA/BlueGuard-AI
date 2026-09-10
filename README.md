# MarineGuard AI – SIH 26143

AI-Based Oil Spill Detection, Spill Backtracking & Vessel Attribution System.

## Project Goal
MarineGuard supports:
1. Satellite scene selection/upload
2. Oil-spill detection
3. Spill characterization
4. Spill-origin backtracking
5. AIS vessel correlation
6. Candidate-vessel attribution
7. 24/48/72-hour drift forecasting
8. Environmental impact assessment
9. GIS visualization and reporting

## Repository Structure

```text
marineguard/
├── frontend/              # Member 6 – React GIS dashboard
├── backend/               # Member 5 – Backend APIs/database/orchestration
├── ai-services/           # Member 2 – Oil-spill AI detection
├── ais-services/          # Member 3 – AIS analysis
├── gis-services/          # Member 4 – GIS/backtracking/forecast/impact
├── data/
│   ├── satellite/
│   ├── ais/
│   └── environmental/
├── docs/
│   ├── architecture/
│   ├── api/
│   └── testing/
├── docker-compose.yml
├── README.md
└── .gitignore
```

## Public API Base Path

`/api/v1`

The public APIs are exposed through the backend. Specialist modules use internal service contracts.

## Common IDs

- `spillId` – unique oil-spill identifier
- `detectionId` – unique detection identifier
- `vesselId` – unique vessel identifier
- `analysisId` – unique analysis identifier

## Branching Strategy

- `main` – stable/demo-ready code
- `develop` – integration branch
- `feature/member2-ai`
- `feature/member3-ais`
- `feature/member4-gis`
- `feature/member5-backend`
- `feature/member6-frontend`

Feature branches are merged into `develop` through pull requests. Member 1 coordinates integration and reviews.

## Integration Flow

Satellite Image
→ AI Detection
→ GIS Backtracking
→ AIS Candidate Search
→ Attribution
→ Forecast
→ Impact
→ Backend
→ React GIS Dashboard

## Development Rule

Do not commit large raw satellite/AIS datasets to Git. Keep sample/test data small and document the source of larger datasets.

## API Documentation

Place the final API contract under:

`docs/api/api-contract.md`

## Architecture Documentation

Place the system architecture document/diagram under:

`docs/architecture/`

## Testing Documentation

Place integration and end-to-end test cases under:

`docs/testing/`

## Team Rule

Every member must provide:
- runnable module/code
- requirements/dependency file
- sample input
- sample output
- endpoint details, if applicable
- short README for their module

Before merging, the module must follow the agreed API contract.
