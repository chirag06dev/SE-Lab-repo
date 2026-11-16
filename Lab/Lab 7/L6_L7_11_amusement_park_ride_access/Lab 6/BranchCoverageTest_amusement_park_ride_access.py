"""
Lab 6 - Branch coverage tests for amusement_park_ride_access.py
SRN : PES2UG24CS136
Name: CHIRAG ARUN YADWAD

Goal: make every decision (if / elif / loop) in amusement_park_ride_access.py
take both its True and False outcomes, including boundary values.
Run:
    coverage run --branch -m pytest BranchCoverageTest_amusement_park_ride_access.py
    coverage report -m
"""
import pytest
from amusement_park_ride_access import process_ride_admissions, inspect_safety_restraints


def patron(height=150, warning=False, child=False):
    return {"height_cm": height, "health_warning": warning, "is_child": child}


def group(ride="family", patrons=None, is_open=True, fast_lane=False):
    return {
        "is_open": is_open,
        "ride_type": ride,
        "has_fast_lane": fast_lane,
        "patrons": patrons if patrons is not None else [],
    }


# ======================================================= input validation
# Decision: not isinstance(groups, list) or express_pass_fee < 0
@pytest.mark.parametrize(
    "groups, fee",
    [
        ("not a list", 5.0),     # left side True
        (None, 5.0),             # left side True
        ([], -1.0),              # left False, right True
    ],
)
def test_invalid_input_raises(groups, fee):
    with pytest.raises(ValueError, match="Invalid groups list or pass fee"):
        process_ride_admissions(groups, fee)


def test_zero_fee_is_valid_boundary():
    # fee == 0 is allowed (fee < 0 is False)
    result = process_ride_admissions([group(patrons=[patron()], fast_lane=True)], 0.0)
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


# ====================================================== groups loop
def test_empty_groups_list_zero_admissions():
    # loop body never runs; revenue 0 -> ZERO_ADMISSIONS
    assert process_ride_admissions([], 5.0) == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


# Decision: not group.get("is_open", False)
def test_closed_group_is_skipped():
    groups = [group(is_open=False, patrons=[patron()]), group(patrons=[patron()])]
    assert process_ride_admissions(groups, 5.0)["total_revenue"] == 10.0


def test_missing_is_open_defaults_to_closed():
    groups = [{"ride_type": "family", "patrons": [patron()]}]
    assert process_ride_admissions(groups, 5.0)["status"] == "ZERO_ADMISSIONS"


# Decision chain: roller_coaster / water_ride / family / other
@pytest.mark.parametrize(
    "ride, expected",
    [
        ("roller_coaster", 25.0),
        ("water_ride", 18.0),
        ("family", 10.0),
    ],
)
def test_ride_type_base_ticket(ride, expected):
    result = process_ride_admissions([group(ride=ride, patrons=[patron()])], 5.0)
    assert result == {"total_revenue": expected, "status": "COMPLETED"}


def test_missing_ride_type_defaults_to_family():
    groups = [{"is_open": True, "patrons": [patron()]}]
    assert process_ride_admissions(groups, 5.0)["total_revenue"] == 10.0


def test_unknown_ride_type_rejected():
    groups = [group(ride="bumper_cars", patrons=[patron()]), group(patrons=[patron()])]
    assert process_ride_admissions(groups, 5.0) == {"total_revenue": 10.0, "status": "COMPLETED"}


# ====================================================== patrons loop
def test_group_with_no_patrons_only_fast_lane_fee():
    # patrons loop never runs; fast lane still charged
    result = process_ride_admissions([group(patrons=[], fast_lane=True)], 7.5)
    assert result == {"total_revenue": 7.5, "status": "COMPLETED"}


def test_missing_patrons_key():
    groups = [{"is_open": True, "ride_type": "family", "has_fast_lane": True}]
    assert process_ride_admissions(groups, 4.0)["total_revenue"] == 4.0


# Decision: height_cm <= 0  (boundary 0 / 1)
def test_zero_height_rejected():
    result = process_ride_admissions([group(patrons=[patron(height=0), patron()])], 5.0)
    assert result["total_revenue"] == 10.0


def test_missing_height_defaults_to_zero_and_rejected():
    result = process_ride_admissions([group(patrons=[{"is_child": False}, patron()])], 5.0)
    assert result["total_revenue"] == 10.0


