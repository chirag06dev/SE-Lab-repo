"""
Lab 6 - Code (line) coverage tests for amusement_park_ride_access.py
SRN : PES2UG24CS136
Name: CHIRAG ARUN YADWAD

Goal: execute every line of amusement_park_ride_access.py at least once.
Run:
    coverage run -m pytest CodeCoverageTest_amusement_park_ride_access.py
    coverage report -m
"""
import pytest
from amusement_park_ride_access import process_ride_admissions, inspect_safety_restraints


def patron(height=150, warning=False, child=False):
    return {"height_cm": height, "health_warning": warning, "is_child": child}


# ------------------------------------------------- process_ride_admissions
def test_single_adult_family_ride():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "has_fast_lane": False,
            "patrons": [{"height_cm": 150, "health_warning": False, "is_child": False}]
        }
    ]
    result = process_ride_admissions(groups, 5.0)
    assert result["total_revenue"] == 10.0
    assert result["status"] == "COMPLETED"


def test_invalid_input_raises():
    # covers: raise ValueError(...)
    with pytest.raises(ValueError):
        process_ride_admissions("not a list", 5.0)


def test_mixed_groups_completed():
    groups = [
        # closed group -> skipped (continue)
        {"is_open": False, "ride_type": "family", "patrons": [patron()]},
        # water ride: adult 18 + child 18*0.6 = 10.8, fast lane +5
        # also one non-coaster health warning (adds 0.0) and one short patron
        {
            "is_open": True,
            "ride_type": "water_ride",
            "has_fast_lane": True,
            "patrons": [
                patron(),
                patron(child=True),
                patron(warning=True),
                patron(height=110),
            ],
        },
    ]
    result = process_ride_admissions(groups, 5.0)
    assert result == {"total_revenue": 33.8, "status": "COMPLETED"}


def test_roller_coaster_health_warning_and_audit():
    groups = [
        # roller coaster: adult 25, then a health warning wipes group total and breaks
        {
            "is_open": True,
            "ride_type": "roller_coaster",
            "patrons": [patron(), patron(warning=True)],
        },
        # unknown ride type -> whole group rejected (counts 1)
        {"is_open": True, "ride_type": "bumper_cars", "patrons": [patron()]},
        # invalid heights -> rejected (counts 3)
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [patron(height=0), patron(height=-5), patron(height=0)],
        },
    ]
    # rejections = 1 + 1 + 3 = 5 > 4 -> SAFETY_AUDIT
    result = process_ride_admissions(groups, 5.0)
    assert result == {"total_revenue": 0.0, "status": "SAFETY_AUDIT"}


def test_zero_admissions():
    groups = [{"is_open": True, "ride_type": "family", "patrons": [patron(height=100)]}]
    result = process_ride_admissions(groups, 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


# ----------------------------------------------- inspect_safety_restraints
def test_no_data():
    assert inspect_safety_restraints([]) == "NO_DATA"


def test_emergency_lock():
    assert inspect_safety_restraints([[1, 0, 0, 1]]) == "EMERGENCY_LOCK"


def test_safe():
    assert inspect_safety_restraints([[1, 0, 1, 1], [1, 1]]) == "SAFE"
