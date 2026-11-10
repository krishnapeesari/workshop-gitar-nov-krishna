# All-in ticket prices

Every price we show a customer is the all-in price: face value plus every
mandatory fee. Checkout must never charge more than the price we listed.

In any customer-facing response, `price_cents` must include all mandatory
per-ticket fees. Fees may be itemized in addition, but never added on top of a
lower headline price. Report a violation as an Important finding even when the
tests pass, and keep reporting other issues as usual.
