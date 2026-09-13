# GIS Model Assumptions

## 1. Coordinate system
- Inputs are latitude/longitude in WGS84.
- GeoJSON coordinates are always `[longitude, latitude]`.

## 2. Baseline drift model
For generic inputs:

`oil_velocity = ocean_current + 0.03 × wind_velocity`

- Wind and current components are expected in m/s.
- The model is a baseline advection model for the MVP.
- It is not a high-fidelity ocean circulation model.

## 3. Backtracking
- The model moves the detected point backward in time using the estimated drift velocity.
- Missing environmental data are handled with a deterministic fallback velocity so the demo remains usable.

## 4. Forecasting
- The model moves the estimated origin forward.
- The dashboard receives 24h, 48h and 72h points plus an uncertainty corridor.
- Uncertainty increases with forecast duration.

## 5. Demo reference mode
When `scenario` is `arabian_sea_demo`, the exact reference outputs supplied for SP101 are returned. This makes the Sunday demo reproducible.

## 6. Limitations
- No diffusion/turbulence solver.
- No real-time ocean API is required for the MVP.
- No automatic vessel accusation is performed by this module.
- Real deployment should replace the sample environment data with validated ocean/wind products and a calibrated drift model.
