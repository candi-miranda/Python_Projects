ATR72 = {
    "name": "ATR 72-600",
    "empty_weight_kg": 13450.0,
    "max_fuel_kg": 4626.0,
    "cruise_mach": 0.443,
    "speed_of_sound_ms": 309.6,
    "lift_to_drag": 16.5,
    "tsfc_per_s": 1.25e-4,
}

LISBON = {"icao": "LPPT", "name": "Lisbon Humberto Delgado", "latitude": 38.7813, "longitude": -9.1359}
PONTA_DELGADA = {"icao": "LPPD", "name": "Ponta Delgada", "latitude": 37.7412, "longitude": -25.6979}


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_and_list_aircraft(client):
    resp = client.post("/aircraft", json=ATR72)
    assert resp.status_code == 201
    assert resp.json()["name"] == "ATR 72-600"

    resp = client.get("/aircraft")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_create_aircraft_rejects_duplicate_name(client):
    client.post("/aircraft", json=ATR72)
    resp = client.post("/aircraft", json=ATR72)
    assert resp.status_code == 409


def test_create_aircraft_rejects_invalid_data(client):
    bad_aircraft = {**ATR72, "empty_weight_kg": -100.0}
    resp = client.post("/aircraft", json=bad_aircraft)
    assert resp.status_code == 422


def test_get_aircraft_not_found(client):
    resp = client.get("/aircraft/999")
    assert resp.status_code == 404


def test_create_and_list_airports(client):
    client.post("/airports", json=LISBON)
    client.post("/airports", json=PONTA_DELGADA)

    resp = client.get("/airports")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_route_feasibility_reachable(client):
    client.post("/aircraft", json=ATR72)
    client.post("/airports", json=LISBON)
    client.post("/airports", json=PONTA_DELGADA)

    resp = client.get(
        "/route/LPPT/LPPD/feasibility",
        params={"aircraft_name": "ATR 72-600"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["origin"] == "LPPT"
    assert data["destination"] == "LPPD"
    assert data["feasible"] is True
    assert data["margin_km"] > 0


def test_route_feasibility_unreachable_for_short_range_aircraft(client):
    short_range_aircraft = {
        **ATR72,
        "name": "Short Hopper",
        "max_fuel_kg": 200.0,  # tiny fuel load -> tiny range
    }
    client.post("/aircraft", json=short_range_aircraft)
    client.post("/airports", json=LISBON)
    client.post("/airports", json=PONTA_DELGADA)

    resp = client.get(
        "/route/LPPT/LPPD/feasibility",
        params={"aircraft_name": "Short Hopper"},
    )
    assert resp.status_code == 200
    assert resp.json()["feasible"] is False


def test_route_feasibility_unknown_airport(client):
    client.post("/aircraft", json=ATR72)
    resp = client.get(
        "/route/ZZZZ/LPPD/feasibility",
        params={"aircraft_name": "ATR 72-600"},
    )
    assert resp.status_code == 404
