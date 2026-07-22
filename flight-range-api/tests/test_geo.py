import math

import pytest

from app.geo import breguet_range_km, great_circle_distance_km


def test_great_circle_distance_zero_for_same_point():
    d = great_circle_distance_km(38.7813, -9.1359, 38.7813, -9.1359)
    assert d == pytest.approx(0.0, abs=1e-6)


def test_great_circle_distance_lisbon_ponta_delgada():
    # Lisbon (LPPT) to Ponta Delgada (LPPD), known to be roughly 1450-1470 km
    d = great_circle_distance_km(38.7813, -9.1359, 37.7412, -25.6979)
    assert 1400 < d < 1550


def test_great_circle_distance_is_symmetric():
    d1 = great_circle_distance_km(38.7813, -9.1359, 51.4700, -0.4543)
    d2 = great_circle_distance_km(51.4700, -0.4543, 38.7813, -9.1359)
    assert d1 == pytest.approx(d2, rel=1e-9)


def test_breguet_range_positive_for_valid_inputs():
    r = breguet_range_km(
        cruise_mach=0.443,
        speed_of_sound_ms=309.6,
        lift_to_drag=16.5,
        tsfc_per_s=1.25e-4,
        empty_weight_kg=13450.0,
        fuel_weight_kg=4626.0,
    )
    assert r > 0


def test_breguet_range_increases_with_more_fuel():
    kwargs = dict(
        cruise_mach=0.443,
        speed_of_sound_ms=309.6,
        lift_to_drag=16.5,
        tsfc_per_s=1.25e-4,
        empty_weight_kg=13450.0,
    )
    r_low_fuel = breguet_range_km(fuel_weight_kg=1000.0, **kwargs)
    r_high_fuel = breguet_range_km(fuel_weight_kg=4626.0, **kwargs)
    assert r_high_fuel > r_low_fuel


def test_breguet_range_zero_fuel_gives_zero_range():
    r = breguet_range_km(
        cruise_mach=0.443,
        speed_of_sound_ms=309.6,
        lift_to_drag=16.5,
        tsfc_per_s=1.25e-4,
        empty_weight_kg=13450.0,
        fuel_weight_kg=0.0,
    )
    assert r == pytest.approx(0.0, abs=1e-9)