# Decision: health warning, nested roller_coaster check
def test_health_warning_on_roller_coaster_wipes_group_and_breaks():
    # adult (25) then warning -> group_total reset to 0 and loop breaks,
    # so the adult after the warning is never processed
    patrons = [patron(), patron(warning=True), patron()]
    result = process_ride_admissions([group(ride="roller_coaster", patrons=patrons)], 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_health_warning_on_roller_coaster_still_charges_fast_lane():
    patrons = [patron(warning=True)]
    result = process_ride_admissions(
        [group(ride="roller_coaster", patrons=patrons, fast_lane=True)], 6.0
    )
    assert result == {"total_revenue": 6.0, "status": "COMPLETED"}


def test_health_warning_on_other_ride_adds_nothing_and_continues():
    patrons = [patron(warning=True), patron()]
    result = process_ride_admissions([group(ride="water_ride", patrons=patrons)], 5.0)
    assert result == {"total_revenue": 18.0, "status": "COMPLETED"}


# Decision: height_cm < 120  (boundary 119 / 120)
@pytest.mark.parametrize(
    "height, expected",
    [
        (1, 0.0),
        (119, 0.0),
        (120, 10.0),
        (121, 10.0),
    ],
)
def test_height_limit_boundary(height, expected):
    result = process_ride_admissions([group(patrons=[patron(height=height)])], 5.0)
    assert result["total_revenue"] == expected


# Decision: is_child  (60% ticket vs full ticket)
def test_child_pays_sixty_percent():
    result = process_ride_admissions([group(ride="roller_coaster", patrons=[patron(child=True)])], 5.0)
    assert result["total_revenue"] == 15.0


def test_adult_pays_full_price():
    result = process_ride_admissions([group(ride="roller_coaster", patrons=[patron(child=False)])], 5.0)
    assert result["total_revenue"] == 25.0


# Decision: has_fast_lane
def test_fast_lane_true_and_false():
    groups = [
        group(patrons=[patron()], fast_lane=True),
        group(patrons=[patron()], fast_lane=False),
    ]
    assert process_ride_admissions(groups, 5.0)["total_revenue"] == 25.0


# ====================================================== final status
# Decision: rejected_patrons > 4  (boundary 4 / 5)
def test_four_rejections_is_not_audit():
    patrons = [patron(height=100)] * 4 + [patron()]
    assert process_ride_admissions([group(patrons=patrons)], 5.0) == {
        "total_revenue": 10.0, "status": "COMPLETED"
    }


def test_five_rejections_triggers_safety_audit():
    patrons = [patron(height=100)] * 5 + [patron()]
    assert process_ride_admissions([group(patrons=patrons)], 5.0) == {
        "total_revenue": 10.0, "status": "SAFETY_AUDIT"
    }


# Decision: total_revenue == 0.0
def test_zero_revenue_without_audit():
    patrons = [patron(height=100)] * 4
    assert process_ride_admissions([group(patrons=patrons)], 5.0) == {
        "total_revenue": 0.0, "status": "ZERO_ADMISSIONS"
    }


def test_multiple_child_tickets_add_up():
    patrons = [patron(child=True)] * 3   # 3 * (10 * 0.6) = 18.0
    assert process_ride_admissions([group(patrons=patrons)], 5.0)["total_revenue"] == 18.0


# =============================================== inspect_safety_restraints
@pytest.mark.parametrize(
    "streams, expected",
    [
        ([], "NO_DATA"),                         # empty list
        (None, "NO_DATA"),                       # falsy input
        ([[]], "SAFE"),                          # stream with no readings
        ([[1, 1, 1]], "SAFE"),                   # never unlatched
        ([[0]], "SAFE"),                         # single unlatch, streak 1
        ([[0, 1, 0, 1]], "SAFE"),                # streak reset by latched reading
        ([[0, 0]], "EMERGENCY_LOCK"),            # streak reaches 2 (boundary)
        ([[1, 0, 0, 0]], "EMERGENCY_LOCK"),
        ([[1, 1], [0, 1], [1, 0, 0]], "EMERGENCY_LOCK"),  # found in a later stream
        ([[1, 0], [0, 1]], "SAFE"),              # streak does not carry across streams
    ],
)
def test_inspect_safety_restraints(streams, expected):
    assert inspect_safety_restraints(streams) == expected
