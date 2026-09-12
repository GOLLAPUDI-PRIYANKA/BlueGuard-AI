import math
import pandas as pd


def calculate_distance_km(
    latitude1,
    longitude1,
    latitude2,
    longitude2
):
    """
    Calculate distance between two geographic coordinates
    using the Haversine formula.

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

    return earth_radius_km * c


def calculate_route_consistency(
    vessel_trajectory,
    spill_origin_latitude,
    spill_origin_longitude
):
    """
    Calculate route consistency for a vessel.

    Route consistency is the proportion of consecutive
    AIS movements where the vessel moves closer to the
    estimated spill origin.

    Returns:
        Value between 0 and 1.
    """

    if len(vessel_trajectory) < 2:
        return 0.0

    vessel_trajectory = (
        vessel_trajectory
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    distances_to_origin = []

    for _, ais_record in vessel_trajectory.iterrows():

        distance_km = calculate_distance_km(
            ais_record["latitude"],
            ais_record["longitude"],
            spill_origin_latitude,
            spill_origin_longitude
        )

        distances_to_origin.append(distance_km)

    approaching_movements = 0
    total_movements = len(distances_to_origin) - 1

    for i in range(1, len(distances_to_origin)):

        previous_distance = distances_to_origin[i - 1]
        current_distance = distances_to_origin[i]

        if current_distance < previous_distance:
            approaching_movements += 1

    route_consistency = (
        approaching_movements / total_movements
    )

    return round(route_consistency, 3)


if __name__ == "__main__":

    file_path = "ais-services/data/ais_sample.csv"

    ais_data = pd.read_csv(file_path)

    ais_data["timestamp"] = pd.to_datetime(
        ais_data["timestamp"],
        utc=True
    )

    # Project example spill origin
    spill_origin_latitude = 15.201
    spill_origin_longitude = 73.512

    # Test vessel
    vessel_trajectory = ais_data[
        ais_data["mmsi"] == 123456789
    ].copy()

    route_consistency = calculate_route_consistency(
        vessel_trajectory,
        spill_origin_latitude,
        spill_origin_longitude
    )

    print(
        f"Route consistency: "
        f"{route_consistency:.3f}"
    )
