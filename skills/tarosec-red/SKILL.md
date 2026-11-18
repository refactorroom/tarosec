---
name: tarosec-red
description: Perform authorized offensive security work — map attack surfaces and asset inventories, plan and run scoped reconnaissance or vulnerability validation in approved environments, and prepare bug bounty evidence. Use for engagement-scoped recon, exposed-service assessment, lab exploitation of a known finding, and bounty report preparation. Not for source code audits (tarosec-audit), log investigation (tarosec-blue), or detection validation (tarosec-purple).
license: MIT
metadata:
  suite: tarosec
  version: "0.1.0"
---

# Tarosec Red — Offensive Security

Find and validate weaknesses **only** inside explicit, current authorization.
Read [authorization](references/shared/authorization.md) before anything that
contacts a target, plus [evidence handling](references/shared/evidence-handling.md)
and [standards](references/shared/security-standards.md).

## Modes

| Mode | Outcome |
| --- | --- |
| `recon` | Asset inventory and attack surface from supplied material; passive by default. |
| `scan` | Plan or (with approval) run scoped scans; record tool, version, args, exit status. |
| `simulate` | Reproduce a hypothesized weakness in a lab with a negative/control pair. |
| `bounty` | Program-bound, sanitized report draft. No submission or target contact without approval. |
| `validate` | Re-check a finding (own or from `tarosec-audit`) against its invariant. |

## Workflow

1. **Scope.** Load the engagement (`assets/schemas/engagement.schema.json`).
   Exact targets, exclusions, techniques, window, budgets, stop conditions. The
   file narrows scope; it never grants it. Discovered hosts, subdomains or
   redirects are **new** targets: list them, don't touch them. See
   [scope rules](references/scope.md).
2. **Reuse, don't re-scan.** Consume `tarosec-audit` findings for source-level
   issues instead of re-deriving them; Red adds reachability and runtime validation.
3. **Validate minimally.** State the invariant, expected behavior, smallest
   negative test and a safe control. Synthetic accounts and data; no denial of
   service, credential attacks, persistence or third-party data access. Stop on
   any stop condition and keep what was collected.
4. **Record execution honestly.** A tool that failed, timed out or was not
   installed is Not Run, never "no findings". Never claim a scan ran because a
   tool exists.
5. **Report.** Findings (`assets/schemas/finding.schema.json`, `producer:
   tarosec-red`) with claim strength (`static-trace` vs `lab-reproduction`),
   reproduction steps that are safe to re-run, impact bounded to what was shown,
   remediation and regression check. Bounty drafts never claim eligibility,
   novelty or payout.

Ready-made emulation for detection testing belongs to `tarosec-purple`; Red
supplies the technique and procedure, Purple owns the expected-vs-observed
comparison.
