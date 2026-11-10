from helpers import ALICE, held_tickets, scan


def test_scan_admits_a_valid_ticket(client, alice_order):
    ticket = held_tickets(client, ALICE)[0]
    resp = scan(client, ticket["qr_token"])
    assert resp.status_code == 200
    assert resp.get_json()["ticket_id"] == ticket["id"]


def test_ticket_cannot_be_scanned_twice(client, alice_order):
    ticket = held_tickets(client, ALICE)[0]
    assert scan(client, ticket["qr_token"]).status_code == 200
    second = scan(client, ticket["qr_token"])
    assert second.status_code == 409
    assert second.get_json() == {"error": "ticket already checked in"}


def test_unknown_code_is_rejected(client):
    assert scan(client, "not-a-ticket").status_code == 404


def test_ticket_for_another_event_is_rejected(client, alice_order):
    ticket = held_tickets(client, ALICE)[0]
    resp = scan(client, ticket["qr_token"], event_id="evt_comedy")
    assert resp.status_code == 409
    assert resp.get_json() == {"error": "ticket is for a different event"}


def test_cancelled_ticket_is_rejected(client, alice_order):
    ticket = held_tickets(client, ALICE)[0]
    client.post(f"/orders/{alice_order['id']}/cancel", headers=ALICE)
    resp = scan(client, ticket["qr_token"])
    assert resp.status_code == 409
    assert resp.get_json() == {"error": "ticket is void"}


def test_scanning_requires_staff(client, alice_order):
    ticket = held_tickets(client, ALICE)[0]
    resp = client.post("/events/evt_jazz/scan", json={"code": ticket["qr_token"]}, headers=ALICE)
    assert resp.status_code == 403


def test_scan_accepts_a_ticket_page_url(client, alice_order):
    ticket = held_tickets(client, ALICE)[0]
    resp = scan(client, ticket["ticket_url"])
    assert resp.status_code == 200
    assert resp.get_json()["ticket_id"] == ticket["id"]


def test_scan_rejects_a_url_that_is_not_a_ticket_page(client, alice_order):
    ticket = held_tickets(client, ALICE)[0]
    resp = scan(client, "https://example.com/t/" + ticket["qr_token"])
    assert resp.status_code == 404
