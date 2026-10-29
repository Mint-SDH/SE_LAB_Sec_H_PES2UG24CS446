import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles

"""
BranchCoverageTest_bus_transit_fare.py
Exhaustive test suite designed to achieve 100% branch and decision coverage on bus_transit_fare.py.
Covers every branch condition (True and False paths), edge cases, and control flow paths.
"""

# ======================================================================
# 1. Tests for process_commute_manifest Input Validation Branches
# ======================================================================

def test_manifests_not_list():
    """Branch: not isinstance(manifests, list) is True."""
    with pytest.raises(ValueError, match="Invalid manifests list or booking fee"):
        process_commute_manifest("invalid_type", 2.0)

    with pytest.raises(ValueError, match="Invalid manifests list or booking fee"):
        process_commute_manifest(None, 2.0)


def test_booking_fee_negative():
    """Branch: booking_fee < 0 is True while isinstance(manifests, list) is True."""
    with pytest.raises(ValueError, match="Invalid manifests list or booking fee"):
        process_commute_manifest([], -0.5)


def test_empty_manifests_loop():
    """Branch: for manifest in manifests loop does not execute (0 iterations)."""
    result = process_commute_manifest([], 2.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


# ======================================================================
# 2. Tests for Manifest Route Active & Route Types
# ======================================================================

def test_route_active_branches():
    """Branch: not manifest.get('route_active', False) evaluates to True and False."""
    # route_active explicitly False
    manifests_inactive = [{"route_active": False, "route_type": "local"}]
    assert process_commute_manifest(manifests_inactive, 0.0)["status"] == "ZERO_RIDERSHIP"

    # route_active omitted (defaults to False)
    manifests_omitted = [{"route_type": "local"}]
    assert process_commute_manifest(manifests_omitted, 0.0)["status"] == "ZERO_RIDERSHIP"


def test_route_type_branches():
    """Branches: route_type == 'express', 'shuttle', 'local', and else (unknown)."""
    # Express: base_seat = 6.0
    res_express = process_commute_manifest([
        {"route_active": True, "route_type": "express", "commuters": [{"zones": 1, "type": "regular"}]}
    ], 0.0)
    assert res_express == {"total_fare": 7.0, "status": "COMPLETED"}

    # Shuttle: base_seat = 4.0
    res_shuttle = process_commute_manifest([
        {"route_active": True, "route_type": "shuttle", "commuters": [{"zones": 1, "type": "regular"}]}
    ], 0.0)
    assert res_shuttle == {"total_fare": 5.0, "status": "COMPLETED"}

    # Local: base_seat = 2.5
    res_local = process_commute_manifest([
        {"route_active": True, "route_type": "local", "commuters": [{"zones": 1, "type": "regular"}]}
    ], 0.0)
    assert res_local == {"total_fare": 3.5, "status": "COMPLETED"}

    # Route type omitted (defaults to "local")
    res_default = process_commute_manifest([
        {"route_active": True, "commuters": [{"zones": 1, "type": "regular"}]}
    ], 0.0)
    assert res_default == {"total_fare": 3.5, "status": "COMPLETED"}

    # Unknown route type: else branch -> rejected_rides += 1; continue
    res_unknown = process_commute_manifest([
        {"route_active": True, "route_type": "monorail", "commuters": [{"zones": 1, "type": "regular"}]}
    ], 0.0)
    assert res_unknown == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


# ======================================================================
# 3. Tests for Commuter Loops, Zones, and Card Blacklisting
# ======================================================================

def test_commuters_loop_and_defaults():
    """Branch: for commuter in commuters loop executes 0 times vs multiple times, with commuter defaults."""
    # commuters key omitted -> defaults to []
    res_empty_commuters = process_commute_manifest([{"route_active": True, "route_type": "local"}], 0.0)
    assert res_empty_commuters == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}

    # commuter dict with all fields omitted (zones=1, type="regular", blacklisted=False)
    res_default_commuter = process_commute_manifest([
        {"route_active": True, "route_type": "local", "commuters": [{}]}
    ], 0.0)
    assert res_default_commuter == {"total_fare": 3.5, "status": "COMPLETED"}


def test_commuter_zones_validation_branches():
    """Branch: zones <= 0 is True vs False."""
    manifests = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [
                {"zones": 0, "type": "regular"},   # zones <= 0 True (zero)
                {"zones": -2, "type": "regular"},  # zones <= 0 True (negative)
                {"zones": 1, "type": "regular"}   # zones <= 0 False (valid)
            ]
        }
    ]
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 3.5, "status": "COMPLETED"}


