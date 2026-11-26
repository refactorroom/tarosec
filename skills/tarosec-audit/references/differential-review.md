# Differential source review

Use the supplied diff or confirm the local base and head. Record the revisions
and distinguish committed changes from working-tree edits. Review changes that
can alter trust or authorization first, then follow affected callers, policy
definitions, and regression tests. Mark dependencies or deployment settings the
supplied source cannot establish. Keep existing risks distinct from regressions
introduced by the change.

Read a repository or component `SECURITY_MODEL.md` when available. Use its
stated trust boundaries, invariants, and exclusions as review context. Compare
them with actual enforcement and flag stale or conflicting claims. Read local
Git evidence without fetching or changing branches.

For each serious candidate, locate the most plausible effective guard or counterevidence.
Record the decision with file locations, evidence IDs, and remaining limitations.
Use [OWASP ASVS 5.0.0](https://github.com/OWASP/ASVS/tree/v5.0.0) when a specific
requirement applies. For background see [Trail of Bits differential review](https://github.com/trailofbits/skills/blob/main/plugins/differential-review/skills/differential-review/SKILL.md)
and [Sentry security models](https://github.com/getsentry/skills/blob/main/skills/security-model/SKILL.md).
