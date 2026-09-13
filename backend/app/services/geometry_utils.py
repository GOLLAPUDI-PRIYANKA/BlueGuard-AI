from geoalchemy2.shape import to_shape
from shapely.wkt import loads as load_wkt
from app.core.exceptions import InvalidGeometryError


def shape_to_geojson(geometry) -> dict:
    """Convert a GeoAlchemy2 geometry column value to a GeoJSON dict."""
    try:
        shapely_geom = to_shape(geometry)
    except Exception as exc:
        raise InvalidGeometryError(f"Could not convert geometry: {exc}")
    if not shapely_geom.is_valid:
        raise InvalidGeometryError("Stored geometry is not valid")
    return shapely_geom.__geo_interface__


def wkt_to_geojson(geometry_wkt: str) -> dict:
    """Convert a WKT geometry string to a GeoJSON dict."""
    try:
        geom = load_wkt(geometry_wkt)
    except Exception as exc:
        raise InvalidGeometryError(f"Could not parse WKT: {exc}")
    if not geom.is_valid:
        raise InvalidGeometryError("WKT geometry is not valid")
    return geom.__geo_interface__


def validate_coordinates(lat: float, lon: float):
    if not (-90 <= lat <= 90):
        raise InvalidGeometryError(f"Latitude out of range: {lat}")
    if not (-180 <= lon <= 180):
        raise InvalidGeometryError(f"Longitude out of range: {lon}")