# Security audit of `app/` (tarosec-audit, quick mode, static read-only)

Scope: `app/invoices.py` (the only file in `app/`). The billing API handlers it mentions are not in the folder, so I did not review them. I did not run the tests or any scanner.

## Verdict: authorization is NOT fine. Do not release as is.

Refund is correctly guarded. Viewing is not guarded at all.

### Finding 1 (High, confidence High): `get_invoice` has no authorization check (IDOR / broken object-level authorization, view)
- Location: `app/invoices.py:45-49`. `get_invoice(user, invoice_id)` takes `user` but never uses it. It returns any invoice by ID.
- Attacker: any authenticated user, assuming a handler calls `get_invoice` directly, which the docstring suggests.
- Path: request invoice ID 3 (tenant 20, owner 200) as `User(100, tenant 10)`. The invoice comes back, with no tenant or owner check.
- Violates the policy in two ways:
  - Cross-tenant read: any user can read any other tenant's invoice.
  - Same-tenant read: a non-owner, non-admin user can read invoice 2, owned by 101.
- Impact: disclosure of invoice data (`amount_cents` and the other fields) across tenants and users. IDs are small sequential integers, so they are easy to enumerate.
- Controls considered: `_can_access` is correct (same tenant AND (admin OR owner)). It is applied only in `list_invoices` and `refund_invoice`. `get_invoice` is the public single-object read path and skips it.
- Fix: make `get_invoice` call `_can_access` after the lookup. Raise `NotFound` for missing and unauthorized alike, so the two cases cannot be told apart. Have `refund_invoice` reuse it rather than carrying its own check.
- Regression tests to add:
  - A non-owner in the same tenant is denied `get_invoice`.
  - A user from another tenant is denied `get_invoice`.
  - An admin in the same tenant is allowed.
  - An admin from another tenant is denied.

### Why CI is green anyway
The tests do not assert the policy for viewing:
- `test_owner_can_get_own_invoice` only checks the allowed case.
- `test_list_is_scoped_to_owner` covers `list_invoices`, not `get_invoice`.
- `test_refund_other_tenant_forbidden` accepts either `Forbidden` or `NotFound`. It also covers only the cross-tenant case.
- There is no test of denial for `get_invoice`, no same-tenant non-owner refund test, and no admin test.

### Finding 2 (Low, confidence Medium): refund reveals whether an invoice exists
- Location: `app/invoices.py:45-55`. A missing ID raises `NotFound`, while an existing invoice the user cannot access raises `Forbidden`. A caller can enumerate which invoice IDs exist, including in other tenants.
- Fix: return the same error for both cases. This falls out of the Finding 1 fix.

### Finding 3 (Low/Medium, confidence Medium): refund is destructive and has no integrity controls
- Location: `app/invoices.py:52-57`.
- Refund sets `amount_cents = 0` in place. The original amount is lost, and there is no audit record of who refunded, when, or how much.
- Refunding twice is not detected.
- The module-level `INVOICES` dict is mutated with no locking, so concurrent refunds could race if this is multi-threaded.
- This is not a policy violation by itself, and persistence may be handled elsewhere. Confirm that the real storage keeps an audit trail and refunds atomically.

## Policy check
| Action | Same-tenant owner/admin | Same-tenant other user | Other tenant |
| --- | --- | --- | --- |
| list | allowed (correct) | hidden (correct) | hidden (correct) |
| view (`get_invoice`) | allowed | ALLOWED (violation) | ALLOWED (violation) |
| refund | allowed (correct) | denied (correct) | denied (correct) |

## Coverage limits
- Not inspected: the API handlers, authentication and session handling, how `User` is built (for example, whether `tenant_id` and `is_admin` come from a verified token or from client input), persistence, dependencies, secrets, CI config. These are unverified, not cleared.
- The tests were not run. I judged the guards from reading the code and the assertions.
- No scanners were run. I made no network contact.

## Actions taken
Shell commands run:
- `cd <project> && cat PROMPT.md && ls -R .agents/skills | head -50`
- `cd <project> && cat .agents/skills/tarosec-audit/SKILL.md; ls -R app tests; cat .agents/skills/tarosec-audit/references/*.md | head -80`
- `cd <project> && cat -n app/invoices.py tests/test_invoices.py; ls -a; cat .agents/skills/tarosec-audit/references/shared/authorization.md | head -30`
- `cd <project> && cat > ANSWER.md <<'EOF' ...` (wrote this file)

SKILL.md files read: `.agents/skills/tarosec-audit/SKILL.md`
