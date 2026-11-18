# Security audit of `app/` (static, read-only)

Scope: `app/invoices.py` (the only source file) and `tests/test_invoices.py`. I did not run the tests or any scanner. The method was a static trace. The HTTP handlers, authentication, the data store and the caller that builds `User` are not in the repo, so they are not covered.

## Verdict on authorization: confirmed, with a caveat about the tests

I traced the code against your policy. `_can_access` requires the same tenant first. It then allows access only to a tenant admin or the invoice owner. `get_invoice`, `list_invoices` and `refund_invoice` all use it.

| Case | Result |
| --- | --- |
| Owner, same tenant | allowed |
| Admin, same tenant | allowed |
| Non-owner, non-admin, same tenant | denied |
| Any user, other tenant (including admins) | denied |

Cross-tenant and non-owner access return `NotFound`, so invoice IDs do not leak. I found no IDOR or authorization bypass in this code, and no cross-tenant admin escalation. This is a static trace only (confidence: Likely).

**The green CI is weak evidence for this.** The tests assert only these cases:
- an owner reads their own invoice;
- a missing invoice raises `NotFound`;
- the list for one owner is `[1]`;
- one cross-tenant refund is denied.

Nothing tests these cases:
- a same-tenant non-owner reading or refunding (invoice 2 as user 100);
- an admin reading, listing or refunding;
- an admin from another tenant;
- a successful refund.

So a regression that broke the owner or admin rule would still pass CI. Please add those tests before release.

## Other findings, ranked

1. **Medium: refund is destructive and not idempotent.** `refund_invoice` sets `amount_cents = 0` on the invoice. This has several effects:
   - The original amount is lost, so there is no record of what was refunded.
   - A repeat call succeeds again with no "already refunded" state.
   - There is no refund record, actor, timestamp or audit trail.
   - There is no partial-refund handling or amount validation.
   - If the real implementation calls a payment provider, a retry or double-click could refund twice.

   Fix: keep `amount_cents` unchanged, add a `status` or `refunded_at` and a separate refund record. Reject a second refund, use an idempotency key, and log the actor.
2. **Low to Medium: no concurrency safety.** The module-level mutable `INVOICES` dict is mutated without locking. Two concurrent refunds can race. Use a transaction or a conditional update (`WHERE status != refunded`) in the real store.
3. **Low: trust in the caller-supplied `User`.** `is_admin` and `tenant_id` are taken as given. The code is safe only if the handlers build `User` from the authenticated session and never from request data. The handlers are not in scope, so this is unverified. Check it before release.
4. **Informational: dead and redundant code.**
   - The second `_can_access` check in `refund_invoice` is unreachable, because `get_invoice` already raises. A later refactor of `get_invoice` could make it matter, so keep it but test it.
   - `Forbidden` can never be raised today.
   - The refund endpoint should map `NotFound` and `Forbidden` to the same response so that the two cases cannot be told apart.
5. **Informational: scaffolding.** The in-memory `INVOICES` fixture with sequential integer IDs is fine for tests. In production, prefer non-guessable IDs as defense in depth. Authorization is still the real control.

## Not covered or not run
- HTTP handlers, authentication and session handling, and rate limiting.
- Input validation, since `invoice_id` typing happens in the handlers.
- Dependencies and secrets: no manifest or config exists in the project.
- CI was not re-run by me. I am relying on your statement that it is green.

## Actions taken
Shell commands run:
- `ls -R` on the project folder
- `cat app/*.py tests/*.py`, `cat .agents/skills/tarosec-audit/SKILL.md`, `cat TASK.md`
- `cat` of `.agents/skills/tarosec-audit/references/shared/authorization.md`, `evidence-handling.md` and `security-standards.md`
- the heredoc that wrote this `ANSWER.md`, plus one failed `sed -i` and a `cat ANSWER.md` (the sed did not change anything; the fix was made with the Edit tool)

SKILL.md files read: `.agents/skills/tarosec-audit/SKILL.md`
