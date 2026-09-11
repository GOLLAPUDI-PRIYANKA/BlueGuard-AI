import pandas as pd

from features.distance import calculate_distance_km
from features.temporal import calculate_time_difference_minutes
from features.heading import calculate_vessel_heading_consistency
from features.route import calculate_route_consistency
from features.continuity import calculate_ais_continuity

from trajectory.trajectory import build_trajectories

from attribution.attribution_engine import (
    calculate_spatial_proximity,
    calculate_temporal_proximity,
    calculate_evidence_score,
    calculate_evidence_percentage,
    get_investigation_priority
)


def generate_candidate_vessels(
    ais_data,
    spill_origin_latitude,
    spill_origin_longitude,
    spill_timestamp,
    spatial_radius_km,
    temporal_window_minutes
):
    """
    Generate and rank candidate vessels based on
    AIS evidence around an estimated oil spill origin.

    Evidence considered:
    - Spatial proximity
    - Temporal proximity
    - Heading consistency
    - Route consistency
    - AIS continuity

    Returns:
        DataFrame containing candidate vessels and
        explainable evidence scores.
    """

    # ---------------------------------------------------------
    # STEP 1: COPY AND NORMALIZE AIS DATA
    # ---------------------------------------------------------

    ais_data = ais_data.copy()

    ais_data["timestamp"] = pd.to_datetime(
        ais_data["timestamp"],
        utc=True
    )

    # Normalize spill timestamp
    spill_timestamp = pd.to_datetime(
        spill_timestamp,
        utc=True
    )

    # ---------------------------------------------------------
    # STEP 2: BUILD VESSEL TRAJECTORIES
    # ---------------------------------------------------------

    trajectories = build_trajectories(
        ais_data
    )

    # ---------------------------------------------------------
    # STEP 3: FIND SPATIAL-TEMPORAL CANDIDATES
    # ---------------------------------------------------------

    candidate_positions = []

    for _, ais_record in ais_data.iterrows():

        distance_km = calculate_distance_km(
            ais_record["latitude"],
            ais_record["longitude"],
            spill_origin_latitude,
            spill_origin_longitude
        )

        time_difference_min = (
            calculate_time_difference_minutes(
                ais_record["timestamp"],
                spill_timestamp
            )
        )

        if (
            distance_km <= spatial_radius_km
            and
            time_difference_min <= temporal_window_minutes
        ):

            candidate_positions.append({
                "mmsi": ais_record["mmsi"],
                "imo_number": ais_record["imo_number"],
                "vessel_type": ais_record["vessel_type"],
                "latitude": ais_record["latitude"],
                "longitude": ais_record["longitude"],
                "timestamp": ais_record["timestamp"],
                "course": ais_record["course"],
                "distanceKm": distance_km,
                "timeDifferenceMin": time_difference_min
            })

    # ---------------------------------------------------------
    # STEP 4: NO CANDIDATES
    # ---------------------------------------------------------

    if not candidate_positions:
        return pd.DataFrame()

    candidate_positions = pd.DataFrame(
        candidate_positions
    )

    candidate_vessels = []

    # ---------------------------------------------------------
    # STEP 5: PROCESS EACH VESSEL
    # ---------------------------------------------------------

    for mmsi, vessel_positions in (
        candidate_positions.groupby("mmsi")
    ):

        vessel_positions = (
            vessel_positions
            .sort_values("timestamp")
            .reset_index(drop=True)
        )

        # -----------------------------------------------------
        # CLOSEST POSITION TO SPILL ORIGIN
        # -----------------------------------------------------

        closest_position = (
            vessel_positions
            .sort_values(
                by=[
                    "distanceKm",
                    "timeDifferenceMin"
                ]
            )
            .iloc[0]
        )

        # -----------------------------------------------------
        # SPATIAL PROXIMITY
        # -----------------------------------------------------

        spatial_proximity = (
            calculate_spatial_proximity(
                closest_position["distanceKm"],
                spatial_radius_km
            )
        )

        # -----------------------------------------------------
        # TEMPORAL PROXIMITY
        # -----------------------------------------------------

        temporal_proximity = (
            calculate_temporal_proximity(
                closest_position["timeDifferenceMin"],
                temporal_window_minutes
            )
        )

        # -----------------------------------------------------
        # HEADING CONSISTENCY
        # -----------------------------------------------------

        heading_consistency = (
            calculate_vessel_heading_consistency(
                closest_position["latitude"],
                closest_position["longitude"],
                closest_position["course"],
                spill_origin_latitude,
                spill_origin_longitude
            )
        )

        # -----------------------------------------------------
        # COMPLETE VESSEL TRAJECTORY
        # -----------------------------------------------------

        full_vessel_trajectory = trajectories[mmsi]

        # -----------------------------------------------------
        # ROUTE CONSISTENCY
        # -----------------------------------------------------

        route_consistency = (
            calculate_route_consistency(
                full_vessel_trajectory,
                spill_origin_latitude,
                spill_origin_longitude
            )
        )

        # -----------------------------------------------------
        # AIS CONTINUITY
        # -----------------------------------------------------

        ais_continuity = (
            calculate_ais_continuity(
                full_vessel_trajectory,
                expected_interval_minutes=10
            )
        )

        # -----------------------------------------------------
        # FINAL EVIDENCE SCORE
        # -----------------------------------------------------

        evidence_score = calculate_evidence_score(
            spatial_proximity,
            temporal_proximity,
            heading_consistency,
            route_consistency,
            ais_continuity
        )

        evidence_percentage = (
            calculate_evidence_percentage(
                evidence_score
            )
        )

        investigation_priority = (
            get_investigation_priority(
                evidence_score
            )
        )

        # -----------------------------------------------------
        # STORE CANDIDATE
        # -----------------------------------------------------

        candidate_vessels.append({

            "mmsi": mmsi,

            "imo_number": (
                closest_position["imo_number"]
            ),

            "vessel_type": (
                closest_position["vessel_type"]
            ),

            "latitude": (
                closest_position["latitude"]
            ),

            "longitude": (
                closest_position["longitude"]
            ),

            "timestamp": (
                closest_position["timestamp"]
            ),

            # Raw evidence
            "distanceKm": round(
                closest_position["distanceKm"],
                3
            ),

            "timeDifferenceMin": round(
                closest_position["timeDifferenceMin"],
                1
            ),

            "headingConsistency": (
                heading_consistency
            ),

            "routeConsistency": (
                route_consistency
            ),

            "aisContinuity": (
                ais_continuity
            ),

            # Normalized evidence
            "spatialProximity": (
                spatial_proximity
            ),

            "temporalProximity": (
                temporal_proximity
            ),

            # Final score
            "evidenceScore": (
                evidence_score
            ),

            "evidencePercentage": (
                evidence_percentage
            ),

            "investigationPriority": (
                investigation_priority
            )
        })

    # ---------------------------------------------------------
    # STEP 6: CREATE DATAFRAME
    # ---------------------------------------------------------

    candidate_vessels = pd.DataFrame(
        candidate_vessels
    )

    # ---------------------------------------------------------
    # STEP 7: SORT BY EVIDENCE SCORE
    # ---------------------------------------------------------

    candidate_vessels = (
        candidate_vessels
        .sort_values(
            by="evidenceScore",
            ascending=False
        )
        .reset_index(drop=True)
    )

    # ---------------------------------------------------------
    # STEP 8: ADD FINAL RANK
    # ---------------------------------------------------------

    candidate_vessels.insert(
        0,
        "candidateRank",
        range(
            1,
            len(candidate_vessels) + 1
        )
    )

    return candidate_vessels


