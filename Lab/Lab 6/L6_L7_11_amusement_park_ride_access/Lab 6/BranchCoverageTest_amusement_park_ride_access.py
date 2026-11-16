"""Lab 6 - Step 2: test cases written to reach >= 90% BRANCH coverage.

This file contains every test from the code coverage step plus extra tests
that drive each decision (if / elif / loop) to both its True and False outcome.

Run:
    coverage run --branch -m pytest BranchCoverageTest_amusement_park_ride_access.py
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
WARNED = {"height_cm": 160, "health_warning": True, "is_child": False}


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
    group = make_group("roller_coaster", [ADULT, WARNED, ADULT])
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


# =============================================================================
# Extra tests added for BRANCH coverage
# =============================================================================

# ---- input validation: both sides of `not isinstance(...) or fee < 0` ----
@pytest.mark.parametrize("bad_groups", [None, "family", {"a": 1}, 42])
def test_non_list_groups_raise_value_error(bad_groups):
    with pytest.raises(ValueError, match="Invalid groups list or pass fee"):
        process_ride_admissions(bad_groups, 5.0)


def test_negative_fee_with_valid_list_raises_value_error():
    with pytest.raises(ValueError):
        process_ride_admissions([make_group("family", [ADULT])], -0.01)


def test_zero_fee_is_accepted():
    result = process_ride_admissions([make_group("family", [ADULT])], 0)
    assert result["status"] == "COMPLETED"


# ---- group loop: never entered ----
def test_empty_group_list_gives_zero_admissions():
    assert process_ride_admissions([], 5.0) == {
        "total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


# ---- group defaults when keys are missing ----
def test_group_without_is_open_is_treated_as_closed():
    result = process_ride_admissions([{"patrons": [ADULT]}], 5.0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_missing_ride_type_defaults_to_family_and_missing_patrons_is_empty():
    open_group = {"is_open": True, "patrons": [ADULT]}
    assert process_ride_admissions([open_group], 0)["total_revenue"] == 10.0
    no_patrons = {"is_open": True}
    assert process_ride_admissions([no_patrons], 0)["status"] == "ZERO_ADMISSIONS"


# ---- ride type branches: every if / elif / else outcome ----
@pytest.mark.parametrize("ride_type, price", [
    ("roller_coaster", 25.0),
    ("water_ride", 18.0),
    ("family", 10.0),
])
def test_adult_base_ticket_prices(ride_type, price):
    result = process_ride_admissions([make_group(ride_type, [ADULT])], 0)
    assert result["total_revenue"] == price


@pytest.mark.parametrize("ride_type, price", [
    ("roller_coaster", 15.0),
    ("water_ride", 10.8),
    ("family", 6.0),
])
def test_child_pays_sixty_percent(ride_type, price):
    result = process_ride_admissions([make_group(ride_type, [CHILD])], 0)
    assert result["total_revenue"] == pytest.approx(price)


def test_unknown_ride_type_does_not_charge_fast_lane():
    group = make_group("carousel", [ADULT], fast_lane=True)
    assert process_ride_admissions([group], 9.0)["total_revenue"] == 0.0


def test_open_group_with_no_patrons():
    result = process_ride_admissions([make_group("family", [])], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


# ---- patron branches ----
def test_empty_patron_dictionary_is_rejected():
    result = process_ride_admissions([make_group("family", [{}])], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_negative_height_is_rejected():
    patron = {"height_cm": -5}
    result = process_ride_admissions([make_group("family", [patron, ADULT])], 0)
    assert result["total_revenue"] == 10.0


@pytest.mark.parametrize("height, accepted", [(119, False), (119.9, False),
                                              (120, True), (121, True)])
def test_minimum_height_boundary(height, accepted):
    patron = {"height_cm": height, "health_warning": False, "is_child": False}
    result = process_ride_admissions([make_group("family", [patron])], 0)
    assert (result["total_revenue"] == 10.0) is accepted


def test_health_warning_on_non_coaster_only_skips_that_patron():
    group = make_group("water_ride", [WARNED, ADULT])
    result = process_ride_admissions([group], 0)
    assert result == {"total_revenue": 18.0, "status": "COMPLETED"}


def test_health_warning_takes_priority_over_height_check():
    short_warned = {"height_cm": 100, "health_warning": True, "is_child": True}
    group = make_group("family", [short_warned, ADULT])
    assert process_ride_admissions([group], 0)["total_revenue"] == 10.0


def test_coaster_warning_discards_group_but_keeps_other_groups():
    groups = [make_group("roller_coaster", [ADULT, WARNED]),
              make_group("family", [ADULT])]
    result = process_ride_admissions(groups, 0)
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


def test_coaster_warning_still_charges_fast_lane_fee():
    group = make_group("roller_coaster", [ADULT, WARNED], fast_lane=True)
    result = process_ride_admissions([group], 5.0)
    assert result["total_revenue"] == 5.0


def test_fast_lane_missing_means_no_fee():
    group = {"is_open": True, "ride_type": "family", "patrons": [ADULT]}
    assert process_ride_admissions([group], 99.0)["total_revenue"] == 10.0


# ---- final status branches ----
def test_more_than_four_rejections_triggers_safety_audit():
    patrons = [{"height_cm": 0}] * 5
    result = process_ride_admissions([make_group("family", patrons)], 0)
    assert result == {"total_revenue": 0.0, "status": "SAFETY_AUDIT"}


def test_safety_audit_keeps_revenue_total():
    patrons = [ADULT] + [{"height_cm": 0}] * 5
    result = process_ride_admissions([make_group("family", patrons)], 0)
    assert result == {"total_revenue": 10.0, "status": "SAFETY_AUDIT"}


def test_exactly_four_rejections_is_not_a_safety_audit():
    patrons = [ADULT] + [{"height_cm": 0}] * 4
    result = process_ride_admissions([make_group("family", patrons)], 0)
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


def test_rejections_accumulate_across_groups():
    groups = [make_group("carousel", [ADULT]) for _ in range(5)]
    groups.append(make_group("family", [ADULT]))
    result = process_ride_admissions(groups, 0)
    assert result["status"] == "SAFETY_AUDIT"


def test_revenue_is_rounded_to_two_decimals():
    group = make_group("family", [ADULT], fast_lane=True)
    assert process_ride_admissions([group], 0.333)["total_revenue"] == 10.33


# ---- inspect_safety_restraints branches ----
def test_none_restraint_data():
    assert inspect_safety_restraints(None) == "NO_DATA"


def test_stream_with_no_readings_is_safe():
    assert inspect_safety_restraints([[]]) == "SAFE"


def test_single_unlatched_reading_is_safe():
    assert inspect_safety_restraints([[0]]) == "SAFE"


def test_unlatched_streak_is_reset_by_latched_reading():
    assert inspect_safety_restraints([[0, 1, 0, 1, 0]]) == "SAFE"


def test_emergency_lock_on_first_two_readings():
    assert inspect_safety_restraints([[0, 0]]) == "EMERGENCY_LOCK"


def test_emergency_lock_found_in_a_later_stream():
    streams = [[1, 1], [0, 1], [0, 0, 0]]
    assert inspect_safety_restraints(streams) == "EMERGENCY_LOCK"


def test_streak_does_not_carry_over_between_streams():
    assert inspect_safety_restraints([[1, 0], [0, 1]]) == "SAFE"
