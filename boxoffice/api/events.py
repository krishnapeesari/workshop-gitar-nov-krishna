from flask import Blueprint

from boxoffice import pricing
from boxoffice.api import store
from boxoffice.errors import BoxofficeError
from boxoffice.models import Event

bp = Blueprint("events", __name__)


def event_json(event: Event) -> dict:
    return {
        "id": event.id,
        "name": event.name,
        "venue": event.venue,
        "starts_at": event.starts_at.isoformat(),
        "price_cents": event.price_cents + pricing.SERVICE_FEE_CENTS,
        "face_value_cents": event.price_cents,
        "service_fee_cents": pricing.SERVICE_FEE_CENTS,
        "tickets_left": event.capacity - store().tickets_sold(event.id),
    }


@bp.get("/events")
def list_events():
    events = sorted(store().events.values(), key=lambda e: e.starts_at)
    return {"events": [event_json(e) for e in events]}


@bp.get("/events/<event_id>")
def get_event(event_id: str):
    event = store().events.get(event_id)
    if event is None:
        raise BoxofficeError("event not found", 404)
    return event_json(event)
