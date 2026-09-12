from typing import List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from candidate_service import generate_candidate_vessels


# =============================================================
# FASTAPI APPLICATION
# =============================================================

app = FastAPI(
    title="MarineGuard AIS Service",
    description=(
        "AIS-based vessel candidate generation and "
        "explainable attribution service."
    ),
    version="1.0.0"
)


# =============================================================
# REQUEST MODELS
# =============================================================

class OriginPoint(BaseModel):
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude of origin polygon point"
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude of origin polygon point"
    )


class CandidateRequest(BaseModel):

    origin_polygon: List[OriginPoint] = Field(
        ...,
        min_length=1,
        description="Estimated spill-origin polygon"
    )

    spill_timestamp: str = Field(
        ...,
        description="Estimated spill/source timestamp in ISO format"
    )

    spatial_radius_km: float = Field(
        10.0,
        gt=0,
        description="Maximum vessel distance from origin in km"
    )

    temporal_window_minutes: float = Field(
        60.0,
        gt=0,
        description="Maximum time difference from spill in minutes"
    )


# =============================================================
# RESPONSE MODELS
# =============================================================

class OriginResponse(BaseModel):
    latitude: float
    longitude: float


class CandidateVessel(BaseModel):

    candidateRank: int

    mmsi: int

    imo_number: Optional[str] = None

    vessel_type: Optional[str] = None

    latitude: float

    longitude: float

    timestamp: str

    distanceKm: float

    timeDifferenceMin: float

    headingConsistency: float

    routeConsistency: float

    aisContinuity: float

    spatialProximity: float

    temporalProximity: float

    evidenceScore: float

    evidencePercentage: float

    investigationPriority: str


class CandidateResponse(BaseModel):

    candidate_count: int

    origin: Optional[OriginResponse] = None

    candidates: List[CandidateVessel]


# =============================================================
# AIS DATA
# =============================================================

AIS_FILE = "data/ais_sample.csv"


try:

    AIS_DATA = pd.read_csv(
        AIS_FILE
    )

except FileNotFoundError:

    AIS_DATA = pd.DataFrame()


# =============================================================
# ROOT ENDPOINT
# =============================================================

@app.get("/")
def root():

    return {
        "service": "MarineGuard AIS Service",
        "status": "running",
        "version": "1.0.0"
    }


# =============================================================
# HEALTH ENDPOINT
# =============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "ais_records": len(AIS_DATA)
    }


# =============================================================
# CANDIDATE VESSEL ENDPOINT
# =============================================================

@app.post(
    "/candidate-vessels",
    response_model=CandidateResponse
)
def candidate_vessels(
    request: CandidateRequest
):

    # ---------------------------------------------------------
    # CHECK AIS DATA
    # ---------------------------------------------------------

    if AIS_DATA.empty:

        raise HTTPException(
            status_code=500,
            detail="AIS dataset could not be loaded."
        )

    # ---------------------------------------------------------
    # CALCULATE ORIGIN CENTROID
    # ---------------------------------------------------------

    origin_latitude = (
        sum(
            point.latitude
            for point in request.origin_polygon
        )
        /
        len(request.origin_polygon)
    )

    origin_longitude = (
        sum(
            point.longitude
            for point in request.origin_polygon
        )
        /
        len(request.origin_polygon)
    )

    # ---------------------------------------------------------
    # GENERATE CANDIDATES
    # ---------------------------------------------------------

    candidates = generate_candidate_vessels(

        AIS_DATA,

        origin_latitude,
        origin_longitude,

        request.spill_timestamp,

        request.spatial_radius_km,
        request.temporal_window_minutes
    )

    # ---------------------------------------------------------
    # NO CANDIDATES
    # ---------------------------------------------------------

    if candidates.empty:

        return CandidateResponse(
            candidate_count=0,
            origin=OriginResponse(
                latitude=origin_latitude,
                longitude=origin_longitude
            ),
            candidates=[]
        )

    # ---------------------------------------------------------
    # CLEAN NaN VALUES
    # ---------------------------------------------------------

    candidates = candidates.astype(
        object
    ).where(
        pd.notna(candidates),
        None
    )

    # ---------------------------------------------------------
    # CONVERT TIMESTAMPS TO STRING
    # ---------------------------------------------------------

    if "timestamp" in candidates.columns:

        candidates["timestamp"] = (
            candidates["timestamp"]
            .astype(str)
        )

    # ---------------------------------------------------------
    # CONVERT DATAFRAME TO RECORDS
    # ---------------------------------------------------------

    candidate_records = (
        candidates
        .to_dict(
            orient="records"
        )
    )

    # ---------------------------------------------------------
    # RETURN RESPONSE
    # ---------------------------------------------------------

    return CandidateResponse(

        candidate_count=len(
            candidate_records
        ),

        origin=OriginResponse(

            latitude=origin_latitude,
            longitude=origin_longitude

        ),

        candidates=candidate_records
    )
