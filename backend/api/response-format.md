# MarineGuard API Response Format

All APIs should follow a common response structure.

## Successful Response

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully"
}
```

## Error Response

```json
{
  "success": false,
  "errorCode": "ERROR_CODE",
  "message": "Description of the error"
}
```

## Common Integration IDs

The following IDs should be used consistently:

- spillId
- detectionId
- analysisId
- vesselId

## Example: Spill Detection Response

```json
{
  "success": true,
  "data": {
    "spillId": "SPILL-001",
    "detectionId": "DET-001",
    "analysisId": "ANALYSIS-001",
    "confidence": 0.91
  },
  "message": "Spill detected successfully"
}
```

## Example: Vessel Ranking Response

```json
{
  "success": true,
  "data": {
    "spillId": "SPILL-001",
    "vessels": [
      {
        "vesselId": "VESSEL-001",
        "score": 0.87
      }
    ]
  },
  "message": "Suspect vessels ranked successfully"
}
```
