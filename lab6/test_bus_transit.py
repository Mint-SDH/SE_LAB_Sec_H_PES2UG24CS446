import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles


# ----------------------------------------------------------------------
# Tests for process_commute_manifest
# ----------------------------------------------------------------------

def test_invalid_manifests_type():
    """Manifests must be a list."""
    with pytest.raises(ValueError, match="Invalid manifests list or booking fee"):
        process_commute_manifest("not_a_list", 2.0)

    with pytest.raises(ValueError, match="Invalid manifests list or booking fee"):
        process_commute_manifest(None, 2.0)


def test_invalid_booking_fee():
    """Booking fee cannot be negative."""
    with pytest.raises(ValueError, match="Invalid manifests list or booking fee"):
        process_commute_manifest([], -1.0)


def test_empty_manifests():
    """Empty list results in ZERO_RIDERSHIP."""
    result = process_commute_manifest([], 2.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_inactive_route():
    """Inactive routes or routes missing route_active should be skipped."""
    manifests = [
        {"route_active": False, "route_type": "local"},
        {"route_type": "shuttle"}  # defaults to route_active=False
    ]
    result = process_commute_manifest(manifests, 1.5)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_route_types_and_defaults():
    """Tests express, shuttle, local, and default route types with commuters."""
    manifests = [
        # Express route (base 6.0) with regular passenger (zones=1 -> 6.0 + 1.0 = 7.0)
        {
            "route_active": True,
            "route_type": "express",
            "commuters": [{"zones": 1, "type": "regular"}]
        },
        # Shuttle route (base 4.0) with regular passenger (zones=2 -> 4.0 + 2.0 = 6.0)
        {
            "route_active": True,
            "route_type": "shuttle",
            "commuters": [{"zones": 2, "type": "regular"}]
        },
        # Local route (base 2.5) with regular passenger (zones=2 -> 2.5 + 2.0 = 4.5)
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [{"zones": 2, "type": "regular"}]
        },
        # Default route_type (defaults to "local", base 2.5) and default commuter fields (zones=1, type="regular")
        {
            "route_active": True,
            "commuters": [{}]
        }
    ]
    # Total = 7.0 + 6.0 + 4.5 + 3.5 = 21.0
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 21.0, "status": "COMPLETED"}


def test_unknown_route_type():
    """An unknown route type should be rejected and skipped."""
    manifests = [
        {
            "route_active": True,
            "route_type": "monorail",
            "commuters": [{"zones": 1, "type": "regular"}]
        }
    ]
    result = process_commute_manifest(manifests, 1.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_passenger_types_and_discounts():
    """Tests student, senior, and regular passenger fare calculations."""
    # Local base = 2.5
    # student: (2.5 + (zones * 0.5)) * 0.50 => zones=3: (2.5 + 1.5) * 0.50 = 2.0
    # senior:  (2.5 + (zones * 0.5)) * 0.70 => zones=3: (2.5 + 1.5) * 0.70 = 2.8
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [
                {"zones": 3, "type": "student"},
                {"zones": 3, "type": "senior"}
            ]
        }
    ]
    # Total = 2.0 + 2.8 = 4.8
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 4.8, "status": "COMPLETED"}


def test_invalid_commuter_zones():
    """Commuters with zones <= 0 should be rejected."""
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [
                {"zones": 0, "type": "regular"},
                {"zones": -1, "type": "student"},
                {"zones": 2, "type": "regular"}  # 2.5 + 2.0 = 4.5
            ]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 4.5, "status": "COMPLETED"}


def test_blacklisted_card_on_express_route():
    """On express route, blacklisted card zeroes manifest fare and breaks commuter loop."""
    manifests = [
        {
            "route_active": True,
            "route_type": "express",
            "commuters": [
                {"zones": 2, "type": "regular"},     # would be 6 + 2 = 8
                {"zones": 1, "blacklisted": True},    # triggers manifest_fare = 0.0 and break
                {"zones": 2, "type": "regular"}      # skipped due to break
            ]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_blacklisted_card_on_non_express_route():
    """On non-express route, blacklisted card adds 0.0 and continues processing remaining commuters."""
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [
                {"zones": 1, "type": "regular"},     # 2.5 + 1 = 3.5
                {"zones": 1, "blacklisted": True},    # rejected, adds 0.0, continues
                {"zones": 1, "type": "regular"}      # 2.5 + 1 = 3.5
            ]
        }
    ]
    # Total = 3.5 + 0.0 + 3.5 = 7.0
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 7.0, "status": "COMPLETED"}


def test_priority_boarding_fee():
    """Priority boarding adds booking fee to the manifest."""
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "priority_boarding": True,
            "commuters": [{"zones": 1, "type": "regular"}]  # 3.5
        }
    ]
    # 3.5 + booking_fee (2.5) = 6.0
    result = process_commute_manifest(manifests, 2.5)
    assert result == {"total_fare": 6.0, "status": "COMPLETED"}


def test_empty_commuters_list_in_active_manifest():
    """Manifest with empty commuters list."""
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": []
        }
    ]
    result = process_commute_manifest(manifests, 2.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_audit_rejected_status():
    """More than 4 rejected rides triggers AUDIT_REJECTED."""
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [
                {"zones": 0},  # reject 1
                {"zones": -1}, # reject 2
                {"zones": -2}, # reject 3
                {"zones": -3}, # reject 4
                {"zones": -4}, # reject 5
                {"zones": 1, "type": "regular"}  # valid ride: 3.5
            ]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 3.5, "status": "AUDIT_REJECTED"}


# ----------------------------------------------------------------------
# Tests for inspect_smartcard_turnstiles
# ----------------------------------------------------------------------

def test_turnstiles_no_data():
    """Empty or falsy matrix returns NO_DATA."""
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"
    assert inspect_smartcard_turnstiles(None) == "NO_DATA"


def test_turnstiles_operational():
    """Turnstiles with failures <= 3 or streak < 2 return OPERATIONAL."""
    # All failures <= 3
    matrix1 = [[0, 1, 2, 3], [1, 2]]
    assert inspect_smartcard_turnstiles(matrix1) == "OPERATIONAL"

    # Single failure > 3 then reset by <= 3
    matrix2 = [[4, 2, 4, 1]]
    assert inspect_smartcard_turnstiles(matrix2) == "OPERATIONAL"

    # Empty inner list
    matrix3 = [[]]
    assert inspect_smartcard_turnstiles(matrix3) == "OPERATIONAL"


def test_turnstiles_jam():
    """Consecutive failures > 3 of streak >= 2 returns TURNSTILE_JAM."""
    # Immediate jam
    assert inspect_smartcard_turnstiles([[4, 5]]) == "TURNSTILE_JAM"

    # Jam in second device
    assert inspect_smartcard_turnstiles([[1, 2], [5, 4]]) == "TURNSTILE_JAM"

    # Jam after a reset
    assert inspect_smartcard_turnstiles([[4, 1, 6, 7]]) == "TURNSTILE_JAM"
