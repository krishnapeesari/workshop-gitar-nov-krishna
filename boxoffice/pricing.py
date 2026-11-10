from boxoffice.models import Event

# Per-ticket service fee. Covers card processing and the ticketing platform.
SERVICE_FEE_CENTS = 350


def service_fee_cents(quantity: int) -> int:
    """Service fee for an order of `quantity` tickets."""
    return SERVICE_FEE_CENTS * quantity


def order_total_cents(event: Event, quantity: int) -> int:
    """Amount charged at checkout for `quantity` tickets to `event`, service fee included."""
    return event.price_cents * quantity + service_fee_cents(quantity)