def test_blacklisted_card_branches():
    """Branches: has_blacklisted_card True/False, and route_type == 'express' True/False."""
    # Case A: Express route with blacklisted card -> manifest_fare = 0.0 and break
    manifest_express_blacklisted = [
        {
            "route_active": True,
            "route_type": "express",
            "commuters": [
                {"zones": 2, "type": "regular", "blacklisted": False}, # 8.0
                {"zones": 1, "blacklisted": True},                     # triggers 0.0 and break
                {"zones": 2, "type": "regular", "blacklisted": False}  # unreachable commuter
            ]
        }
    ]
    res_express = process_commute_manifest(manifest_express_blacklisted, 0.0)
    assert res_express == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}

    # Case B: Non-express route (local) with blacklisted card -> adds 0.0, no break
    manifest_local_blacklisted = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [
                {"zones": 1, "type": "regular", "blacklisted": False}, # 3.5
                {"zones": 2, "type": "regular", "blacklisted": True},  # rejected, fare += 0.0
                {"zones": 1, "type": "regular", "blacklisted": False}  # 3.5
            ]
        }
    ]
    res_local = process_commute_manifest(manifest_local_blacklisted, 0.0)
    assert res_local == {"total_fare": 7.0, "status": "COMPLETED"}


def test_passenger_type_branches():
    """Branches: student, senior, and regular passenger concession categories."""
    manifests = [
        {
            "route_active": True,
            "route_type": "local",  # base = 2.5
            "commuters": [
                {"zones": 3, "type": "student", "blacklisted": False}, # (2.5 + 1.5) * 0.50 = 2.0
                {"zones": 3, "type": "senior", "blacklisted": False},  # (2.5 + 1.5) * 0.70 = 2.8
                {"zones": 3, "type": "regular", "blacklisted": False}  # 2.5 + 3.0 = 5.5
            ]
        }
    ]
    # Total = 2.0 + 2.8 + 5.5 = 10.3
    result = process_commute_manifest(manifests, 0.0)
    assert result == {"total_fare": 10.3, "status": "COMPLETED"}


def test_priority_boarding_branches():
    """Branches: manifest.get('priority_boarding', False) True vs False."""
    # Priority boarding True
    res_with_pb = process_commute_manifest([
        {"route_active": True, "route_type": "local", "priority_boarding": True, "commuters": [{"zones": 1}]}
    ], 3.0)
    assert res_with_pb == {"total_fare": 6.5, "status": "COMPLETED"}

    # Priority boarding False
    res_without_pb = process_commute_manifest([
        {"route_active": True, "route_type": "local", "priority_boarding": False, "commuters": [{"zones": 1}]}
    ], 3.0)
    assert res_without_pb == {"total_fare": 3.5, "status": "COMPLETED"}


# ======================================================================
# 4. Tests for Final Status Return Branches
# ======================================================================

def test_status_branches():
    """Branches: rejected_rides > 4 (AUDIT_REJECTED), total_fare == 0.0 (ZERO_RIDERSHIP), and COMPLETED."""
    # Branch 1: rejected_rides > 4
    manifests_audit_rejected = [
        {
            "route_active": True,
            "route_type": "local",
            "commuters": [
                {"zones": 0}, {"zones": 0}, {"zones": 0}, {"zones": 0}, {"zones": 0},
                {"zones": 1, "type": "regular"}
            ]
        }
    ]
    res_audit = process_commute_manifest(manifests_audit_rejected, 0.0)
    assert res_audit == {"total_fare": 3.5, "status": "AUDIT_REJECTED"}

    # Branch 2: total_fare == 0.0 with rejected_rides <= 4
    res_zero = process_commute_manifest([], 0.0)
    assert res_zero == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}

    # Branch 3: total_fare > 0.0 with rejected_rides <= 4
    res_completed = process_commute_manifest([
        {"route_active": True, "route_type": "local", "commuters": [{"zones": 1}]}
    ], 0.0)
    assert res_completed == {"total_fare": 3.5, "status": "COMPLETED"}


# ======================================================================
# 5. Tests for inspect_smartcard_turnstiles Branches
# ======================================================================

def test_turnstiles_matrix_branches():
    """Branch: not turnstile_matrix evaluates to True and False."""
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"
    assert inspect_smartcard_turnstiles(None) == "NO_DATA"


def test_turnstiles_operational_branches():
    """Branches: failures > 3 evaluates to False (else branch resets streak), and loops finish with OPERATIONAL."""
    # Empty inner device readings
    assert inspect_smartcard_turnstiles([[]]) == "OPERATIONAL"

    # All failures <= 3 (never triggers failures > 3)
    assert inspect_smartcard_turnstiles([[0, 1, 2, 3]]) == "OPERATIONAL"

    # Streak of 1 failure > 3, then reset by failures <= 3, never reaches streak >= 2
    assert inspect_smartcard_turnstiles([[4, 1, 4, 2, 0]]) == "OPERATIONAL"


def test_turnstiles_jam_branches():
    """Branches: tap_failure_streak >= 2 is True (TURNSTILE_JAM)."""
    # Consecutive failures > 3
    assert inspect_smartcard_turnstiles([[4, 5]]) == "TURNSTILE_JAM"

    # Jam in secondary device reading list
    assert inspect_smartcard_turnstiles([[1, 2], [5, 6]]) == "TURNSTILE_JAM"

    # Reset followed by a subsequent jam
    assert inspect_smartcard_turnstiles([[4, 1, 4, 5]]) == "TURNSTILE_JAM"

