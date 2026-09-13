from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.spill_repository import SpillRepository
from app.repositories.detection_repository import DetectionRepository
from app.repositories.vessel_repository import VesselRepository
from app.core.security import generate_id
from app.core.exceptions import SpillNotFoundError
from app.schemas.spill import (
    DetectRequest,
    DetectResponseData,
    SpillDetail,
    NearbyVesselsData,
    NearbyVessel,
    Coordinate,
    SpillOriginData,
    OriginPoint,
    SuspectsData,
    SuspectVessel,
    SuspectEvidence,
)
from app.services.ai_client import build_ai_client


class SpillService:
    def __init__(self, db: Session):
        self.db = db
        self.spill_repo = SpillRepository(db)
        self.detection_repo = DetectionRepository(db)
        self.vessel_repo = VesselRepository(db)
        self.ai_client = build_ai_client()

    async def detect_spill(self, request: DetectRequest) -> DetectResponseData:
        ai_result = await self.ai_client.detect(request.imageUrl, image_bounds=request.imageBounds)

        if not ai_result.detected:
            spill_id = generate_id("SP")
            spill = self.spill_repo.create(
                spill_id=spill_id,
                detected_at=datetime.now(timezone.utc),
                area_sq_km=0.0,
                severity="LOW",
                confidence=ai_result.confidence,
                centroid_lon=ai_result.centroid_lon,
                centroid_lat=ai_result.centroid_lat,
                geometry_wkt=ai_result.geometry_wkt,
                status="DETECTED",
            )
            self.detection_repo.create(
                detection_id=generate_id("DET"),
                spill_id=spill_id,
                image_source=request.source,
                image_timestamp=request.captureTime,
                model_version=ai_result.model_version,
                mask_uri=ai_result.mask_uri,
                prediction_confidence=ai_result.confidence,
            )
            self.db.commit()
            return DetectResponseData(
                spillId=spill_id,
                detected=False,
                confidence=ai_result.confidence,
                areaSqKm=0.0,
                severity="LOW",
                centroid=Coordinate(lat=ai_result.centroid_lat, lon=ai_result.centroid_lon),
            )

        spill_id = generate_id("SP")
        spill = self.spill_repo.create(
            spill_id=spill_id,
            detected_at=datetime.now(timezone.utc),
            area_sq_km=ai_result.area_sq_km,
            severity=ai_result.severity,
            confidence=ai_result.confidence,
            centroid_lon=ai_result.centroid_lon,
            centroid_lat=ai_result.centroid_lat,
            geometry_wkt=ai_result.geometry_wkt,
            status="DETECTED",
        )
        self.detection_repo.create(
            detection_id=generate_id("DET"),
            spill_id=spill_id,
            image_source=request.source,
            image_timestamp=request.captureTime,
            model_version=ai_result.model_version,
            mask_uri=ai_result.mask_uri,
            prediction_confidence=ai_result.confidence,
        )
        self.db.commit()

        return DetectResponseData(
            spillId=spill_id,
            detected=True,
            confidence=ai_result.confidence,
            areaSqKm=ai_result.area_sq_km,
            severity=ai_result.severity,
            centroid=Coordinate(lat=ai_result.centroid_lat, lon=ai_result.centroid_lon),
        )

    def get_spill(self, spill_id: str) -> SpillDetail:
        spill = self.spill_repo.get_by_id(spill_id)
        if not spill:
            raise SpillNotFoundError(spill_id)
        from geoalchemy2 import shape
        centroid = shape.to_shape(spill.centroid)
        return SpillDetail(
            spillId=spill.spill_id,
            status=spill.status,
            areaSqKm=spill.area_sq_km,
            severity=spill.severity,
            confidence=spill.confidence,
            detectedAt=spill.detected_at,
            centroid=Coordinate(lat=centroid.y, lon=centroid.x),
        )

    def get_nearby_vessels(self, spill_id: str) -> NearbyVesselsData:
        spill = self.spill_repo.get_by_id(spill_id)
        if not spill:
            raise SpillNotFoundError(spill_id)

        results = self.spill_repo.get_nearby_vessels(spill_id)
        vessels = []
        for vessel, position, distance_m in results:
            vessels.append(
                NearbyVessel(
                    vesselId=vessel.vessel_id,
                    name=vessel.name,
                    distanceKm=round(distance_m / 1000.0, 1),
                )
            )

        return NearbyVesselsData(spillId=spill_id, vessels=vessels)

    def get_origin(self, spill_id: str) -> SpillOriginData:
        from app.repositories.origin_repository import OriginRepository
        origin_repo = OriginRepository(self.db)
        origin = origin_repo.get_by_spill_id(spill_id)
        if not origin:
            raise SpillNotFoundError(spill_id)
        from geoalchemy2 import shape
        geom = shape.to_shape(origin.geometry)
        centroid = geom.centroid
        return SpillOriginData(
            spillId=spill_id,
            estimatedOrigin=OriginPoint(lat=centroid.y, lon=centroid.x),
            estimatedTime=origin.estimated_time,
            confidence=origin.confidence,
        )

    def get_suspects(self, spill_id: str) -> SuspectsData:
        from app.repositories.suspect_repository import SuspectRepository
        suspect_repo = SuspectRepository(self.db)
        scores = suspect_repo.get_by_spill_id(spill_id)
        suspects = []
        for s in scores:
            vessel = self.vessel_repo.get_by_id(s.vessel_id)
            name = vessel.name if vessel else "Unknown"
            evidence = s.evidence_json or {}
            suspects.append(
                SuspectVessel(
                    vesselId=s.vessel_id,
                    name=name,
                    score=s.score,
                    evidence=SuspectEvidence(
                        distanceKm=evidence.get("distanceKm", 0.0),
                        timeDifferenceMin=evidence.get("timeDifferenceMin", 0.0),
                        routeConsistency=evidence.get("routeConsistency", 0.0),
                        aisContinuity=evidence.get("aisContinuity", 0.0),
                    ),
                )
            )
        return SuspectsData(spillId=spill_id, suspects=suspects)
