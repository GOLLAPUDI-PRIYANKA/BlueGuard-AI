def calculate_spatial_proximity(
    distance_km,
    spatial_radius_km
):
    """
    Convert distance from the spill origin into
    a normalized spatial proximity score.

    Returns:
        Value between 0 and 1.
    """

    if distance_km >= spatial_radius_km:
        return 0.0

    spatial_proximity = (
        1 - (distance_km / spatial_radius_km)
    )

    return round(
        max(
            0.0,
            min(1.0, spatial_proximity)
        ),
        3
    )


def calculate_temporal_proximity(
    time_difference_min,
    temporal_window_minutes
):
    """
    Convert time difference from the estimated spill
    time into a normalized temporal proximity score.

    Returns:
        Value between 0 and 1.
    """

    if time_difference_min >= temporal_window_minutes:
        return 0.0

    temporal_proximity = (
        1 - (
            time_difference_min
            / temporal_window_minutes
        )
    )

    return round(
        max(
            0.0,
            min(1.0, temporal_proximity)
        ),
        3
    )


def calculate_trajectory_consistency(
    heading_consistency,
    route_consistency
):
    """
    Combine heading consistency and route consistency
    into a single trajectory consistency score.

    Both input values must be between 0 and 1.

    Returns:
        Trajectory consistency between 0 and 1.
    """

    trajectory_consistency = (
        0.5 * heading_consistency
        + 0.5 * route_consistency
    )

    return round(
        max(
            0.0,
            min(1.0, trajectory_consistency)
        ),
        3
    )


def calculate_evidence_score(
    spatial_proximity,
    temporal_proximity,
    heading_consistency,
    route_consistency,
    ais_continuity
):
    """
    Calculate an explainable vessel evidence score.

    Weights:

    Spatial proximity      = 30%
    Temporal proximity     = 20%
    Heading consistency    = 20%
    Route consistency      = 20%
    AIS continuity         = 10%

    Returns:
        Evidence score between 0 and 1.
    """

    # ---------------------------------------------------------
    # WEIGHTS
    # ---------------------------------------------------------

    spatial_weight = 0.30
    temporal_weight = 0.20
    heading_weight = 0.20
    route_weight = 0.20
    continuity_weight = 0.10

    # ---------------------------------------------------------
    # WEIGHTED SCORE
    # ---------------------------------------------------------

    evidence_score = (
        spatial_weight * spatial_proximity
        + temporal_weight * temporal_proximity
        + heading_weight * heading_consistency
        + route_weight * route_consistency
        + continuity_weight * ais_continuity
    )

    return round(
        max(
            0.0,
            min(1.0, evidence_score)
        ),
        3
    )


def calculate_evidence_percentage(
    evidence_score
):
    """
    Convert the normalized evidence score into
    a percentage for easier presentation.
    """

    return round(
        evidence_score * 100,
        1
    )


def get_investigation_priority(
    evidence_score
):
    """
    Convert the evidence score into an investigation
    priority label.

    This is NOT a statement of guilt.

    It only indicates how strongly the available
    evidence supports further investigation.
    """

    if evidence_score >= 0.80:
        return "High"

    if evidence_score >= 0.60:
        return "Medium"

    return "Low"


# =============================================================
# TEST THE ATTRIBUTION ENGINE
# =============================================================

if __name__ == "__main__":

    spatial_radius_km = 10
    temporal_window_minutes = 60

    # ---------------------------------------------------------
    # CANDIDATE 1
    # ---------------------------------------------------------

    distance_km = 0.077
    time_difference_min = 0

    heading_consistency = 0.989
    route_consistency = 0.8
    ais_continuity = 1.0

    spatial_score = calculate_spatial_proximity(
        distance_km,
        spatial_radius_km
    )

    temporal_score = calculate_temporal_proximity(
        time_difference_min,
        temporal_window_minutes
    )

    evidence_score = calculate_evidence_score(
        spatial_score,
        temporal_score,
        heading_consistency,
        route_consistency,
        ais_continuity
    )

    evidence_percentage = calculate_evidence_percentage(
        evidence_score
    )

    priority = get_investigation_priority(
        evidence_score
    )

    print("\n==========================================")
    print("MARINEGUARD ATTRIBUTION ENGINE")
    print("==========================================")

    print("\nCandidate 1:")

    print(
        f"Spatial proximity:     {spatial_score:.3f}"
    )

    print(
        f"Temporal proximity:    {temporal_score:.3f}"
    )

    print(
        f"Heading consistency:   {heading_consistency:.3f}"
    )

    print(
        f"Route consistency:     {route_consistency:.3f}"
    )

    print(
        f"AIS continuity:        {ais_continuity:.3f}"
    )

    print(
        f"\nEvidence score:        {evidence_score:.3f}"
    )

    print(
        f"Evidence percentage:   {evidence_percentage:.1f}%"
    )

    print(
        f"Investigation priority: {priority}"
    )

    # ---------------------------------------------------------
    # CANDIDATE 2
    # ---------------------------------------------------------

    distance_km = 9.806
    time_difference_min = 10

    heading_consistency = 0.709
    route_consistency = 1.0
    ais_continuity = 1.0

    spatial_score = calculate_spatial_proximity(
        distance_km,
        spatial_radius_km
    )

    temporal_score = calculate_temporal_proximity(
        time_difference_min,
        temporal_window_minutes
    )

    evidence_score = calculate_evidence_score(
        spatial_score,
        temporal_score,
        heading_consistency,
        route_consistency,
        ais_continuity
    )

    evidence_percentage = calculate_evidence_percentage(
        evidence_score
    )

    priority = get_investigation_priority(
        evidence_score
    )

    print("\n------------------------------------------")
    print("Candidate 2:")

    print(
        f"Spatial proximity:     {spatial_score:.3f}"
    )

    print(
        f"Temporal proximity:    {temporal_score:.3f}"
    )

    print(
        f"Heading consistency:   {heading_consistency:.3f}"
    )

    print(
        f"Route consistency:     {route_consistency:.3f}"
    )

    print(
        f"AIS continuity:        {ais_continuity:.3f}"
    )

    print(
        f"\nEvidence score:        {evidence_score:.3f}"
    )

    print(
        f"Evidence percentage:   {evidence_percentage:.1f}%"
    )

    print(
        f"Investigation priority: {priority}"
    )

    print("\n==========================================")
