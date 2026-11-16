"""Lab 6 - Step 1: test cases written to reach >= 90% LINE coverage.

Run:
    coverage run -m pytest CodeCoverageTest_amusement_park_ride_access.py
    coverage report -m --include=amusement_park_ride_access.py
"""
import pytest

from amusement_park_ride_access import (
    inspect_safety_restraints,
    process_ride_admissions,
)


def make_group(ride_type, patrons, is_open=True, fast_lane=False):
    """Helper that builds a group dictionary."""
    return {
        "is_open": is_open,
        "ride_type": ride_type,
        "has_fast_lane": fast_lane,
        "patrons": patrons,
    }


ADULT = {"height_cm": 150, "health_warning": False, "is_child": False}
CHILD = {"height_cm": 130, "health_warning": False, "is_child": True}


# ----------------------------------------------------- starter test case
def test_single_adult_family_ride():
    groups = [make_group("family", [ADULT])]
    result = process_ride_admissions(groups, 5.0)
    assert result["total_revenue"] == 10.0
    assert result["status"] == "COMPLETED"


# ------------------------------------------- process_ride_admissions
def test_invalid_pass_fee_raises_value_error():
    with pytest.raises(ValueError):
        process_ride_admissions([], -1)


def test_closed_group_is_skipped():
    groups = [make_group("family", [ADULT], is_open=False)]
    result = process_ride_admissions(groups, 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_roller_coaster_adult_price():
    result = process_ride_admissions([make_group("roller_coaster", [ADULT])], 0)
    assert result == {"total_revenue": 25.0, "status": "COMPLETED"}


def test_water_ride_child_gets_discount():
    result = process_ride_admissions([make_group("water_ride", [CHILD])], 0)
    assert result["total_revenue"] == pytest.approx(10.8)
    assert result["status"] == "COMPLETED"


def test_unknown_ride_type_is_rejected():
    result = process_ride_admissions([make_group("carousel", [ADULT])], 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_patron_with_no_height_is_rejected():
    patrons = [ADULT, {"height_cm": 0}]
    result = process_ride_admissions([make_group("family", patrons)], 0)
    assert result["total_revenue"] == 10.0


def test_too_short_patron_is_rejected():
    short = {"height_cm": 100, "health_warning": False, "is_child": True}
    result = process_ride_admissions([make_group("family", [short, ADULT])], 0)
    assert result["total_revenue"] == 10.0


def test_health_warning_on_roller_coaster_cancels_group_total():
    warned = {"height_cm": 160, "health_warning": True, "is_child": False}
    group = make_group("roller_coaster", [ADULT, warned, ADULT])
    result = process_ride_admissions([group], 0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_fast_lane_fee_is_added():
    group = make_group("family", [ADULT], fast_lane=True)
    result = process_ride_admissions([group], 7.5)
    assert result["total_revenue"] == 17.5


# ------------------------------------------- inspect_safety_restraints
def test_no_restraint_data():
    assert inspect_safety_restraints([]) == "NO_DATA"


def test_two_unlatched_readings_trigger_emergency_lock():
    assert inspect_safety_restraints([[1, 0, 0, 1]]) == "EMERGENCY_LOCK"


def test_all_latched_is_safe():
    assert inspect_safety_restraints([[1, 1, 1], [1, 0, 1, 0, 1]]) == "SAFE"
