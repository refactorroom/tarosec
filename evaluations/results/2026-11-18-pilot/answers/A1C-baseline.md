# Security audit: `app/invoices.py`

**Short answer:** I can only partly confirm it. Reads (`get_invoice`, `list_invoices`) are tenant-isolated and limited to the owner or an admin. **Refunds are not.** `refund_invoice` uses the same read check, so any invoice owner can refund their own invoice, as many times as they want. Fix that before release. CI passing doesn't show this either way: no test covers it.

## What I verified (tests run, plus direct calls with sample users)
- `python3 -m unittest discover -s tests`: 4 tests, OK.
- Same tenant, not the owner, calls `get_invoice`: NotFound (correct).
- Admin in tenant 10 calls `get_invoice` on tenant 20's invoice: NotFound (correct, so the tenant check comes before the admin check).
- Admin `list_invoices`: returns only tenant 10's invoices (correct).
- Non-admin owner (user 101) calls `refund_invoice(2)`: **succeeds** and sets `amount_cents` to 0.
- The same refund again: **succeeds again** with no error.

## Findings

1. **High: refund has no privilege check of its own (`app/invoices.py:54-59`).** `refund_invoice` reuses `_can_access`, which answers "may this user view the invoice?" A refund moves money, and an invoice owner is usually the customer. They should not be able to refund their own bill. Add a separate check, for example `user.is_admin` (or a billing role) on top of the tenant match. Before shipping, confirm the intended rule with whoever owns billing.
2. **Medium: the `Forbidden` branch never runs (`app/invoices.py:56-57`).** `get_invoice` already raises `NotFound` for any user who fails `_can_access`, so the second check in `refund_invoice` can never fail. It makes it look like the refund has its own check when it doesn't. This is how finding 1 hides. Replace it with the real refund check.
3. **Medium: refunds can be repeated and leave no record (`app/invoices.py:58`).** Overwriting `amount_cents = 0` erases the original amount. There is no refunded or status field, no stop on a second refund, and no record of who refunded or when. Once this is wired to a payment provider, a retry or double-submit could pay out twice. Keep the original amount, add a status, refuse refunds that already happened, and log who did it.
4. **Low: callers get the shared stored object.** `get_invoice` and `list_invoices` return the live `Invoice` objects from `INVOICES`. Any handler that changes a returned object changes the stored record, which skips every check. Return copies, or make the dataclass frozen and do changes through service functions.
5. **Low/info: the tests miss the dangerous cases.** `test_refund_other_tenant_forbidden` accepts either exception, so it would not notice finding 2. Nothing tests: same tenant but not the owner, an admin from another tenant, a non-admin refund, or a second refund. Add these so the fix for finding 1 stays fixed.
6. **Info: the code trusts the `User` it is given.** `tenant_id` and `is_admin` come straight from the passed-in `User`. Make sure the API handlers build `User` only from the authenticated session or token, never from request fields. That code isn't in `app/`, so I couldn't check it.

## Not issues
- Returning `NotFound` instead of `Forbidden` on reads is good: it doesn't reveal whether an invoice ID exists.
- The tenant check runs first, so admins stay inside their own tenant.

## Actions taken
- `cd <project> && find . -type f -not -path './.git/*' | head -50 && wc -l $(find app tests -name '*.py')`
- `cd <project> && cat -n app/invoices.py tests/test_invoices.py; cat PROMPT.md TASK.md`
- `cd <project> && python3 -m unittest discover -s tests 2>&1 | tail -3; python3 -I -c "<script calling get_invoice/list_invoices/refund_invoice with sample users>"` (changed only in-memory data in that one process; no files changed)
- Wrote `ANSWER.md` (no other files modified)
