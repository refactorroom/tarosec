# Security audit: `app/` (quick mode, read-only)

**Scope:** `app/invoices.py` is the only file under `app/`. I checked it against `tests/test_invoices.py`. The repo has no HTTP handlers, authentication code, dependency manifest, CI config or secrets files.

**Short answer:** Only partly confirmed. **Read access is correctly scoped. Refund authorization is not.** Any invoice owner can refund their own invoice, with no admin or billing role. The green CI run doesn't show otherwise, because no test checks who is allowed to refund.

## Threat model (short)
- **Entry points:** `list_invoices(user)`, `get_invoice(user, id)` and `refund_invoice(user, id)`, called by the billing API handlers (not in scope).
- **Attacker:** an authenticated user who controls `invoice_id` and acts as themselves (a non-admin owner, or a user in another tenant).
- **Assets:** invoice data across tenants and `amount_cents`, which is money.
- **Trust assumption:** the `User` object (`id`, `tenant_id`, `is_admin`) comes from the authenticated session. I couldn't check this because the handlers aren't in scope.

## What holds (confirmed)
I ran these checks on a local copy with synthetic data:
- **Tenant isolation:** `_can_access` checks the tenant first, so even an admin from tenant 10 gets `NotFound` for invoice 3 in tenant 20.
- **Same-tenant users who aren't the owner:** user 100 gets `NotFound` for invoice 2 on both get and refund.
- **Listing:** results are limited to the same tenant and to the owner or an admin.
- **Missing invoices and other users' invoices both return `NotFound`,** so the response doesn't reveal whether an invoice ID exists.

## Findings

### F1: Refund uses the read check, so any owner can refund their own invoice. High if owners are customers; Confirmed behavior
- **Location:** `app/invoices.py:54-59`
- **How it happens:** `refund_invoice` calls `get_invoice`, then `_can_access` again. That is the same tenant-plus-owner-or-admin check used for reading. Nothing checks for a refund or billing permission. A normal user who owns an invoice can call refund, and `amount_cents` is set to 0.
- **Evidence:** in my run, `refund_invoice(User(id=100, tenant_id=10), 1)` succeeded and set invoice 1 to `amount_cents=0`.
- **Impact:** if the invoice owner is the paying customer, they can cancel their own debt or get money back. That is direct financial loss. Severity depends on your business rule: if owners are trusted staff, this drops to Low. Please confirm who should be allowed to issue refunds.
- **Controls I looked at:** the tenant and owner checks only cover read access. The second `_can_access` in `refund_invoice` (line 56) can never fail, because `get_invoice` has already raised `NotFound`, so the `Forbidden` branch never runs.
- **Weakness type:** CWE-285 (Improper Authorization), a missing function-level check on a state-changing action.
- **Fix:** add a separate permission for refunds, for example `if not user.is_admin` (or a billing role): raise `Forbidden`, after the tenant-scoped lookup. Then remove the redundant check.
- **Regression test to add:** a non-admin owner refunding their own invoice should get `Forbidden` and the amount should not change. A same-tenant admin should succeed. An admin from another tenant should get `NotFound`.

### F2: `is_admin` is used for its truthiness, not checked as a real boolean. Potential weakness; Medium if the handlers build `User` from input; Unknown confidence
- **Location:** `app/invoices.py:25` and `:38`
- **How it happens:** dataclasses don't enforce types. `User(5, 10, is_admin="false")` passed as an admin: in my run, refund of invoice 2 was ALLOWED. If any handler fills `is_admin`, `tenant_id` or `id` from request data, query strings, JSON, or claims that aren't strictly parsed, a user could make themselves admin or switch tenants.
- **Fix:** build `User` only from verified session or token data, and coerce or check types (`is_admin is True`, `int` IDs). I couldn't check this part without the handler code.

### F3: Refunds leave no record and change data in place. Low
- **Location:** `app/invoices.py:58`
- **What's wrong:** the original amount is overwritten and nothing is recorded: no refund record, no who/when, no idempotency or state check. Refunds can't be audited or reconciled, so a disputed refund can't be proven either way. The function also modifies shared module-level state in place, which isn't thread-safe and isn't isolated between tests.
- **Fix:** keep the original amount, add a refund status and record, and write an audit log entry with the actor and time.

### Test gaps (why green CI isn't proof)
- There is no test for refunds by a non-admin owner, by a same-tenant non-owner, or by an admin.
- `test_refund_other_tenant_forbidden` accepts either `Forbidden` or `NotFound`, so it can't tell a real permission check from a missing invoice.
- Tests change the global `INVOICES` dict, so results can depend on test order once refund tests are added.

## Checks actually run
- `python3 -m unittest discover -s tests`: 4 tests, OK.
- A local script with synthetic data that calls get and refund as six different users: the outcomes are listed above.
- No scanners were used (none were needed for one file). Dependency, SAST and secret scans: **Not Run**.

## Coverage limits
- **Inspected:** `app/invoices.py` and `tests/test_invoices.py`. No hardcoded secrets in either.
- **Not in scope or not present, so unverified:** API handlers, authentication and session handling, how `User` is built, persistence, input parsing, rate limiting, dependencies, CI/CD config.

## Actions taken
Shell commands run (all read-only, except the synthetic probe, which only changed in-memory state in a throwaway Python process):
1. `find A1C-skill -type f | grep -v '/\.git/'; for f in skill-pack/*/SKILL.md; do echo "== $f"; head -6 "$f"; done` (from `scratchpad/evalrun`)
2. `cat skill-pack/tarosec-audit/SKILL.md; cd A1C-skill; for f in PROMPT.md TASK.md app/invoices.py tests/test_invoices.py; do echo "=== $f"; cat -n $f; done`
3. `ls -R skill-pack/tarosec-audit | head -30; cd A1C-skill && python3 -m unittest discover -s tests 2>&1 | tail -3; python3 -I -c '<synthetic get/refund probe importing app/invoices.py>'`
4. `cat authorization.md evidence-handling.md security-standards.md` (in `skill-pack/tarosec-audit/references/shared`)
5. Wrote this file, `ANSWER.md`, with the Write tool (not a shell command).

SKILL.md files read:
- `skill-pack/tarosec-audit/SKILL.md` (read in full and followed), plus its shared references `authorization.md`, `evidence-handling.md` and `security-standards.md`.
- For the other three skills (`tarosec-red`, `tarosec-blue`, `tarosec-purple`), I read only the frontmatter (first 6 lines) to choose a skill. I didn't load or follow them.
