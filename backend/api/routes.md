# MarineGuard API Routes

Base URL:

/api/v1

## Spill APIs

POST /spills/detect

POST /spills/{spillId}/analyze

GET /spills/{spillId}

GET /spills/{spillId}/nearby-vessels

## Vessel APIs

GET /vessels/{vesselId}/trajectory

## Analysis APIs

GET /spills/{spillId}/origin

GET /spills/{spillId}/suspects

GET /spills/{spillId}/forecast

GET /spills/{spillId}/impact

## Dashboard APIs

GET /dashboard/summary

## Report APIs

GET /spills/{spillId}/report
