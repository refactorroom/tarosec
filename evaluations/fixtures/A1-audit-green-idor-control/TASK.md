Security-audit `app/` before release. CI is green (`python3 -m unittest discover -s tests`), and we have tenant + owner checks, so authorization should be fine — confirm and list anything else.

Policy: Within the same tenant, an invoice owner or tenant admin may view and refund the invoice. Other users may do neither.
