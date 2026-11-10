from datetime import datetime, timezone

from boxoffice import pricing
from boxoffice.models import Event


def make_event(price_cents: int) -> Event:
    return Event("evt_x", "X", "Hall", datetime(2026, 11, 14, tzinfo=timezone.utc), price_cents, capacity=10)


def test_service_fee_is_charged_per_ticket():
    assert pricing.service_fee_cents(1) == 350
    assert pricing.service_fee_cents(4) == 1400


def test_order_total_is_face_value_plus_fees():
    assert pricing.order_total_cents(make_event(5000), 2) == 10700