# =============================================================
# TEST CANDIDATE PIPELINE
# =============================================================

if __name__ == "__main__":

    file_path = "ais-services/data/ais_sample.csv"

    # Load AIS data
    ais_data = pd.read_csv(
        file_path
    )

    # Example spill origin
    spill_origin_latitude = 15.201
    spill_origin_longitude = 73.512

    # Example spill timestamp
    spill_timestamp = (
        "2026-08-28T23:40:00Z"
    )

    # Search radius
    spatial_radius_km = 10

    # Search time window
    temporal_window_minutes = 60

    # Generate candidates
    candidate_vessels = (
        generate_candidate_vessels(
            ais_data,
            spill_origin_latitude,
            spill_origin_longitude,
            spill_timestamp,
            spatial_radius_km,
            temporal_window_minutes
        )
    )

    print("\n==========================================")
    print("MARINEGUARD AIS CANDIDATE ANALYSIS")
    print("==========================================")

    if candidate_vessels.empty:

        print("\nNo candidate vessels found.")

    else:

        print(
            f"\nTotal candidate vessels: "
            f"{len(candidate_vessels)}"
        )

        print("\nCandidate analysis:")

        display_columns = [
            "candidateRank",
            "mmsi",
            "imo_number",
            "vessel_type",
            "distanceKm",
            "timeDifferenceMin",
            "headingConsistency",
            "routeConsistency",
            "aisContinuity",
            "spatialProximity",
            "temporalProximity",
            "evidenceScore",
            "evidencePercentage",
            "investigationPriority"
        ]

        print(
            candidate_vessels[
                display_columns
            ].to_string(index=False)
        )

    print("\n==========================================")
