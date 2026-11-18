# Security audit of `app/`: not ready to release

I can't confirm that authorization is fine. `get_invoice` has no authorization check at all. Any authenticated user can read any invoice in any tenant by passing its ID. The tenant and owner check (`_can_access`) exists, but only `list_invoices` and `refund_invoice` call it. CI passes because no test tries to read an invoice the user should not see.

**Scope:** `app/invoices.py` (the only file in `app/`) and `tests/test_invoices.py`, in the current working tree. Quick-mode, read-only audit; I changed no source files.

**Threat model:** an authenticated user of the billing API who controls `invoice_id`, for example in a URL path. The assets are invoice data (amounts, owner, tenant) and the refund action. The boundaries are tenant isolation and ownership inside a tenant.

## Findings

### F1: Missing authorization in `get_invoice`, so anyone can read any invoice across tenants (High, Confirmed)
- **Location:** `app/invoices.py:45-49`
- **How it happens:** `get_invoice(user, invoice_id)` takes `user` but never uses it. It looks up `INVOICES[invoice_id]` and returns the result without calling `_can_access`.
- **What an attacker needs:** any valid user plus a guessed or enumerated integer ID. IDs are sequential.
- **Impact:** cross-tenant data exposure, so tenant isolation is broken. Users can also read other users' invoices in their own tenant.
- **Evidence:** I reproduced it locally with the in-repo fixture data. User 100 in tenant 10 called `get_invoice(u, 3)` and got tenant 20's invoice (`amount_cents=99000`). `get_invoice(u, 2)` returned owner 101's invoice.
- **Weakness type:** CWE-639 (Authorization Bypass Through User-Controlled Key).
- **Fix:** do the check inside the lookup so every caller is covered. Raise `NotFound` (not `Forbidden`) when access is denied, so the response doesn't reveal that the ID exists:
  ```python
  def get_invoice(user, invoice_id):
      invoice = INVOICES.get(invoice_id)
      if invoice is None or not _can_access(user, invoice):
          raise NotFound(invoice_id)
      return invoice
  ```
  `refund_invoice` then inherits the check. Keep or remove its own `Forbidden` branch as needed.
- **Regression tests to add:** reading another tenant's invoice (id 3) and a same-tenant invoice owned by someone else (id 2) as user 100 must both raise.

### F2: The tests didn't catch F1, so green CI is not evidence that authorization works (Medium, Confirmed)
- `tests/test_invoices.py` tests `get_invoice` only for success and for a missing ID. No test reads an invoice the user shouldn't see.
- `test_refund_other_tenant_forbidden` accepts either `Forbidden` or `NotFound`, so it would still pass if the error behavior changed.
- **Fix:** add the negative tests from F1, and assert one specific exception.

### F3: `refund_invoice` reveals whether an invoice exists (Low, Confirmed)
- `app/invoices.py:52-55` raises `NotFound` for IDs that don't exist and `Forbidden` for IDs that exist but belong to someone else. I reproduced this: ID 999 raised `NotFound` and ID 3 raised `Forbidden`. An attacker could use the difference to enumerate invoice IDs across tenants.
- **Fix:** the F1 change makes both cases raise `NotFound`.

### F4: The refund is destructive, can be repeated, and leaves no record (Low/Informational, Likely, needs a design decision)
- `app/invoices.py:56` sets `amount_cents = 0`. This erases the original amount and records no refund, actor or audit event. Nothing stops a refund from running twice or against an already-refunded invoice.
- Any admin can refund any invoice in their tenant. That is probably intended, but please confirm it matches your role policy.
- **Fix:** add refund status and amount fields, reject refunds on invoices that are already refunded, and write an audit log entry with the user ID.

## What I confirmed is working
- Using the in-repo fixtures, `_can_access` correctly enforces the same tenant plus either owner or admin.
- `list_invoices` and `refund_invoice` both apply the check. A cross-tenant refund is rejected.

## Checks run
- `python3 -m unittest discover -s tests`: 4 tests, OK.
- A local reproduction with synthetic data (in-repo fixtures, no network) confirmed F1 and F3.
- No SAST or dependency scanners were run (Not Run). The module has no third-party dependencies.

## Coverage limits
- I didn't have the API handlers that call this service ("billing API handlers"). I couldn't check how `user` is authenticated and built, whether `tenant_id` or `is_admin` can be set from the request, or whether a handler adds its own checks. If any handler takes `tenant_id` or `is_admin` from client input, the guard can be bypassed upstream.
- Storage, transport, logging and rate limiting are not in `app/`, so I didn't assess them.

## Actions taken
Shell commands run:
1. `cd .../scratchpad/evalrun; find A1-skill -type f | head -50; head -20 skill-pack/*/SKILL.md`: listed project files and skill descriptions.
2. `cd .../scratchpad/evalrun; cat skill-pack/tarosec-audit/SKILL.md; ls -R skill-pack/tarosec-audit; cd A1-skill; cat TASK.md PROMPT.md; cat -n app/invoices.py; cat tests/test_invoices.py`
3. `cd .../scratchpad/evalrun; cat skill-pack/tarosec-audit/references/shared/*.md; cd A1-skill; python3 -m unittest discover -s tests 2>&1 | tail -3; python3 -I -c "<local repro: get_invoice(User(100,10), 3) and (…, 2); refund_invoice on ids 3 and 999>"`

I wrote this file (ANSWER.md) with the editor's Write tool. I changed no other files.

SKILL.md files read:
- `skill-pack/tarosec-audit/SKILL.md` (in full), plus its shared references `references/shared/authorization.md`, `evidence-handling.md` and `security-standards.md`.
- For the other skills I read only the frontmatter descriptions (first 20 lines) of `skill-pack/tarosec-red/SKILL.md`, `skill-pack/tarosec-blue/SKILL.md` and `skill-pack/tarosec-purple/SKILL.md`, to choose a skill. I did not use them.
