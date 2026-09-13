# Environmental sample data

This folder contains a small mock dataset for the SIH 26143 demo.

The MVP expects:
- `wind_u`, `wind_v`: wind components in m/s
- `current_u`, `current_v`: ocean-current components in m/s
- `timestamp`: ISO-8601 UTC time

The model uses:

`oil_velocity = current_velocity + 0.03 * wind_velocity`

This sample is intentionally small. Do not commit large raw environmental/satellite datasets to Git.
