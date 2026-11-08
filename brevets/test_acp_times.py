"""
Nose tests for acp_times.py

Expected values come from the worked examples at
https://rusa.org/pages/acp-brevet-control-times-calculator
and were cross-checked against https://rusa.org/octime_acp.html.

Run from the brevets directory with:  nosetests
"""
import arrow
from acp_times import open_time, close_time

START = "2017-01-01T00:00:00+00:00"


def assert_raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return
    raise AssertionError("{} not raised".format(exc.__name__))


def after(hours, minutes):
    """ISO time `hours`h`minutes`m after START."""
    return arrow.get(START).shift(hours=hours, minutes=minutes).isoformat()


def check(control_km, brevet_km, open_hm, close_hm):
    assert open_time(control_km, brevet_km, START) == after(*open_hm)
    assert close_time(control_km, brevet_km, START) == after(*close_hm)


def test_start_control():
    # Start opens at the start time and closes one hour later
    check(0, 200, (0, 0), (1, 0))


def test_first_segment():
    # 200km brevet, controls at 60/120/175 (RUSA example 1)
    check(60, 200, (1, 46), (4, 0))
    check(120, 200, (3, 32), (8, 0))
    check(175, 200, (5, 9), (11, 40))


def test_early_controls_relaxed_close():
    # Within the first 60km close = dist/20 + 1h, not dist/15
    check(20, 200, (0, 35), (2, 0))
    check(50, 300, (1, 28), (3, 30))
    # Just past 60km the normal 15 km/h rule applies again
    check(61, 200, (1, 48), (4, 4))


def test_finish_uses_fixed_limits():
    # Final controle closes at the fixed per-brevet limit,
    # not the value the speed table would give
    check(200, 200, (5, 53), (13, 30))
    check(300, 300, (9, 0), (20, 0))
    check(400, 400, (12, 8), (27, 0))
    check(600, 600, (18, 48), (40, 0))
    check(1000, 1000, (33, 5), (75, 0))


def test_finish_past_nominal_distance():
    # A finish up to 20% long is timed as if at the nominal distance
    check(205, 200, (5, 53), (13, 30))
    check(240, 200, (5, 53), (13, 30))
    check(609, 600, (18, 48), (40, 0))


def test_multi_segment_speeds():
    # 600km brevet (RUSA example 2): speeds change at 200 and 400km
    check(350, 600, (10, 34), (23, 20))
    check(550, 600, (17, 8), (36, 40))
    # 1000km brevet (RUSA example 3): 600-1000 segment at 11.428/28
    check(890, 1000, (29, 9), (65, 23))


def test_fractional_distance_truncated_to_km():
    # RUSA truncates distances to whole km before calculating:
    # 100.9km is timed as 100km (2H56 / 6H40), not 100.9km (2H58 / 6H44)
    check(100.9, 200, (2, 56), (6, 40))
    # 240.9km on a 200km brevet truncates to 240km: still within 20%
    check(240.9, 200, (5, 53), (13, 30))


def test_intermediate_control_at_brevet_distance():
    # 200km is the finish of a 200km brevet (fixed 13H30) but only an
    # intermediate control on a 400km brevet (200/15 = 13H20)
    check(200, 400, (5, 53), (13, 20))
    check(600, 1000, (18, 48), (40, 0))


def test_control_closer_than_15km():
    # Oddities: by the plain 15 km/h rule a 10km control would close at
    # 0H40, before the start closes. The 60km rule gives 10/20 + 1 = 1H30
    check(10, 200, (0, 18), (1, 30))


def test_preserves_time_zone():
    start = "2021-06-15T07:30:00-07:00"
    assert open_time(100, 200, start) == "2021-06-15T10:26:00-07:00"
    assert close_time(100, 200, start) == "2021-06-15T14:10:00-07:00"


def test_invalid_input():
    assert_raises(ValueError, open_time, -5, 200, START)
    assert_raises(ValueError, close_time, 250, 200, START)  # > 20% over
    assert_raises(ValueError, open_time, 100, 250, START)   # not a brevet
