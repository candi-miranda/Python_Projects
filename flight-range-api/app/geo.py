"""
Pure, side-effect-free calculations. Kept separate from the API and
database layers so they can be unit tested directly, with no need to
spin up a DB or an HTTP client.
"""
import math

EARTH_RADIUS_KM = 6371.0


def great_circle_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two points on Earth, using the
    haversine formula.
    """
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c


def breguet_range_km(
    cruise_mach: float,
    speed_of_sound_ms: float,
    lift_to_drag: float,
    tsfc_per_s: float,
    empty_weight_kg: float,
    fuel_weight_kg: float,
) -> float:
    """
    Maximum cruise range via the Breguet range equation:

        R = (M * a / CT) * (CL/CD) * ln(1 + WF / W0)

    Same formula used in the Aircraft Optimal Design coursework
    (see the `range_explicit.py` / `BreguetRange` components), reused
    here as a small, dependency-free function.
    """
    velocity_ms = cruise_mach * speed_of_sound_ms
    range_m = (
        (velocity_ms / tsfc_per_s)
        * lift_to_drag
        * math.log(1 + fuel_weight_kg / empty_weight_kg)
    )
    return range_m / 1000.0
