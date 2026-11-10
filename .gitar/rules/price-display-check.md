---
title: "Price display check"
description: "Show how each customer-facing price is built when pricing changes"
type: automation
when: "A pull request is opened or updated and changes boxoffice/pricing.py or boxoffice/api/events.py"
actions: "Post a pull request comment headed 'Price display check' with a table of every customer-facing price field the pull request adds or changes"
---

# Price display check

When this pull request changes how prices are calculated or returned, post one
pull request comment headed `Price display check`. Include a table with the
columns Endpoint, Field, What a customer pays per ticket, and All-in (yes, no,
or n/a). A field is all-in only if it equals what checkout charges per ticket,
including every mandatory fee.

Do not add labels. Do not modify code.
