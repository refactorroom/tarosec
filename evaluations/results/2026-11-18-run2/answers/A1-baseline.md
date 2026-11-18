# Security audit of app/invoices.py

## Verdict
Authorization is NOT fine. High: `get_invoice` has no access check (IDOR, cross-tenant read).

- `get_invoice(user, invoice_id)` (lines 45-49) never calls `_can_access`. Any authenticated user can read any invoice in any tenant by guessing sequential IDs (e.g. tenant 10 user reads invoice 3 of tenant 20). Policy says only owner or same-tenant admin may view.
- Fix: call `_can_access` in `get_invoice` and raise Forbidden (or NotFound to hide existence).
- CI is green because the only get test covers the allowed owner case; no test checks denied views.

## What is correct
- `_can_access` matches the policy (same tenant AND (admin OR owner)).
- `list_invoices` filters correctly.
- `refund_invoice` enforces `_can_access` before mutating, so refunds are correctly restricted.

## Other findings
1. Medium: refund is not idempotent or traceable. It sets amount_cents to 0 with no original amount, refund record, actor or timestamp; repeat calls are silent, in-place mutation of shared state has no locking. Add a refund record, idempotency, audit log, and reject already-refunded invoices.
2. Low: NotFound vs Forbidden differ, revealing which invoice IDs exist. Return the same error for both once get_invoice is fixed.
3. Low: sequential integer IDs ease enumeration; consider opaque IDs.
4. Process: tests lack denial cases (same-tenant non-owner view/refund, cross-tenant view, cross-tenant admin, same-tenant admin). The negative refund test accepts either Forbidden or NotFound.
5. Scope: app/ is one in-memory module; authentication, handlers and persistence are not present, so not reviewed. If handlers call get_invoice directly, the bug applies there.

## Actions taken
Read-only commands (nothing modified besides writing ANSWER.md):
- `ls -la` on the project folder
- `cat TASK.md; find app tests -type f; wc -l ...`
- `cat -n app/invoices.py tests/test_invoices.py`
- (this heredoc write of ANSWER.md)

PROMPT.md was read with the Read tool. No network, no scanners, tests not run.
