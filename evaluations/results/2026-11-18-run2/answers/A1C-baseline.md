# Audit of `app/invoices.py`

Scope: only `app/invoices.py` (59 lines) and `tests/test_invoices.py` exist. The billing API handlers, authentication, and the payment processor are not in the folder, so I could not audit them. I read the code only and ran nothing, including the tests.

## Authorization: confirmed against the policy
`_can_access` requires the same tenant first, then `is_admin` or `owner_id == user.id`. That matches the policy.
- `list_invoices`, `get_invoice` and `refund_invoice` all go through that check.
- `refund_invoice` calls `get_invoice` first, so refund has the same gate as view.
- A cross-tenant admin is denied, because the tenant check comes before the admin check.
- A same-tenant non-owner who is not an admin is denied for both view and refund.
- Denied access raises `NotFound`, not `Forbidden`. That is a reasonable choice because it avoids leaking which invoice IDs exist.
- I found no IDOR or tenant-bypass in this file.

## Other findings
1. **Medium - The refund only zeroes the amount.** `refund_invoice` sets `amount_cents = 0`.
   - The original amount is destroyed. There is no refund record, no refunded amount, no status and no timestamp.
   - There is no call to a payment processor, so no money moves in this code.
   - A second refund call succeeds silently, so it is not idempotent. Fix this by adding a `status` or `refunded_cents` field and rejecting a second refund with a 409.
2. **Medium - There is no audit logging.** Nothing records who refunded which invoice, or who was denied. Refunds are a sensitive action and should be logged.
3. **Low - There is no concurrency control.** The data is a global in-memory dict, and the check and the mutation are not atomic. This matters once it is backed by a real store, where it would allow a double refund.
4. **Low - The `Forbidden` branch in `refund_invoice` is unreachable.** It repeats the check that `get_invoice` already made. It is harmless, but it suggests the code is not behaving the way the author expects. The test's `assertRaises((Forbidden, NotFound))` hides this.
5. **Low - The tests do not support the "authorization is fine" claim.** Green CI proves little here.
   - Only the owner-view, missing-invoice, owner-list and cross-tenant-refund cases are covered.
   - Missing: admin view and refund, same-tenant non-owner denied for view and refund, a cross-tenant admin, a successful refund, and a double refund.
   - Add these cases before release.
6. **Info - Unverified assumption.** Authorization trusts the `User` object (`id`, `tenant_id`, `is_admin`). If a handler builds it from request input rather than a verified session or token, the checks do nothing. Please review the handlers, because that is where the real risk is.

## Verdict
The authorization logic itself is correct for the stated policy. I would not call the release fully audited until the refund semantics (finding 1), logging, tests and handler-side identity are addressed or accepted.

## Actions taken
- `cd` into the project folder and `find`/`wc` to list the files
- `cat` of `TASK.md`, `app/invoices.py` and `tests/test_invoices.py`
- This `cat > ANSWER.md` heredoc to write the answer
