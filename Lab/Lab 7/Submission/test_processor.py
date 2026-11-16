"""Lab 7: property-based fuzz tests for processor.py using Hypothesis.

The first three tests are the required "no crash" properties: whatever text
(or None) Hypothesis generates, the function must not raise an exception.
The remaining tests check stronger properties on structured inputs.
"""
import math

from hypothesis import given, strategies as st

from processor import (
    compute_dispatch_throughput,
    resolve_safety_restraint_code,
    validate_height_and_fastpass,
)


# ----------------------------------------------------------------------
# 1. No-crash fuzz tests (random text or None)
# ----------------------------------------------------------------------
@given(st.text() | st.none())
def test_validate_height_and_fastpass_no_crash(s):
    try:
        validate_height_and_fastpass(s)
    except Exception as e:
        assert False, f"validate_height_and_fastpass crashed with: {e!r}"


@given(st.text() | st.none())
def test_compute_dispatch_throughput_safe(s):
    try:
        compute_dispatch_throughput(s)
    except Exception as e:
        assert False, f"compute_dispatch_throughput crashed with: {e!r}"


@given(st.text() | st.none())
def test_resolve_safety_restraint_code_safe(s):
    try:
        resolve_safety_restraint_code(s)
    except Exception as e:
        assert False, f"resolve_safety_restraint_code crashed with: {e!r}"


# ----------------------------------------------------------------------
# 2. Fuzzing with other kinds of input (numbers, lists, bytes, ...)
# ----------------------------------------------------------------------
ANY_VALUE = st.one_of(
    st.none(), st.integers(), st.floats(), st.booleans(), st.binary(),
    st.lists(st.integers()), st.text(),
)


@given(ANY_VALUE)
def test_validate_height_rejects_any_type_without_crashing(value):
    assert isinstance(validate_height_and_fastpass(value), str)


@given(ANY_VALUE)
def test_throughput_any_type_returns_float_or_none(value):
    result = compute_dispatch_throughput(value)
    assert result is None or isinstance(result, float)


@given(ANY_VALUE)
def test_restraint_any_type_returns_text(value):
    assert isinstance(resolve_safety_restraint_code(value), str)


# ----------------------------------------------------------------------
# 3. Structured inputs: check the actual business rules
# ----------------------------------------------------------------------
@given(st.integers(min_value=1, max_value=300),
       st.sampled_from(["YES", "NO", "yes", "no", " Yes ", " nO "]))
def test_valid_rider_specs_give_correct_decision(height, fastpass):
    result = validate_height_and_fastpass(f"{height}:{fastpass}")
    assert f"Height {height}cm" in result
    assert ("Approved" in result) == (height >= 120)
    assert ("FastPass Priority" in result) == (fastpass.strip().upper() == "YES")


@given(st.integers(max_value=0) | st.integers(min_value=301),
       st.sampled_from(["YES", "NO"]))
def test_out_of_range_heights_are_invalid(height, fastpass):
    result = validate_height_and_fastpass(f"{height}:{fastpass}")
    assert result.startswith("Invalid")


@given(st.integers(min_value=1, max_value=300), st.text(max_size=8))
def test_unknown_fastpass_value_is_invalid(height, word):
    if word.strip().upper() in ("YES", "NO"):
        return
    assert validate_height_and_fastpass(f"{height}:{word}").startswith("Invalid")


@given(st.integers(min_value=0, max_value=10_000),
       st.floats(min_value=0.1, max_value=1_000, allow_nan=False))
def test_valid_throughput_matches_division(riders, minutes):
    result = compute_dispatch_throughput(f"{riders}/{minutes}")
    assert result == round(riders / minutes, 2)


@given(st.integers(min_value=0, max_value=10_000))
def test_zero_or_negative_cycle_time_is_rejected(riders):
    assert compute_dispatch_throughput(f"{riders}/0") is None
    assert compute_dispatch_throughput(f"{riders}/-2.5") is None


@given(st.sampled_from(["nan", "inf", "-inf", "1e999"]), st.floats(0.1, 100))
def test_non_finite_numbers_are_rejected(token, other):
    assert compute_dispatch_throughput(f"{token}/{other}") is None
    assert compute_dispatch_throughput(f"{other}/{token}") is None


@given(st.text())
def test_throughput_result_is_finite_and_non_negative_when_present(s):
    result = compute_dispatch_throughput(s)
    if result is not None:
        assert math.isfinite(result) and result >= 0


@given(st.sampled_from(["CST", "WTR", "DRP", "WHL"]),
       st.text(max_size=10),
       st.booleans())
def test_known_zone_prefixes_resolve(prefix, suffix, lower):
    code = prefix.lower() if lower else prefix
    result = resolve_safety_restraint_code(f" {code}{suffix} ")
    assert result in {"Over-the-Shoulder Harness", "Lap Bar and Seatbelt",
                      "Hydraulic Shoulder Vest", "Manual Safety Bar"}


@given(st.text(max_size=2))
def test_short_zone_codes_are_unknown(code):
    assert resolve_safety_restraint_code(code).startswith("Unknown")
