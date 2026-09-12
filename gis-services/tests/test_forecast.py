from forecasting.drift_prediction import ForecastingModel


def test_demo_forecast():
    model = ForecastingModel()
    result = model.predict_drift(
        15.201,
        73.512,
        "2026-08-28T23:40:00Z",
        [],
        hours_forward=72,
        scenario="arabian_sea_demo",
    )

    assert len(result["forecast_points"]) == 3

    p24, p48, p72 = result["forecast_points"]
    assert (p24["lat"], p24["lon"]) == (15.58, 74.12)
    assert (p48["lat"], p48["lon"]) == (15.89, 74.45)
    assert (p72["lat"], p72["lon"]) == (16.12, 74.78)


def test_generic_forecast_returns_three_points():
    model = ForecastingModel()
    result = model.predict_drift(
        15.201,
        73.512,
        "2026-08-28T23:40:00Z",
        [],
        hours_forward=72,
    )

    assert len(result["forecast_points"]) == 3
