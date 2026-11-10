def test_lists_upcoming_events_in_date_order(client):
    events = client.get("/events").get_json()["events"]
    assert [e["id"] for e in events] == ["evt_jazz", "evt_comedy"]


def test_event_shows_price_fee_and_tickets_left(client, alice_order):
    event = client.get("/events/evt_jazz").get_json()
    assert event["price_cents"] == 5350
    assert event["face_value_cents"] == 5000
    assert event["service_fee_cents"] == 350
    assert event["tickets_left"] == 198


def test_unknown_event_is_404(client):
    assert client.get("/events/evt_nope").status_code == 404
