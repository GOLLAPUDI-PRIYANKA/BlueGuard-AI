import math


def calculate_distance_km(
    latitude1,
    longitude1,
    latitude2,
    longitude2
):
    """
    Calculate the distance between two geographic
    coordinates using the Haversine formula.

    Returns:
        Distance in kilometers.
    """

    earth_radius_km = 6371.0

    latitude1 = math.radians(latitude1)
    latitude2 = math.radians(latitude2)

    latitude_difference = latitude2 - latitude1
    longitude_difference = math.radians(
        longitude2 - longitude1
    )

    a = (
        math.sin(latitude_difference / 2) ** 2
        + math.cos(latitude1)
        * math.cos(latitude2)
        * math.sin(longitude_difference / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    distance_km = earth_radius_km * c

    return distance_km


if __name__ == "__main__":

    # Project example spill origin
    spill_origin_latitude = 15.201
    spill_origin_longitude = 73.512

    # Vessel position
    vessel_latitude = 15.199
    vessel_longitude = 73.511

    distance_km = calculate_distance_km(
        vessel_latitude,
        vessel_longitude,
        spill_origin_latitude,
        spill_origin_longitude
    )

    print(
        f"Distance from spill origin: "
        f"{distance_km:.3f} km"
    )
