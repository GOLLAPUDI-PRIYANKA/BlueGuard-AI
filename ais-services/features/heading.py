import math


def calculate_bearing(
    latitude1,
    longitude1,
    latitude2,
    longitude2
):
    """
    Calculate the bearing from point 1 to point 2.

    Returns:
        Bearing in degrees from 0 to 360.
    """

    latitude1 = math.radians(latitude1)
    latitude2 = math.radians(latitude2)

    longitude_difference = math.radians(
        longitude2 - longitude1
    )

    x = (
        math.sin(longitude_difference)
        * math.cos(latitude2)
    )

    y = (
        math.cos(latitude1)
        * math.sin(latitude2)
        -
        math.sin(latitude1)
        * math.cos(latitude2)
        * math.cos(longitude_difference)
    )

    bearing = math.degrees(
        math.atan2(x, y)
    )

    bearing = (bearing + 360) % 360

    return bearing


def calculate_heading_consistency(
    vessel_course,
    expected_bearing
):
    """
    Compare vessel course with the expected bearing.

    Returns:
        Heading consistency between 0 and 1.

        1.0 = same direction
        0.0 = opposite direction
    """

    difference = abs(
        vessel_course - expected_bearing
    )

    # Handle circular compass angles
    difference = min(
        difference,
        360 - difference
    )

    heading_consistency = 1 - (
        difference / 180
    )

    return round(
        max(0, min(1, heading_consistency)),
        3
    )


def calculate_vessel_heading_consistency(
    vessel_latitude,
    vessel_longitude,
    vessel_course,
    spill_origin_latitude,
    spill_origin_longitude
):
    """
    Calculate how consistent the vessel's course is
    with the direction from the vessel toward the
    estimated spill origin.
    """

    expected_bearing = calculate_bearing(
        vessel_latitude,
        vessel_longitude,
        spill_origin_latitude,
        spill_origin_longitude
    )

    heading_consistency = calculate_heading_consistency(
        vessel_course,
        expected_bearing
    )

    return heading_consistency


if __name__ == "__main__":

    # Project example spill origin
    spill_origin_latitude = 15.201
    spill_origin_longitude = 73.512

    # Example vessel position
    vessel_latitude = 15.199
    vessel_longitude = 73.511

    # Example vessel course
    vessel_course = 43.5

    expected_bearing = calculate_bearing(
        vessel_latitude,
        vessel_longitude,
        spill_origin_latitude,
        spill_origin_longitude
    )

    heading_consistency = (
        calculate_heading_consistency(
            vessel_course,
            expected_bearing
        )
    )

    print(
        f"Expected bearing: "
        f"{expected_bearing:.2f} degrees"
    )

    print(
        f"Vessel course: "
        f"{vessel_course:.2f} degrees"
    )

    print(
        f"Heading consistency: "
        f"{heading_consistency:.3f}"
    )
