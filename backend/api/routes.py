from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")


@router.get("/dashboard/summary")
def dashboard_summary():
    return {
        "success": True,
        "data": {
            "activeSpills": 0,
            "criticalSpills": 0,
            "message": "No live spill data connected yet"
        },
        "message": "Dashboard summary retrieved successfully"
    }


@router.get("/spills/{spillId}")
def get_spill(spillId: str):
    return {
        "success": True,
        "data": {
            "spillId": spillId,
            "status": "demo"
        },
        "message": "Spill retrieved successfully"
    }


@router.get("/spills/{spillId}/nearby-vessels")
def nearby_vessels(spillId: str):
    return {
        "success": True,
        "data": {
            "spillId": spillId,
            "vessels": []
        },
        "message": "Nearby vessels retrieved successfully"
    }


@router.get("/spills/{spillId}/origin")
def spill_origin(spillId: str):
    return {
        "success": True,
        "data": {
            "spillId": spillId,
            "origin": None
        },
        "message": "Spill origin retrieved successfully"
    }


@router.get("/spills/{spillId}/suspects")
def spill_suspects(spillId: str):
    return {
        "success": True,
        "data": {
            "spillId": spillId,
            "vessels": []
        },
        "message": "Suspect vessels retrieved successfully"
    }


@router.get("/spills/{spillId}/forecast")
def spill_forecast(spillId: str):
    return {
        "success": True,
        "data": {
            "spillId": spillId,
            "forecast": {
                "24h": None,
                "48h": None,
                "72h": None
            }
        },
        "message": "Spill forecast retrieved successfully"
    }


@router.get("/spills/{spillId}/impact")
def spill_impact(spillId: str):
    return {
        "success": True,
        "data": {
            "spillId": spillId,
            "impactZones": []
        },
        "message": "Impact zones retrieved successfully"
    }


@router.get("/vessels/{vesselId}/trajectory")
def vessel_trajectory(vesselId: str):
    return {
        "success": True,
        "data": {
            "vesselId": vesselId,
            "trajectory": []
        },
        "message": "Vessel trajectory retrieved successfully"
    }
