"""Read what a gate scanner sees on a ticket."""
from boxoffice.models import TICKET_PAGE_URL


def token_from_scan(code: str) -> str:
    """Return the QR token inside a scanned code.

    Older tickets encode the bare token. Tickets from the customer app encode the
    ticket page URL: TICKET_PAGE_URL followed by the token. Any other text comes
    back unchanged, so it fails the ticket lookup like any unknown code.
    """
    return code.removeprefix(TICKET_PAGE_URL)
