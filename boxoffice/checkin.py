from datetime import datetime

from boxoffice import qr
from boxoffice.errors import BoxofficeError
from boxoffice.models import Store, Ticket


class CheckinError(BoxofficeError):
    pass


def resolve_ticket(store: Store, code: str, event_id: str) -> Ticket:
    """Find the valid ticket for `event_id` behind a scanned code, in either QR format."""
    ticket = store.ticket_by_qr(qr.token_from_scan(code))
    if ticket is None:
        raise CheckinError("unknown ticket", 404)
    if ticket.event_id != event_id:
        raise CheckinError("ticket is for a different event", 409)
    if ticket.status != "valid":
        raise CheckinError("ticket is void", 409)
    return ticket


def scan(store: Store, code: str, event_id: str, now: datetime) -> Ticket:
    """Admit the ticket behind a code scanned at a gate for `event_id`."""
    ticket = resolve_ticket(store, code, event_id)
    if ticket.checked_in_at is not None:
        raise CheckinError("ticket already checked in", 409)
    ticket.checked_in_at = now
    return ticket
