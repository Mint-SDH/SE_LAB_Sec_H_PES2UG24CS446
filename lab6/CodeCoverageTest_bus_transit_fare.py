import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles

"""
CodeCoverageTest_bus_transit_fare.py
Test suite designed to achieve 100% line/statement coverage on bus_transit_fare.py.
"""

def test_invalid_manifests_type():
    """Line coverage for invalid manifests parameter."""
    with pytest.raises(ValueError, match="Invalid manifests list or booking fee"):
        process_commute_manifest("invalid_type", 2.0)


def test_invalid_booking_fee():
    """Line coverage for invalid booking fee parameter."""
    with pytest.raises(ValueError, match="Invalid manifests list or booking fee"):
        process_commute_manifest([], -1.0)


def test_inactive_route():
    """Line coverage for skipping inactive routes (continue)."""
    manifests = [{"route_active": False, "route_type": "local"}]
    result = process_commute_manifest(manifests, 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


def test_express_route_with_blacklisted_card():
    """Line coverage for express route with a blacklisted card (break statement)."""
    manifests = [
        {
            "route_active": True,
            "route_type": "express",
            "commuters": [
                {"zones": 2, "type": "regular", "blacklisted": True}
            ]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result["total_fare"] == 0.0
    assert result["status"] == "ZERO_RIDERSHIP"


def test_shuttle_route_with_concession_types():
    """Line coverage for shuttle route, student discount, and senior discount."""
    manifests = [
        {
            "route_active": True,
            "route_type": "shuttle",
            "commuters": [
                {"zones": 2, "type": "student", "blacklisted": False},
                {"zones": 2, "type": "senior", "blacklisted": False}
            ]
        }
    ]
    # base = 4.0
    # student: (4.0 + 1.0) * 0.50 = 2.50
    # senior:  (4.0 + 1.0) * 0.70 = 3.50
    # total = 6.00
    result = process_commute_manifest(manifests, 0.0)
    assert result["total_fare"] == 6.0
    assert result["status"] == "COMPLETED"


def test_local_route_regular_with_priority_boarding():
    """Line coverage for local route, regular commuters, and priority boarding fee."""
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "priority_boarding": True,
            "commuters": [
                {"zones": 2, "type": "regular", "blacklisted": False}
            ]
        }
    ]
    # base = 2.5 + 2.0 = 4.5 + booking_fee (1.5) = 6.0
    result = process_commute_manifest(manifests, 1.5)
    assert result["total_fare"] == 6.0
    assert result["status"] == "COMPLETED"


def test_unknown_route_type():
    """Line coverage for unrecognized route type handling."""
    manifests = [
        {
            "route_active": True,
            "route_type": "ferry",
            "commuters": [{"zones": 1, "type": "regular"}]
        }
    ]
    result = process_commute_manifest(manifests, 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


def test_non_express_blacklisted_card_and_invalid_zones():
    """Line coverage for non-express blacklisted card and invalid zones."""
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [
                {"zones": 0, "type": "regular"},                     # zones <= 0 rejection
                {"zones": 2, "type": "regular", "blacklisted": True}, # non-express blacklisted card
                {"zones": 1, "type": "regular"}                      # valid ride
            ]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result["total_fare"] == 3.5
    assert result["status"] == "COMPLETED"


def test_audit_rejected_condition():
    """Line coverage for rejected_rides > 4 condition (AUDIT_REJECTED)."""
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [
                {"zones": -1},
                {"zones": -2},
                {"zones": -3},
                {"zones": -4},
                {"zones": -5}
            ]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result["status"] == "AUDIT_REJECTED"


def test_turnstiles_no_data():
    """Line coverage for inspect_smartcard_turnstiles with empty data."""
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"


def test_turnstiles_operational_and_jam():
    """Line coverage for turnstiles operational and turnstile jam."""
    # Reset streak (else branch) and operational
    assert inspect_smartcard_turnstiles([[4, 1, 2]]) == "OPERATIONAL"

    # Consecutive failures triggering jam
    assert inspect_smartcard_turnstiles([[5, 5]]) == "TURNSTILE_JAM"

