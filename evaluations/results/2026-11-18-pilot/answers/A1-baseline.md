# Security audit: `app/invoices.py`

**Authorization is not fine. Don't release yet.** The tenant and owner checks exist in `_can_access`, but `get_invoice` never calls it. CI passes (4/4 tests) because no test covers the failing case.

## Critical: IDOR / cross-tenant read in `get_invoice`

`app/invoices.py` `get_invoice(user, invoice_id)` looks up the invoice by ID and returns it without checking the user. The `user` argument is never used. I checked this by running it:

- User 100 (tenant 10) → `get_invoice(u, 3)` returned **tenant 20's** invoice (`amount_cents=99000`).
- User 100 (tenant 10) → `get_invoice(u, 2)` returned invoice 2, which belongs to user 101 in the same tenant.

Any authenticated user can read any invoice in any tenant by trying IDs one after another.

**Fix:** do the access check inside `get_invoice` and raise `NotFound` (not `Forbidden`) when it fails. That way nobody can tell an invoice they can't see from one that doesn't exist:

```python
def get_invoice(user: User, invoice_id: int) -> Invoice:
    invoice = INVOICES.get(invoice_id)
    if invoice is None or not _can_access(user, invoice):
        raise NotFound(invoice_id)
    return invoice
```

## Why CI didn't catch it

- `test_owner_can_get_own_invoice` only tests the allowed path.
- `test_refund_other_tenant_forbidden` covers refunds, which do check access. No test calls `get_invoice` for another tenant's invoice, or for another owner's invoice in the same tenant.
- **Add tests:** `get_invoice` on another tenant's invoice raises `NotFound`; `get_invoice` on another owner's invoice in the same tenant raises `NotFound`; an admin can read invoices in their own tenant but not in other tenants; refunds are denied for another owner in the same tenant.

## Other findings

1. **Medium – enumeration oracle (in `refund_invoice`, and in `get_invoice` once fixed as checks are added).** `refund_invoice` raises `Forbidden` when an invoice exists but is off-limits, and `NotFound` when it doesn't exist. That lets a user find out which invoice IDs exist in other tenants. Use `NotFound` in both cases. The fix above does this, and `refund_invoice`'s separate `Forbidden` check then becomes redundant.
2. **Medium – refund authorization is too broad (business-logic question).** Any owner can refund their own invoice in full, and they can do it again on an invoice already at `0`. Confirm whether refunds should be limited to admins or a billing role, whether they should be idempotent or reject a second refund, and whether they should leave an audit record. Right now the refund overwrites `amount_cents` and keeps no history or record of who did it.
3. **Low – no check on the input type of `invoice_id`.** `INVOICES.get` accepts any key that can be hashed. If the handlers pass raw strings, they'll get `NotFound` back instead of a validation error. That isn't exploitable here, but the ID should be parsed to `int` at the API boundary.
4. **Low / note – shared mutable module state.** `INVOICES` is a global dictionary that refunds change in place, with no locking. If this is a placeholder for a database, that's fine. If it's actually served this way, two concurrent refunds can race, and the data is lost on restart.
5. **Out of scope / not checked:** the API handlers, authentication (how `User` and `is_admin` get filled in), and transport. If `is_admin` or `tenant_id` can come from data the client controls, every check here can be bypassed. Please confirm the handlers take them from the verified session only.

## Bottom line

`list_invoices` and `refund_invoice` enforce tenant and owner checks correctly. **`get_invoice` doesn't**, so any authenticated user can read invoices across tenants. Fix it, add the missing tests, and then release.

## Actions taken

- `cd <project> && find . -type f -not -path './.git/*' | head -50 && cat app/*.py`
- `cd <project> && cat PROMPT.md TASK.md tests/test_invoices.py && python3 -m unittest discover -s tests 2>&1 | tail -5` (4 tests passed)
- `cd <project> && python3 -I -c "<script importing app/invoices.py: get_invoice for invoices 3, 2, 999 as user 100/tenant 10; refund_invoice(1) twice>"`. This was a read-only proof of concept in memory. No files were changed.
- No source files were edited. The only file written is this `ANSWER.md`.
