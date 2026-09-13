# BlueGuard-AI End-to-End Integration Test

## Purpose

This test verifies that the complete BlueGuard-AI workflow can operate from satellite input to dashboard output.

## Test Scenario

Use one fixed historical/sample satellite scene containing an oil-spill-like region.

## Step 1 — Satellite Input

Input:

- Sample satellite image
- Scene metadata
- Acquisition timestamp
- Geographic reference information

Expected:

- Image is accepted by the system.
- Scene metadata is available.

## Step 2 — AI Spill Detection

Send the satellite image to the AI detection service.

Expected output:

- Spill mask
- Detection confidence
- Spill polygon/regions
- detectionId

## Step 3 — Spill Analysis

Calculate:

- Spill area
- Spill centroid
- Severity
- confidence

Expected:

- spillId is created.
- analysisId is created.

## Step 4 — GIS Backtracking

Provide:

- Spill geometry
- Wind data
- Current data

Expected:

- Estimated origin region
- Estimated source time

## Step 5 — AIS Candidate Search

Use the estimated origin and time window.

Expected:

- Candidate vessel IDs
- Vessel positions
- Relevant trajectory features

## Step 6 — Vessel Attribution

Calculate attribution scores using:

- Spatial proximity
- Temporal proximity
- Trajectory consistency
- Source-region overlap
- AIS behavior signal

Expected:

- Ranked candidate vessels
- Score
- Supporting evidence

## Step 7 — Spill Forecast

Generate:

- 24-hour forecast
- 48-hour forecast
- 72-hour forecast
- Uncertainty information

## Step 8 — Impact Analysis

Generate:

- Potential impact zones
- Affected-area information

## Step 9 — Dashboard

Display:

- Satellite scene
- Spill polygon
- Spill information
- Estimated origin
- Vessel trajectories
- Ranked vessels
- Evidence
- Forecast
- Impact zones

## Integration IDs

The following IDs must remain consistent:

- spillId
- detectionId
- analysisId
- vesselId

## Pass Criteria

The test passes when:

1. The satellite scene is accepted.
2. AI produces a spill detection.
3. Spill geometry is available.
4. GIS produces an estimated origin/time.
5. AIS returns candidate vessels.
6. Attribution produces ranked candidates.
7. Forecast produces 24/48/72-hour results.
8. Impact zones are generated.
9. Dashboard displays the complete investigation workflow.

## Important Limitation

The system provides investigation-support information.

A vessel ranking must not be presented as an automatic legal accusation.
