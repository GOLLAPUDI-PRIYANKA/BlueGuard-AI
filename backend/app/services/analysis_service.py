import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.repositories.spill_repository import SpillRepository
from app.repositories.origin_repository import OriginRepository
from app.repositories.suspect_repository import SuspectRepository
from app.repositories.vessel_repository import VesselRepository
from app.repositories.forecast_repository import ForecastRepository
from app.repositories.impact_repository import ImpactRepository
from app.core.security import generate_id
from app.core.exceptions import (
    SpillNotFoundError,
    AnalysisFailedError,
)
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponseData
from app.services.gis_client import MockGISClient
from app.services.ais_client import MockAISClient
from app.services.attribution_client import MockAttributionClient
from app.services.forecast_client import MockForecastClient
from app.services.impact_client import MockImpactClient
from app.models.spill import SpillStatus

logger = logging.getLogger("marineguard.analysis")


class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.spill_repo = SpillRepository(db)
        self.origin_repo = OriginRepository(db)
        self.suspect_repo = SuspectRepository(db)
        self.vessel_repo = VesselRepository(db)
        self.forecast_repo = ForecastRepository(db)
        self.impact_repo = ImpactRepository(db)
        self.gis_client = MockGISClient()
        self.ais_client = MockAISClient()
        self.attribution_client = MockAttributionClient()
        self.forecast_client = MockForecastClient()
        self.impact_client = MockImpactClient()

    async def analyze(self, spill_id: str, request: AnalyzeRequest) -> AnalyzeResponseData:
        spill = self.spill_repo.get_by_id(spill_id)
        if not spill:
            raise SpillNotFoundError(spill_id)

        try:
            self.spill_repo.update_status(spill_id, SpillStatus.UNDER_INVESTIGATION)
            self.db.commit()

            from geoalchemy2 import shape
            centroid = shape.to_shape(spill.centroid)
            spill_geom_wkt = shape.to_shape(spill.geometry).wkt

            origin = await self._run_backtracking(
                spill_id, spill_geom_wkt, centroid.x, centroid.y, spill.detected_at
            )

            candidates = await self._run_ais_search(
                origin_lon=origin["lon"],
                origin_lat=origin["lat"],
                start_time=origin["time"],
                end_time=spill.detected_at.isoformat(),
                ais_hours_before=request.aisHoursBefore,
                ais_hours_after=request.aisHoursAfter,
            )

            suspect_scores = await self._run_attribution(
                spill_id=spill_id,
                origin_lon=origin["lon"],
                origin_lat=origin["lat"],
                origin_time=origin["time"],
                candidates=candidates,
            )

            if request.includeForecast:
                await self._run_forecast(
                    spill_id=spill_id,
                    spill_lon=centroid.x,
                    spill_lat=centroid.y,
                    spill_area=spill.area_sq_km,
                )

            if request.includeImpact:
                await self._run_impact(
                    spill_id=spill_id,
                    spill_lon=centroid.x,
                    spill_lat=centroid.y,
                    spill_area=spill.area_sq_km,
                    spill_geom_wkt=spill_geom_wkt,
                )

            self.spill_repo.update_status(spill_id, SpillStatus.ANALYSIS_COMPLETE)
            self.db.commit()

            top_vessel = None
            if suspect_scores:
                top_vessel = suspect_scores[0].vessel_id

            return AnalyzeResponseData(
                spillId=spill_id,
                status="ANALYSIS_COMPLETE",
                originConfidence=origin["confidence"],
                topSuspectVesselId=top_vessel,
            )

        except Exception as e:
            logger.error(f"Analysis failed for {spill_id}: {e}")
            self.spill_repo.update_status(spill_id, SpillStatus.DETECTED)
            self.db.commit()
            raise AnalysisFailedError(str(e))

    async def _run_backtracking(
        self, spill_id: str, spill_geom_wkt: str, centroid_lon: float, centroid_lat: float, detection_time: datetime
    ) -> dict:
        result = await self.gis_client.backtrack(
            spill_geometry_wkt=spill_geom_wkt,
            centroid_lon=centroid_lon,
            centroid_lat=centroid_lat,
            detection_time=detection_time.isoformat(),
        )

        self.origin_repo.delete_by_spill_id(spill_id)
        self.origin_repo.create(
            origin_id=generate_id("ORG"),
            spill_id=spill_id,
            estimated_time=result.estimated_time,
            geometry_wkt=result.geometry_wkt,
            confidence=result.confidence,
            method=result.method,
        )
        self.db.commit()

        return {
            "lon": result.origin_lon,
            "lat": result.origin_lat,
            "time": result.estimated_time,
            "confidence": result.confidence,
        }

    async def _run_ais_search(
        self,
        origin_lon: float,
        origin_lat: float,
        start_time: str,
        end_time: str,
        ais_hours_before: int,
        ais_hours_after: int,
    ) -> list:
        result = await self.ais_client.get_candidate_vessels(
            origin_lon=origin_lon,
            origin_lat=origin_lat,
            start_time=start_time,
            end_time=end_time,
        )

        for candidate in result.candidates:
            self.vessel_repo.upsert(
                vessel_id=candidate.vessel_id,
                mmsi=candidate.mmsi,
                name=candidate.name,
                vessel_type=candidate.vessel_type,
                flag_country=candidate.flag_country,
            )

            from app.models.vessel_position import VesselPosition
            for pt in candidate.trajectory:
                pos_id = generate_id("POS")
                pos = VesselPosition(
                    position_id=pos_id,
                    vessel_id=candidate.vessel_id,
                    timestamp=datetime.fromisoformat(pt["timestamp"].replace("Z", "+00:00")),
                    latitude=pt["lat"],
                    longitude=pt["lon"],
                    speed=None,
                    course=None,
                    geometry=f"SRID=4326;POINT({pt['lon']} {pt['lat']})",
                )
                self.db.add(pos)

        self.db.commit()
        return result.candidates

    async def _run_attribution(
        self,
        spill_id: str,
        origin_lon: float,
        origin_lat: float,
        origin_time: str,
        candidates: list,
    ) -> list:
        vessel_ids = [c.vessel_id for c in candidates]
        if not vessel_ids:
            return []

        result = await self.attribution_client.score_vessels(
            spill_id=spill_id,
            origin_lon=origin_lon,
            origin_lat=origin_lat,
            origin_time=origin_time,
            candidate_vessel_ids=vessel_ids,
        )

        self.suspect_repo.delete_by_spill_id(spill_id)
        scored = []
        for attr in result.attributions:
            scored.append(
                self.suspect_repo.create(
                    score_id=generate_id("SCR"),
                    spill_id=spill_id,
                    vessel_id=attr.vessel_id,
                    score=attr.score,
                    spatial_score=attr.spatial_score,
                    temporal_score=attr.temporal_score,
                    route_score=attr.route_score,
                    evidence_json=attr.evidence,
                )
            )
        self.db.commit()
        return scored

    async def _run_forecast(
        self,
        spill_id: str,
        spill_lon: float,
        spill_lat: float,
        spill_area: float,
    ):
        result = await self.forecast_client.forecast(
            spill_lon=spill_lon,
            spill_lat=spill_lat,
            spill_area_sq_km=spill_area,
        )

        self.forecast_repo.delete_by_spill_id(spill_id)
        for entry in result.entries:
            self.forecast_repo.create(
                prediction_id=generate_id("FCT"),
                spill_id=spill_id,
                forecast_hour=float(entry.hours),
                latitude=entry.center_lat,
                longitude=entry.center_lon,
                geometry_wkt=entry.geometry_wkt,
                uncertainty=entry.uncertainty,
                area_sq_km=entry.area_sq_km,
            )
        self.db.commit()

    async def _run_impact(
        self,
        spill_id: str,
        spill_lon: float,
        spill_lat: float,
        spill_area: float,
        spill_geom_wkt: str,
    ):
        result = await self.impact_client.assess_impact(
            spill_lon=spill_lon,
            spill_lat=spill_lat,
            spill_area_sq_km=spill_area,
            spill_geometry_wkt=spill_geom_wkt,
        )

        self.impact_repo.delete_by_spill_id(spill_id)
        for zone in result.zones:
            self.impact_repo.create(
                impact_id=generate_id("IMP"),
                spill_id=spill_id,
                zone_type=zone.zone_type,
                risk_level=zone.risk_level,
                geometry_wkt=zone.geometry_wkt,
                affected_area_sq_km=zone.affected_area_sq_km,
            )
        self.db.commit()
