"""Ride processing helpers, hardened against invalid input (Lab 7).

Every function accepts any value without raising an exception:
 * validate_height_and_fastpass  -> always returns text ("Invalid ..." on bad input)
 * compute_dispatch_throughput   -> returns a float, or None for bad input
 * resolve_safety_restraint_code -> always returns text ("Unknown ..." on bad input)
"""
import math

ELIGIBLE_HEIGHT_CM = 120
MIN_HEIGHT_CM = 1
MAX_HEIGHT_CM = 300

RESTRAINT_TYPES = {
    "CST": "Over-the-Shoulder Harness",
    "WTR": "Lap Bar and Seatbelt",
    "DRP": "Hydraulic Shoulder Vest",
    "WHL": "Manual Safety Bar",
}


def validate_height_and_fastpass(rider_spec):
    """Validate a 'Height:FastPass' rider spec such as '140:YES'."""
    if not isinstance(rider_spec, str):
        return "Invalid input: rider spec must be text like 140:YES"

    parts = rider_spec.strip().split(':')
    if len(parts) != 2:
        return "Invalid input: use the format Height:FastPass (e.g. 140:YES)"

    height_str, pass_str = parts[0].strip(), parts[1].strip().upper()

    # Only plain ASCII digits: rejects "", "-5", "1.5", "1_0", "abc", "+3"
    if not (height_str.isascii() and height_str.isdigit()):
        return "Invalid height: must be a whole number of centimetres"
    try:
        height = int(height_str)
    except ValueError:  # e.g. thousands of digits
        return "Invalid height: number is too large"
    if not MIN_HEIGHT_CM <= height <= MAX_HEIGHT_CM:
        return (f"Invalid height: must be between {MIN_HEIGHT_CM} "
                f"and {MAX_HEIGHT_CM} cm")

    pass_map = {"YES": True, "NO": False}
    if pass_str not in pass_map:
        return "Invalid fastpass value: use YES or NO"

    eligible = height >= ELIGIBLE_HEIGHT_CM
    status = "FastPass Priority" if pass_map[pass_str] else "Standard Entry"
    return (f"Height {height}cm: {'Approved' if eligible else 'Denied'} "
            f"({status})")


def compute_dispatch_throughput(ride_metric_str):
    """Return riders per minute for a 'riders/minutes' string, else None."""
    if not isinstance(ride_metric_str, str):
        return None

    parts = ride_metric_str.split('/')
    if len(parts) != 2:
        return None

    try:
        riders = float(parts[0])
        cycle_mins = float(parts[1])
    except ValueError:
        return None

    # float() happily accepts "nan", "inf" and "1e999": reject them
    if not (math.isfinite(riders) and math.isfinite(cycle_mins)):
        return None
    if riders < 0 or cycle_mins <= 0:  # no negative riders, no divide by zero
        return None

    rate = riders / cycle_mins
    if not math.isfinite(rate):  # e.g. 1e308 / 1e-308 overflows
        return None
    return round(rate, 2)


def resolve_safety_restraint_code(zone_code):
    """Return the restraint type for a zone code such as 'CST_01'."""
    if not isinstance(zone_code, str):
        return "Unknown restraint: zone code must be text"

    prefix = zone_code.strip()[:3]
    # non-ASCII text can upper-case into a valid prefix (e.g. a ligature)
    if not prefix.isascii():
        return "Unknown restraint: unrecognised zone code"
    return RESTRAINT_TYPES.get(
        prefix.upper(), "Unknown restraint: unrecognised zone code")


def main():
    """Interactive demo of the three functions."""
    print("==== Running validate_height_and_fastpass ====")
    r_input = input("Enter rider spec (Height:FastPass, e.g. 140:YES): ")
    print(validate_height_and_fastpass(r_input))

    print("\n==== Running compute_dispatch_throughput ====")
    t_input = input("Enter riders/mins (e.g. 48/2.5): ")
    throughput = compute_dispatch_throughput(t_input)
    if throughput is None:
        print("Invalid input: use riders/minutes with minutes > 0 (e.g. 48/2.5)")
    else:
        print("Throughput (riders/min):", throughput)

    print("\n==== Running resolve_safety_restraint_code ====")
    z_input = input("Enter ride zone code (e.g. CST_01, WTR_A): ")
    print("Restraint:", resolve_safety_restraint_code(z_input))


if __name__ == "__main__":
    main()
