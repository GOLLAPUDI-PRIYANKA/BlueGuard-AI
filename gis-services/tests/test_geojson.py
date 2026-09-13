from spatial.geojson_builder import GeoJSONBuilder


def test_origin_geojson_is_valid():
    builder = GeoJSONBuilder()
    feature = builder.create_origin_feature(15.201, 73.512, 12.0)

    assert feature["type"] == "Feature"
    assert feature["geometry"]["type"] == "Polygon"
    ring = feature["geometry"]["coordinates"][0]
    assert ring[0] == ring[-1]
    assert len(ring) > 4


def test_forecast_geojson_coordinates_are_lon_lat():
    builder = GeoJSONBuilder()
    feature = builder.create_point_feature(
        15.201,
        73.512,
        {"type": "test"},
    )

    assert feature["geometry"]["coordinates"] == [73.512, 15.201]
