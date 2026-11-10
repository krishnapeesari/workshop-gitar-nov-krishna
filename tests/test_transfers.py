import pytest

from boxoffice.orders import OrderError, cancel_order
from helpers import ALICE, BOB, held_tickets, scan


def transfer(client, ticket_id, to_email, headers=ALICE):
    return client.post(f"/tickets/{ticket_id}/transfer", json={"to_email": to_email}, headers=headers)


def test_holder_can_transfer_a_ticket(client, alice_order):
    ticket_id = alice_order["ticket_ids"][0]
    resp = transfer(client, ticket_id, "Bob@Example.com ")
    assert resp.status_code == 200
    assert resp.get_json() == {"id": ticket_id, "holder_email": "bob@example.com"}
    assert [t["id"] for t in held_tickets(client, BOB)] == [ticket_id]
    assert ticket_id not in [t["id"] for t in held_tickets(client, ALICE)]


def test_transfer_replaces_the_qr_code(client, alice_order):
    ticket_id = alice_order["ticket_ids"][0]
    old_token = next(t["qr_token"] for t in held_tickets(client, ALICE) if t["id"] == ticket_id)
    transfer(client, ticket_id, "bob@example.com")
    new_token = held_tickets(client, BOB)[0]["qr_token"]
    assert new_token != old_token
    assert scan(client, old_token).status_code == 404
    assert scan(client, new_token).status_code == 200


def test_only_the_holder_can_transfer(client, alice_order):
    resp = transfer(client, alice_order["ticket_ids"][0], "carol@example.com", headers=BOB)
    assert resp.status_code == 404


def test_rejects_an_invalid_email(client, alice_order):
    resp = transfer(client, alice_order["ticket_ids"][0], "bob at example")
    assert resp.status_code == 400


def test_cannot_transfer_to_yourself(client, alice_order):
    resp = transfer(client, alice_order["ticket_ids"][0], "alice@example.com")
    assert resp.status_code == 409


def test_cannot_transfer_a_used_ticket(client, alice_order):
    ticket = held_tickets(client, ALICE)[0]
    scan(client, ticket["qr_token"])
    resp = transfer(client, ticket["id"], "bob@example.com")
    assert resp.status_code == 409
    assert resp.get_json() == {"error": "ticket has already been used"}


def test_cannot_transfer_a_void_ticket(client, alice_order):
    client.post(f"/orders/{alice_order['id']}/cancel", headers=ALICE)
    resp = transfer(client, alice_order["ticket_ids"][0], "bob@example.com")
    assert resp.status_code == 409
    assert resp.get_json() == {"error": "ticket is void"}


def test_cannot_transfer_after_the_event_starts(client, clock, alice_order):
    clock.advance(days=40)
    resp = transfer(client, alice_order["ticket_ids"][0], "bob@example.com")
    assert resp.status_code == 409


def test_cannot_cancel_an_order_after_a_ticket_is_transferred(
    client, store, payments, clock, alice_order
):
    order_id = alice_order["id"]
    ticket_id = alice_order["ticket_ids"][0]
    resp = transfer(client, ticket_id, "bob@example.com")
    assert resp.status_code == 200

    order = store.orders[order_id]
    order_before = (order.status, order.total_cents, order.payment_id)
    tickets_before = [
        (t.id, t.holder_email, t.status, t.qr_token, t.checked_in_at)
        for t in store.tickets_for_order(order_id)
    ]

    with pytest.raises(OrderError) as exc:
        cancel_order(store, payments, order_id, order.buyer_email, clock())

    assert exc.value.status == 409
    assert exc.value.message == "order has transferred tickets"
    assert (order.status, order.total_cents, order.payment_id) == order_before
    assert [
        (t.id, t.holder_email, t.status, t.qr_token, t.checked_in_at)
        for t in store.tickets_for_order(order_id)
    ] == tickets_before
    assert all(t.status != "void" for t in store.tickets_for_order(order_id))
    assert payments.refunds == []
