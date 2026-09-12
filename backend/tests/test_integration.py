import pytest


def test_full_pipeline_end_to_end(client):
    payload = {
        "imageUrl": "sentinel_scene_demo.tif",
        "source": "SENTINEL_1",
        "captureTime": "2026-08-29T08:30:00Z",
    }

    detect_resp = client.post("/api/v1/spills/detect", json=payload)
    assert detect_resp.status_code == 200
    detect_body = detect_resp.json()
    assert detect_body["success"] is True
    spill_id = detect_body["data"]["spillId"]

    spill_resp = client.get(f"/api/v1/spills/{spill_id}")
    assert spill_resp.status_code == 200
    spill_body = spill_resp.json()
    assert spill_body["data"]["spillId"] == spill_id

    analyze_resp = client.post(
        f"/api/v1/spills/{spill_id}/analyze",
        json={"includeForecast": True, "includeImpact": True, "aisHoursBefore": 12, "aisHoursAfter": 12},
    )
    assert analyze_resp.status_code == 200
    analyze_body = analyze_resp.json()
    assert analyze_body["success"] is True

    origin_resp = client.get(f"/api/v1/spills/{spill_id}/origin")
    assert origin_resp.status_code == 200

    suspects_resp = client.get(f"/api/v1/spills/{spill_id}/suspects")
    assert suspects_resp.status_code == 200
    suspects_body = suspects_resp.json()
    assert suspects_body["data"]["spillId"] == spill_id

    forecast_resp = client.get(f"/api/v1/spills/{spill_id}/forecast")
    assert forecast_resp.status_code == 200
    forecast_body = forecast_resp.json()
    assert len(forecast_body["data"]["forecast"]) == 3

    impact_resp = client.get(f"/api/v1/spills/{spill_id}/impact")
    assert impact_resp.status_code == 200
    impact_body = impact_resp.json()
    assert "marineRisk" in impact_body["data"]

    nearby_resp = client.get(f"/api/v1/spills/{spill_id}/nearby-vessels")
    assert nearby_resp.status_code == 200

    report_resp = client.get(f"/api/v1/spills/{spill_id}/report")
    assert report_resp.status_code == 200
    report_body = report_resp.json()
    assert report_body["data"]["reportStatus"] == "READY"

    dashboard_resp = client.get("/api/v1/dashboard/summary")
    assert dashboard_resp.status_code == 200
    dashboard_body = dashboard_resp.json()
    assert dashboard_body["data"]["totalSpills"] >= 1