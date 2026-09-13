from backtracking.drift_model import BacktrackingModel


def test_demo_backtracking():
    model = BacktrackingModel()
    result = model.estimate_source(
        15.462,
        73.845,
        "2026-08-29T10:00:00Z",
        [],
        hours_back=10 + 20 / 60,
        scenario="arabian_sea_demo",
    )

    assert result["origin_lat"] == 15.201
    assert result["origin_lon"] == 73.512
    assert result["origin_time"] == "2026-08-28T23:40:00Z"
    assert result["confidence"] == 0.81
    assert result["uncertainty_km"] == 12.0


def test_generic_backtracking_returns_valid_coordinates():
    model = BacktrackingModel()
    result = model.estimate_source(
        15.462,
        73.845,
        "2026-08-29T10:00:00Z",
        [],
        hours_back=10,
    )

    assert -90 <= result["origin_lat"] <= 90
    assert -180 <= result["origin_lon"] <= 180
