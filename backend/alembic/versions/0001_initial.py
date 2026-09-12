"""Initial schema: PostGIS, spills, detections, vessels, origins, suspects, forecasts, environment, impacts

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "spills",
        sa.Column("spill_id", sa.String(length=20), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("area_sq_km", sa.Float(), nullable=False),
        sa.Column("severity", sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="spillseverity"), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("centroid", Geometry(geometry_type="POINT", srid=4326), nullable=False),
        sa.Column("geometry", Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False),
        sa.Column("status", sa.Enum("DETECTED", "UNDER_INVESTIGATION", "ANALYSIS_COMPLETE", "CLOSED", name="spillstatus"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("spill_id"),
    )
    op.execute("CREATE INDEX idx_spill_centroid ON spills USING gist (centroid)")
    op.execute("CREATE INDEX idx_spill_geometry ON spills USING gist (geometry)")
    op.create_index("idx_spill_status", "spills", ["status"], unique=False)
    op.create_index("idx_spill_detected_at", "spills", ["detected_at"], unique=False)

    op.create_table(
        "spill_detections",
        sa.Column("detection_id", sa.String(length=20), nullable=False),
        sa.Column("spill_id", sa.String(length=20), nullable=False),
        sa.Column("image_source", sa.String(length=50), nullable=False),
        sa.Column("image_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("mask_uri", sa.String(length=500), nullable=True),
        sa.Column("prediction_confidence", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["spill_id"], ["spills.spill_id"]),
        sa.PrimaryKeyConstraint("detection_id"),
    )
    op.create_index("idx_detection_spill_id", "spill_detections", ["spill_id"], unique=False)
    op.create_index("idx_detection_image_timestamp", "spill_detections", ["image_timestamp"], unique=False)

    op.create_table(
        "vessels",
        sa.Column("vessel_id", sa.String(length=20), nullable=False),
        sa.Column("mmsi", sa.String(length=20), nullable=True),
        sa.Column("imo_number", sa.String(length=20), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("vessel_type", sa.String(length=50), nullable=True),
        sa.Column("flag_country", sa.String(length=10), nullable=True),
        sa.PrimaryKeyConstraint("vessel_id"),
    )
    op.create_index("idx_vessel_mmsi", "vessels", ["mmsi"], unique=False)
    op.create_index("idx_vessel_imo", "vessels", ["imo_number"], unique=False)

    op.create_table(
        "vessel_positions",
        sa.Column("position_id", sa.String(length=20), nullable=False),
        sa.Column("vessel_id", sa.String(length=20), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("speed", sa.Float(), nullable=True),
        sa.Column("course", sa.Float(), nullable=True),
        sa.Column("geometry", Geometry(geometry_type="POINT", srid=4326), nullable=False),
        sa.ForeignKeyConstraint(["vessel_id"], ["vessels.vessel_id"]),
        sa.PrimaryKeyConstraint("position_id"),
    )
    op.create_index("idx_vpos_vessel_id", "vessel_positions", ["vessel_id"], unique=False)
    op.create_index("idx_vpos_timestamp", "vessel_positions", ["timestamp"], unique=False)
    op.execute("CREATE INDEX idx_vpos_geometry ON vessel_positions USING gist (geometry)")
    op.create_index("idx_vpos_vessel_time", "vessel_positions", ["vessel_id", "timestamp"], unique=False)

    op.create_table(
        "spill_origins",
        sa.Column("origin_id", sa.String(length=20), nullable=False),
        sa.Column("spill_id", sa.String(length=20), nullable=False),
        sa.Column("estimated_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("geometry", Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("method", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["spill_id"], ["spills.spill_id"]),
        sa.PrimaryKeyConstraint("origin_id"),
        sa.UniqueConstraint("spill_id"),
    )
    op.create_index("idx_origin_spill_id", "spill_origins", ["spill_id"], unique=False)
    op.execute("CREATE INDEX idx_origin_geometry ON spill_origins USING gist (geometry)")

    op.create_table(
        "suspect_scores",
        sa.Column("score_id", sa.String(length=20), nullable=False),
        sa.Column("spill_id", sa.String(length=20), nullable=False),
        sa.Column("vessel_id", sa.String(length=20), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("spatial_score", sa.Float(), nullable=False),
        sa.Column("temporal_score", sa.Float(), nullable=False),
        sa.Column("route_score", sa.Float(), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["spill_id"], ["spills.spill_id"]),
        sa.ForeignKeyConstraint(["vessel_id"], ["vessels.vessel_id"]),
        sa.PrimaryKeyConstraint("score_id"),
    )
    op.create_index("idx_suspect_spill_id", "suspect_scores", ["spill_id"], unique=False)
    op.create_index("idx_suspect_vessel_id", "suspect_scores", ["vessel_id"], unique=False)
    op.create_index("idx_suspect_score", "suspect_scores", ["score"], unique=False)

    op.create_table(
        "drift_predictions",
        sa.Column("prediction_id", sa.String(length=20), nullable=False),
        sa.Column("spill_id", sa.String(length=20), nullable=False),
        sa.Column("forecast_hour", sa.Float(), nullable=False),
        sa.Column("area_sq_km", sa.Float(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("geometry", Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False),
        sa.Column("uncertainty", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["spill_id"], ["spills.spill_id"]),
        sa.PrimaryKeyConstraint("prediction_id"),
    )
    op.create_index("idx_forecast_spill_id", "drift_predictions", ["spill_id"], unique=False)
    op.execute("CREATE INDEX idx_forecast_geometry ON drift_predictions USING gist (geometry)")

    op.create_table(
        "environment_data",
        sa.Column("id", sa.String(length=20), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("wind_u", sa.Float(), nullable=True),
        sa.Column("wind_v", sa.Float(), nullable=True),
        sa.Column("current_u", sa.Float(), nullable=True),
        sa.Column("current_v", sa.Float(), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("geometry", Geometry(geometry_type="POINT", srid=4326), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_env_timestamp", "environment_data", ["timestamp"], unique=False)
    op.execute("CREATE INDEX idx_env_geometry ON environment_data USING gist (geometry)")

    op.create_table(
        "impact_zones",
        sa.Column("id", sa.String(length=20), nullable=False),
        sa.Column("spill_id", sa.String(length=20), nullable=False),
        sa.Column("zone_type", sa.Enum("COASTAL", "FISHING", "ENVIRONMENTAL", name="zonetype"), nullable=False),
        sa.Column("risk_level", sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="risklevel"), nullable=False),
        sa.Column("geometry", Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False),
        sa.Column("affected_area_sq_km", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["spill_id"], ["spills.spill_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_impact_spill_id", "impact_zones", ["spill_id"], unique=False)
    op.execute("CREATE INDEX idx_impact_geometry ON impact_zones USING gist (geometry)")


def downgrade() -> None:
    op.drop_index("idx_impact_geometry", table_name="impact_zones")
    op.drop_table("impact_zones")
    op.drop_index("idx_env_geometry", table_name="environment_data")
    op.drop_table("environment_data")
    op.drop_index("idx_forecast_geometry", table_name="drift_predictions")
    op.drop_table("drift_predictions")
    op.drop_index("idx_suspect_score", table_name="suspect_scores")
    op.drop_table("suspect_scores")
    op.drop_index("idx_origin_geometry", table_name="spill_origins")
    op.drop_table("spill_origins")
    op.drop_index("idx_vpos_vessel_time", table_name="vessel_positions")
    op.drop_index("idx_vpos_geometry", table_name="vessel_positions")
    op.drop_table("vessel_positions")
    op.drop_index("idx_vessel_imo", table_name="vessels")
    op.drop_table("vessels")
    op.drop_index("idx_detection_image_timestamp", table_name="spill_detections")
    op.drop_table("spill_detections")
    op.drop_index("idx_spill_detected_at", table_name="spills")
    op.drop_table("spills")

    op.execute("DROP TABLE IF EXISTS spillseverity, spillstatus, zonetype, risklevel CASCADE")