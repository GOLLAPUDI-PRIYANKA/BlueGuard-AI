import pandas as pd


def calculate_ais_continuity(
    vessel_trajectory,
    expected_interval_minutes=10,
    tolerance_minutes=2
):
    """
    Calculate AIS continuity for a vessel trajectory.

    The score measures how consistently a vessel's AIS
    positions follow the expected reporting interval.

    Parameters:
        vessel_trajectory:
            DataFrame containing the vessel trajectory.

        expected_interval_minutes:
            Expected AIS reporting interval.

        tolerance_minutes:
            Allowed deviation from the expected interval.

    Returns:
        Float between 0 and 1.
    """

    # ---------------------------------------------------------
    # CHECK FOR INSUFFICIENT DATA
    # ---------------------------------------------------------

    if len(vessel_trajectory) < 2:
        return 1.0

    # ---------------------------------------------------------
    # PREPARE TRAJECTORY
    # ---------------------------------------------------------

    vessel_trajectory = (
        vessel_trajectory
        .sort_values("timestamp")
        .reset_index(drop=True)
        .copy()
    )

    vessel_trajectory["timestamp"] = pd.to_datetime(
        vessel_trajectory["timestamp"],
        utc=True
    )

    # ---------------------------------------------------------
    # USE EXISTING TIME GAPS WHEN AVAILABLE
    # ---------------------------------------------------------

    if "timeGapMinutes" in vessel_trajectory.columns:

        time_gaps = (
            vessel_trajectory["timeGapMinutes"]
            .iloc[1:]
            .astype(float)
            .tolist()
        )

    else:

        # Calculate time gaps if the trajectory does not
        # already contain them.

        time_gaps = []

        for i in range(1, len(vessel_trajectory)):

            previous_timestamp = (
                vessel_trajectory.loc[
                    i - 1,
                    "timestamp"
                ]
            )

            current_timestamp = (
                vessel_trajectory.loc[
                    i,
                    "timestamp"
                ]
            )

            time_difference_minutes = (
                current_timestamp
                - previous_timestamp
            ).total_seconds() / 60

            time_gaps.append(
                time_difference_minutes
            )

    # ---------------------------------------------------------
    # CALCULATE CONTINUITY
    # ---------------------------------------------------------

    total_expected_intervals = 0
    observed_intervals = 0

    for time_difference_minutes in time_gaps:

        # Ignore invalid or negative time gaps
        if time_difference_minutes <= 0:
            continue

        # Determine how many expected intervals
        # are represented by this time gap.
        expected_intervals = round(
            time_difference_minutes
            / expected_interval_minutes
        )

        expected_intervals = max(
            expected_intervals,
            1
        )

        total_expected_intervals += expected_intervals

        expected_time = (
            expected_intervals
            * expected_interval_minutes
        )

        # Check whether the actual gap is close enough
        # to the expected reporting interval.
        if abs(
            time_difference_minutes
            - expected_time
        ) <= tolerance_minutes:

            observed_intervals += expected_intervals

    # ---------------------------------------------------------
    # AVOID DIVISION BY ZERO
    # ---------------------------------------------------------

    if total_expected_intervals == 0:
        return 1.0

    # ---------------------------------------------------------
    # FINAL CONTINUITY SCORE
    # ---------------------------------------------------------

    continuity = (
        observed_intervals
        / total_expected_intervals
    )

    return round(
        max(
            0.0,
            min(1.0, continuity)
        ),
        3
    )


# =============================================================
# TEST THE AIS CONTINUITY MODULE
# =============================================================

if __name__ == "__main__":

    file_path = "ais-services/data/ais_sample.csv"

    # Load AIS data
    ais_data = pd.read_csv(file_path)

    # Normalize timestamp
    ais_data["timestamp"] = pd.to_datetime(
        ais_data["timestamp"],
        utc=True
    )

    # Test every vessel
    for mmsi, vessel_trajectory in ais_data.groupby("mmsi"):

        continuity = calculate_ais_continuity(
            vessel_trajectory,
            expected_interval_minutes=10
        )

        print(
            f"MMSI {mmsi} "
            f"→ AIS continuity: {continuity:.3f}"
        )
