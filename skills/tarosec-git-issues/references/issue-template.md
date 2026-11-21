# Issue template

Title: `Security: <short plain-language summary>`

```markdown
## Summary
<2-3 sentences: what area is affected and why it matters>

## Findings
- **<Short name>** (Severity: High/Medium/Low) — <one-sentence impact>. Status: <open / proposed fix / mitigated locally, not yet committed / committed, not pushed / remediation status unknown>. Verification: <supported result or not verified>.

## Recommended direction
- <one line per finding: the fix approach in plain words>

## Acceptance criteria
- [ ] <observable outcome, e.g. "Unauthenticated requests to X are rejected">
- [ ] <verification outcome, e.g. "Preview content cannot run scripts">

## Context
<One or two sentences on review type and limits, e.g. "Partial static review; no runtime testing; partial coverage, not a clean result.">

## References (optional)
- <public CWE / OWASP / vendor doc URLs only>
```

## Update block (appended to an existing issue)

```markdown
---
## Update <YYYY-MM-DD>
<what changed, current remediation and verification status; qualify candidates needing review>

- [ ] <remaining next step>
```

## Notes

- Severity is the analyst's severity word from the validated finding; do not
  recompute it.
- One finding per bullet. Keep the whole issue short enough to read in a minute.
- Omit References when no public link explains the fix.
- Optional "reviewed, no action" line for LIKELY FALSE POSITIVE items goes in
  Context, one sentence, no detail.

- For NEEDS REVIEW candidates, say "Needs validation" explicitly and use conditional impact. Do not invent a severity when none was supplied.
- A linked PR alone does not establish merged, deployed or verified status.
