"""Ticket transfers: the holder of a ticket hands it to someone else.

The recipient becomes the holder and gets a new QR code, so the old one stops
working at the gate. The order, and its receipt, stay with the original buyer.
"""
import re
from datetime import datetime

from boxoffice.errors import BoxofficeError
from boxoffice.models import Store, Ticket, new_qr_token

EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


class TransferError(BoxofficeError):
    pass


def transfer_ticket(store: Store, ticket_id: str, holder_email: str, to_email: str, now: datetime) -> Ticket:
    """Make `to_email` the holder of a ticket that `holder_email` currently holds."""
    ticket = store.tickets.get(ticket_id)
    if ticket is None or ticket.holder_email != holder_email:
        raise TransferError("ticket not found", 404)
    to_email = to_email.strip().lower()
    if not EMAIL_RE.fullmatch(to_email):
        raise TransferError("enter a valid email address", 400)
    if to_email == holder_email:
        raise TransferError("you already hold this ticket", 409)
    if ticket.status != "valid":
        raise TransferError("ticket is void", 409)
    if ticket.checked_in_at is not None:
        raise TransferError("ticket has already been used", 409)
    if now >= store.events[ticket.event_id].starts_at:
        raise TransferError("event has already started", 409)

    ticket.holder_email = to_email
    ticket.qr_token = new_qr_token()
    return ticket
