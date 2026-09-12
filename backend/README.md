# BlueGuard AI — Backend

FastAPI + PostgreSQL/PostGIS backend for the SIH 2026 Marine Oil Spill Detection, Spill Backtracking & Vessel Attribution system (Problem Statement 26143).

## Architecture

```
React Frontend
      ↓
   FastAPI
      ↓
   Routers
      ↓
   Services  →  External Service Clients (AI/AIS/GIS/Attribution/Forecast/Impact)
      ↓
Repositories
      ↓
PostgreSQL + PostGIS
```

The backend is the central integration layer. It never trains models or runs backtracking algorithms itself; it orchestrates external services through clean client interfaces and stores validated results.

## Getting Started (Docker)

```bash
docker compose up --build
```

- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

The PostGIS database starts automatically with `POSTGRES_DB=marineguard_db`, and Alembic migrations run on backend startup.

## Getting Started (Local)

1. Create a PostGIS database:

```bash
docker run --name marineguard-db \
  -e POSTGRES_USER=marineguard -e POSTGRES_PASSWORD=marineguard -e POSTGRES_DB=marineguard_db \
  -p 5432:5432 -d postgis/postgis:16-3.4-alpine
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment:

```bash
cp .env.example .env
```

4. Run migrations:

```bash
alembic upgrade head
```

5. Start the API:

```bash
uvicorn app.main:app --reload
```

## API Endpoints

Base URL: `/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/spills/detect` | Register satellite image for detection |
| GET | `/spills/{spillId}` | Get complete spill metadata |
| GET | `/spills/{spillId}/nearby-vessels` | Find vessels near spill area |
| GET | `/vessels/{vesselId}/trajectory` | Get vessel trajectory |
| GET | `/spills/{spillId}/origin` | Estimated source region/time |
| GET | `/spills/{spillId}/suspects` | Ranked suspect vessels |
| GET | `/spills/{spillId}/forecast` | 24/48/72h drift forecast |
| GET | `/spills/{spillId}/impact` | Environmental impact risk |
| GET | `/dashboard/summary` | Dashboard KPIs |
| POST | `/spills/{spillId}/analyze` | Run full investigation pipeline |
| GET | `/spills/{spillId}/report` | Investigation report metadata |

### Response Format

Success:
```json
{"success": true, "data": {}, "message": "..."}
```

Error:
```json
{"success": false, "errorCode": "...", "message": "..."}
```

## Mock Services

The other modules (AI, AIS, GIS, Attribution, Forecast, Impact) are developed by other team members. The backend ships with mock clients in `app/services/`, so the system runs end-to-end immediately. To plug in a real service, replace the mock class with a concrete HTTP client implementing the same interface — no public API changes required.

## Testing

```bash
pytest
```

Tests cover the full pipeline with mocked external services, so no ML models are required.

## Configuration

See `.env.example`. All service URLs and the database connection string come from environment variables.