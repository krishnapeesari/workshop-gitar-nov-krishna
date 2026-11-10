from flask import Blueprint, g, request

from boxoffice.api import now, store
from boxoffice.auth import require_customer
from boxoffice.models import TICKET_PAGE_URL, Ticket
from boxoffice.transfers import transfer_ticket

bp = Blueprint("tickets", __name__)


def ticket_json(ticket: Ticket) -> dict:
    return {
        "id": ticket.id,
        "event_id": ticket.event_id,
        "status": ticket.status,
        "checked_in": ticket.checked_in_at is not None,
        "qr_token": ticket.qr_token,
        "ticket_url": TICKET_PAGE_URL + ticket.qr_token,
    }


@bp.get("/me/tickets")
@require_customer
def my_tickets():
    return {"tickets": [ticket_json(t) for t in store().tickets_held_by(g.principal.email)]}


@bp.post("/tickets/<ticket_id>/transfer")
@require_customer
def transfer(ticket_id: str):
    body = request.get_json(silent=True) or {}
    ticket = transfer_ticket(store(), ticket_id, g.principal.email, str(body.get("to_email", "")), now())
    return {"id": ticket.id, "holder_email": ticket.holder_email}
