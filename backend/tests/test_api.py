import os
import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_detect_spill_success(client):
    payload = {
        "imageUrl": "sentinel_scene_001.tif",
        "source": "SENTINEL_1",
        "captureTime": "2026-08-29T08:30:00Z",
    }
    resp = client.post("/api/v1/spills/detect", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["spillId"].startswith("SP")
    assert body["data"]["detected"] in (True, False)
    assert 0 <= body["data"]["confidence"] <= 1


def test_detect_spill_invalid_confidence(client):
    payload = {
        "imageUrl": "",
        "source": "",
        "captureTime": "not-a-date",
    }
    resp = client.post("/api/v1/spills/detect", json=payload)
    assert resp.status_code == 422


def test_get_nonexistent_spill(client):
    resp = client.get("/api/v1/spills/SP_NONEXISTENT")
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["errorCode"] == "SPILL_NOT_FOUND"


def test_get_nonexistent_vessel_trajectory(client):
    resp = client.get("/api/v1/vessels/VES_NONEXISTENT/trajectory")
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["errorCode"] == "VESSEL_NOT_FOUND"