from helpers import ALICE, BOB, held_tickets, scan


def test_place_order_charges_buyer_for_each_ticket_plus_fees(client, payments):
    resp = client.post("/orders", json={"event_id": "evt_jazz", "quantity": 2}, headers=ALICE)
    assert resp.status_code == 201
    assert resp.get_json()["total_cents"] == 10700
    assert payments.charges == [("pay_1", "alice@example.com", 10700)]


def test_order_requires_sign_in(client):
    resp = client.post("/orders", json={"event_id": "evt_jazz", "quantity": 1})
    assert resp.status_code == 401


def test_quantity_is_limited_per_order(client):
    resp = client.post("/orders", json={"event_id": "evt_jazz", "quantity": 9}, headers=ALICE)
    assert resp.status_code == 400


def test_cannot_oversell_an_event(client, store):
    store.events["evt_comedy"].capacity = 3
    client.post("/orders", json={"event_id": "evt_comedy", "quantity": 2}, headers=ALICE)
    resp = client.post("/orders", json={"event_id": "evt_comedy", "quantity": 2}, headers=BOB)
    assert resp.status_code == 409
    assert resp.get_json() == {"error": "not enough tickets left"}


def test_cancel_refunds_full_total_and_voids_tickets(client, payments, alice_order):
    resp = client.post(f"/orders/{alice_order['id']}/cancel", headers=ALICE)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "cancelled"
    assert payments.refunds == [("pay_1", 10700)]
    statuses = {t["status"] for t in held_tickets(client, ALICE)}
    assert statuses == {"void"}


def test_only_the_buyer_can_cancel(client, alice_order):
    resp = client.post(f"/orders/{alice_order['id']}/cancel", headers=BOB)
    assert resp.status_code == 404


def test_cannot_cancel_after_event_starts(client, clock, alice_order):
    clock.advance(days=40)
    resp = client.post(f"/orders/{alice_order['id']}/cancel", headers=ALICE)
    assert resp.status_code == 409


def test_cannot_cancel_after_a_ticket_is_scanned(client, alice_order):
    ticket = held_tickets(client, ALICE)[0]
    assert scan(client, ticket["qr_token"]).status_code == 200
    resp = client.post(f"/orders/{alice_order['id']}/cancel", headers=ALICE)
    assert resp.status_code == 409
    assert resp.get_json() == {"error": "order has checked-in tickets"}
