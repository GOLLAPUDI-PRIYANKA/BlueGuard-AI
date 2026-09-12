import os
os.environ["DATABASE_URL"] = "postgresql://marineguard:marineguard@localhost:5432/marineguard_test"
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base
from app.models import (  # noqa: F401
    spill,
    spill_detection,
    vessel,
    vessel_position,
    spill_origin,
    suspect_score,
    drift_prediction,
    environment_data,
    impact_zone,
)


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def db_session():
    from app.core.database import SessionLocal, engine
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()