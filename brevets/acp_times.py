"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_alg.html
and https://rusa.org/pages/rulesForRiders
"""
import math

import arrow

# (segment_start_km, segment_end_km, min_speed_kmh, max_speed_kmh)
# Speeds apply to the portion of the control distance inside each segment.
SPEED_TABLE = [
    (0, 200, 15, 34),
    (200, 400, 15, 32),
    (400, 600, 15, 30),
    (600, 1000, 11.428, 28),
    (1000, 1300, 13.333, 26),
]

# Fixed overall time limits (hours) for each official brevet distance.
# These override the computed close time at (or past) the finish.
FINISH_CLOSE_HOURS = {
    200: 13.5,
    300: 20,
    400: 27,
    600: 40,
    1000: 75,
}

# Controls in the first 60 km close at 20 km/h plus one hour
# (the French "relaxed" rule adopted by RUSA's calculator).
EARLY_CONTROL_KM = 60
EARLY_CONTROL_SPEED = 20
EARLY_CONTROL_BONUS_HOURS = 1

# A final control may be at most 20% past the nominal brevet distance.
MAX_OVERSHOOT = 1.2


def _validate(control_dist_km, brevet_dist_km):
    """Check inputs and return the control distance truncated to whole
    kilometers, as the RUSA calculator does before any calculation."""
    control_dist_km = math.floor(control_dist_km)
    if brevet_dist_km not in FINISH_CLOSE_HOURS:
        raise ValueError(
            "Brevet distance must be one of {}".format(
                sorted(FINISH_CLOSE_HOURS)))
    if control_dist_km < 0:
        raise ValueError("Control distance cannot be negative")
    if control_dist_km > brevet_dist_km * MAX_OVERSHOOT:
        raise ValueError(
            "Control distance is more than 20% past the brevet distance")
    return control_dist_km


def _hours_at_speed(dist_km, use_max_speed):
    """Total riding time for dist_km, applying each segment's speed
    only to the kilometers that fall inside that segment."""
    hours = 0.0
    for seg_start, seg_end, min_speed, max_speed in SPEED_TABLE:
        if dist_km <= seg_start:
            break
        covered = min(dist_km, seg_end) - seg_start
        hours += covered / (max_speed if use_max_speed else min_speed)
    return hours


def _shift(brevet_start_time, hours):
    """Shift the start time by hours, rounded to the nearest minute
    (halves round up, matching the RUSA calculator)."""
    minutes = math.floor(hours * 60 + 0.5)
    return arrow.get(brevet_start_time).shift(minutes=minutes).isoformat()


def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
       brevet_dist_km: number, the nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control open time.
       This will be in the same time zone as the brevet start time.
    Raises:
       ValueError for an invalid brevet distance, a negative control
       distance, or a control more than 20% past the brevet distance.
    """
    control_dist_km = _validate(control_dist_km, brevet_dist_km)
    dist = min(control_dist_km, brevet_dist_km)
    return _shift(brevet_start_time, _hours_at_speed(dist, use_max_speed=True))


def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
       control_dist_km:  number, the control distance in kilometers
          brevet_dist_km: number, the nominal distance of the brevet
          in kilometers, which must be one of 200, 300, 400, 600, or 1000
          (the only official ACP brevet distances)
       brevet_start_time:  An ISO 8601 format date-time string indicating
           the official start time of the brevet
    Returns:
       An ISO 8601 format date string indicating the control close time.
       This will be in the same time zone as the brevet start time.
    Raises:
       ValueError for an invalid brevet distance, a negative control
       distance, or a control more than 20% past the brevet distance.
    """
    control_dist_km = _validate(control_dist_km, brevet_dist_km)
    if control_dist_km >= brevet_dist_km:
        hours = FINISH_CLOSE_HOURS[brevet_dist_km]
    elif control_dist_km <= EARLY_CONTROL_KM:
        hours = (control_dist_km / EARLY_CONTROL_SPEED
                 + EARLY_CONTROL_BONUS_HOURS)
    else:
        hours = _hours_at_speed(control_dist_km, use_max_speed=False)
    return _shift(brevet_start_time, hours)
