import pandas as pd


def calculate_time_difference_minutes(
    vessel_timestamp,
    spill_timestamp
):
    """
    Calculate the absolute time difference between
    an AIS vessel position and the estimated spill time.

    Returns:
        Time difference in minutes.
    """

    vessel_timestamp = pd.to_datetime(
        vessel_timestamp,
        utc=True
    )

    spill_timestamp = pd.to_datetime(
        spill_timestamp,
        utc=True
    )

    time_difference = abs(
        (vessel_timestamp - spill_timestamp)
        .total_seconds()
        / 60
    )

    return time_difference


if __name__ == "__main__":

    vessel_timestamp = "2026-08-28T23:30:00Z"

    spill_timestamp = "2026-08-28T23:40:00Z"

    time_difference_min = (
        calculate_time_difference_minutes(
            vessel_timestamp,
            spill_timestamp
        )
    )

    print(
        f"Time difference: "
        f"{time_difference_min:.1f} minutes"
    )
