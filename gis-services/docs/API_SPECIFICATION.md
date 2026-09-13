# GIS API Specification

Base URL: `http://localhost:5001`

All successful responses use:

```json
{
  "success": true,
  "data": {}
}
```

Errors use:

```json
{
  "success": false,
  "error": "message"
}
```

## GET /health

Checks that the GIS service is running.

## POST /api/gis/backtrack

Request:

```json
{
  "spill_id": "SP101",
  "detected_lat": 15.462,
  "detected_lon": 73.845,
  "detected_time": "2026-08-29T10:00:00Z",
  "hours_back": 10.3333333333,
  "scenario": "arabian_sea_demo"
}
```

Returns:
- origin latitude/longitude
- origin time
- confidence
- uncertainty
- GeoJSON origin polygon
- GeoJSON backtrack trail
- detection point

## POST /api/gis/forecast

Request:

```json
{
  "spill_id": "SP101",
  "origin_lat": 15.201,
  "origin_lon": 73.512,
  "origin_time": "2026-08-28T23:40:00Z",
  "hours_forward": 72,
  "scenario": "arabian_sea_demo"
}
```

Returns:
- +24h, +48h, +72h forecast points
- confidence
- uncertainty
- forecast path
- forecast corridor GeoJSON

## POST /api/gis/complete

Request:

```json
{
  "spill_id": "SP101",
  "detected_lat": 15.462,
  "detected_lon": 73.845,
  "detected_time": "2026-08-29T10:00:00Z",
  "hours_back": 10.3333333333,
  "hours_forward": 72,
  "scenario": "arabian_sea_demo"
}
```

Returns both backtracking and forecasting results plus one combined GeoJSON FeatureCollection.

## Frontend notes

Use the GeoJSON directly with Leaflet/React-Leaflet.

- Detection point: red
- Origin uncertainty polygon: cyan
- Backtrack trail: red
- Forecast corridor: orange
- Forecast path: orange
- Forecast markers: orange
