# Member 4 - GIS Services

SIH 26143: AI-Based Marine Oil Spill Detection, Backtracking and Forecasting

This service is responsible for:

1. Backtracking a detected spill to estimate a source region.
2. Forecasting where the spill may move over 24/48/72 hours.
3. Returning map-ready GeoJSON.

## Folder structure

```text
gis-services/
├── backtracking/
│   ├── __init__.py
│   ├── drift_model.py
│   └── assumptions.md
├── forecasting/
│   ├── __init__.py
│   ├── drift_prediction.py
│   └── assumptions.md
├── spatial/
│   ├── __init__.py
│   ├── geometry_utils.py
│   └── geojson_builder.py
├── data/
│   ├── __init__.py
│   ├── environmental/
│   │   ├── README.md
│   │   └── arabian_sea_aug2026.json
│   └── adapters/
│       ├── __init__.py
│       └── environment_adapter.py
├── api/
│   ├── __init__.py
│   └── app.py
├── tests/
│   ├── __init__.py
│   ├── test_backtrack.py
│   ├── test_forecast.py
│   └── test_geojson.py
├── docs/
│   ├── MODEL_ASSUMPTIONS.md
│   ├── API_SPECIFICATION.md
│   └── DEMO_SCRIPT.md
├── README.md
├── requirements.txt
├── .env
├── .env.example
└── .gitignore
```

## Requirements

- Python 3.10+
- Flask
- Flask-CORS
- pytest

## Setup on Windows

From inside `gis-services`:

```powershell
py -3.10 -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run tests

```powershell
pytest tests -v
```

## Run API

From the `gis-services` folder:

```powershell
python api/app.py
```

API runs on:

`http://localhost:5001`

Health check:

```text
GET http://localhost:5001/health
```

## Demo request

```powershell
curl.exe -X POST http://localhost:5001/api/gis/complete `
  -H "Content-Type: application/json" `
  -d '{"spill_id":"SP101","detected_lat":15.462,"detected_lon":73.845,"detected_time":"2026-08-29T10:00:00Z","hours_back":10.3333333333,"hours_forward":72,"scenario":"arabian_sea_demo"}'
```

## Expected demo result

Backtracking:
- Origin: 15.201 N, 73.512 E
- Origin time: 2026-08-28 23:40 UTC
- Confidence: 81%
- Uncertainty: ±12 km

Forecast:
- +24h: 15.58 N, 74.12 E
- +48h: 15.89 N, 74.45 E
- +72h: 16.12 N, 74.78 E

## Important

This is an MVP baseline model. It is designed for a reproducible hackathon demonstration, not operational oil-spill response. Do not present the reference scenario as live ocean data.
