from datetime import datetime

from boxoffice import pricing
from boxoffice.errors import BoxofficeError
from boxoffice.models import Order, Store, Ticket, new_qr_token
from boxoffice.payments import FakePayments

MAX_TICKETS_PER_ORDER = 8


class OrderError(BoxofficeError):
    pass


def place_order(
    store: Store, payments: FakePayments, event_id: str, buyer_email: str, quantity: int, now: datetime
) -> Order:
    """Charge the buyer and issue their tickets."""
    event = store.events.get(event_id)
    if event is None:
        raise OrderError("event not found", 404)
    if now >= event.starts_at:
        raise OrderError("event has already started", 409)
    if not 1 <= quantity <= MAX_TICKETS_PER_ORDER:
        raise OrderError(f"quantity must be between 1 and {MAX_TICKETS_PER_ORDER}", 400)
    if store.tickets_sold(event.id) + quantity > event.capacity:
        raise OrderError("not enough tickets left", 409)

    total = pricing.order_total_cents(event, quantity)
    order = Order(
        id=store.next_id("ord"),
        event_id=event.id,
        buyer_email=buyer_email,
        total_cents=total,
        payment_id=payments.charge(buyer_email, total),
    )
    store.orders[order.id] = order
    for _ in range(quantity):
        ticket = Ticket(
            id=store.next_id("tkt"),
            order_id=order.id,
            event_id=event.id,
            price_cents=event.price_cents,
            holder_email=buyer_email,
            qr_token=new_qr_token(),
        )
        store.tickets[ticket.id] = ticket
    return order


def cancel_order(store: Store, payments: FakePayments, order_id: str, buyer_email: str, now: datetime) -> Order:
    """Cancel a paid order before its event starts.

    Refunds the buyer the full order total and voids every ticket on the order.
    Orders with a checked-in or transferred ticket can't be cancelled.
    """
    order = store.orders.get(order_id)
    if order is None or order.buyer_email != buyer_email:
        raise OrderError("order not found", 404)
    if order.status != "paid":
        raise OrderError("order is already cancelled", 409)
    if now >= store.events[order.event_id].starts_at:
        raise OrderError("event has already started", 409)
    tickets = store.tickets_for_order(order.id)
    if any(t.checked_in_at is not None for t in tickets):
        raise OrderError("order has checked-in tickets", 409)
    if any(t.holder_email != order.buyer_email for t in tickets):
        raise OrderError("order has transferred tickets", 409)

    payments.refund(order.payment_id, order.total_cents)
    for ticket in tickets:
        ticket.status = "void"
    order.status = "cancelled"
    return order
