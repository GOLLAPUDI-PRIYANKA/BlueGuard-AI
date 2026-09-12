import pandas as pd


def clean_ais_data(ais_data):
    """
    Clean AIS data before building vessel trajectories.

    Operations:
    - Remove duplicate AIS records
    - Remove invalid coordinates
    - Normalize timestamps
    - Sort records by vessel and timestamp
    """

    ais_data = ais_data.copy()

    # ---------------------------------------------------------
    # 1. NORMALIZE TIMESTAMP
    # ---------------------------------------------------------

    ais_data["timestamp"] = pd.to_datetime(
        ais_data["timestamp"],
        utc=True,
        errors="coerce"
    )

    # Remove records with invalid timestamps
    ais_data = ais_data.dropna(
        subset=["timestamp"]
    )

    # ---------------------------------------------------------
    # 2. REMOVE DUPLICATE AIS RECORDS
    # ---------------------------------------------------------

    duplicate_columns = [
        "mmsi",
        "latitude",
        "longitude",
        "timestamp"
    ]

    existing_columns = [
        column
        for column in duplicate_columns
        if column in ais_data.columns
    ]

    ais_data = ais_data.drop_duplicates(
        subset=existing_columns
    )

    # ---------------------------------------------------------
    # 3. REMOVE INVALID COORDINATES
    # ---------------------------------------------------------

    ais_data = ais_data[
        ais_data["latitude"].between(-90, 90)
        &
        ais_data["longitude"].between(-180, 180)
    ]

    # ---------------------------------------------------------
    # 4. SORT AIS RECORDS
    # ---------------------------------------------------------

    ais_data = (
        ais_data
        .sort_values(
            by=["mmsi", "timestamp"]
        )
        .reset_index(drop=True)
    )

    return ais_data


def build_trajectories(ais_data):
    """
    Build vessel trajectories from cleaned AIS data.

    Each vessel's trajectory contains:
    - Position
    - Timestamp
    - Speed
    - Course
    - Time gap from previous AIS record
    """

    # ---------------------------------------------------------
    # CLEAN AIS DATA
    # ---------------------------------------------------------

    ais_data = clean_ais_data(ais_data)

    trajectories = {}

    # ---------------------------------------------------------
    # BUILD TRAJECTORY FOR EACH VESSEL
    # ---------------------------------------------------------

    for mmsi, vessel_data in ais_data.groupby("mmsi"):

        vessel_data = (
            vessel_data
            .sort_values("timestamp")
            .reset_index(drop=True)
            .copy()
        )

        # -----------------------------------------------------
        # CALCULATE TIME GAP BETWEEN AIS POSITIONS
        # -----------------------------------------------------

        vessel_data["timeGapMinutes"] = (
            vessel_data["timestamp"]
            .diff()
            .dt.total_seconds()
            .div(60)
        )

        # First position has no previous position
        vessel_data["timeGapMinutes"] = (
            vessel_data["timeGapMinutes"]
            .fillna(0)
        )

        # -----------------------------------------------------
        # SELECT TRAJECTORY COLUMNS
        # -----------------------------------------------------

        trajectory_columns = [
            "mmsi",
            "imo_number",
            "latitude",
            "longitude",
            "timestamp",
            "speed",
            "course",
            "vessel_type",
            "timeGapMinutes"
        ]

        # Keep only columns that exist
        trajectory_columns = [
            column
            for column in trajectory_columns
            if column in vessel_data.columns
        ]

        trajectory = vessel_data[
            trajectory_columns
        ].copy()

        trajectories[mmsi] = trajectory

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    print("Vessel trajectories created successfully.")
    print(f"Total vessels: {len(trajectories)}")

    return trajectories


# =============================================================
# TEST TRAJECTORY MODULE
# =============================================================

if __name__ == "__main__":

    file_path = "ais-services/data/ais_sample.csv"

    # Load AIS data
    ais_data = pd.read_csv(file_path)

    # Build trajectories
    trajectories = build_trajectories(ais_data)

    # Display each vessel trajectory
    for mmsi, trajectory in trajectories.items():

        print("\n------------------------------------------")
        print(f"MMSI: {mmsi}")
        print(
            f"Number of positions: "
            f"{len(trajectory)}"
        )

        print("\nTrajectory:")

        display_columns = [
            "latitude",
            "longitude",
            "timestamp",
            "speed",
            "course",
            "timeGapMinutes"
        ]

        display_columns = [
            column
            for column in display_columns
            if column in trajectory.columns
        ]

        print(
            trajectory[display_columns]
            .to_string(index=False)
        )
