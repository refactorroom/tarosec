# Publication checklist

Before review, record PASS / FAIL / N/A (with reason) for each applicable content
check. A failed safety check blocks publication. Approval is a separate later gate.
Keep this checklist and evidence mapping private.

## Content readiness

- No secrets, credentials, hostnames, internal IPs, customer data or payloads in title, body or linked content.
- No code snippets, line numbers, attack steps, scanner details, local artifact references, per-file lists or self-computed scores.
- Each validated TRUE POSITIVE has a corresponding finding, direction and acceptance criterion. NEEDS REVIEW candidates are qualified; likely false positives are absent or one aggregate line.
- Analyst severities are preserved. No unsupported exploitability, incident or absence-of-incident claim.
- Remediation and verification status are separately supported per finding; unknowns stay unknown. Partial review says "partial coverage, not a clean result".
- Target host/repository and intended create versus update are resolved. Existing matching issues were checked before creation.

## Optional references

- Prefer no paths. For each optional code reference, run from the repository root: `git ls-files --error-unmatch -- <path>` and `git check-ignore --no-index -- <path>`. The first must succeed; the second must return 1 (not ignored). Other errors mean unknown, not safe. Use literal path arguments, not user-supplied glob patterns.
- Tracked does not mean committed: check `git cat-file -e <sha>:<path>` for the exact referenced commit, and inspect for sensitive content. No links to local or staged-only files.
- Code links use a full commit SHA in the intended repository. Local `git branch -r --contains <sha>` is only a hint; confirm the commit/path is accessible on that host before claiming it is pushed. Omit unverifiable links.
- Each public documentation URL was retrieved successfully, follows to an appropriate public destination and explains the fix. HTTP success alone is insufficient; HEAD errors may need a GET check. Omit unreachable or unchecked links and disclose that privately.

## Update readiness

- Existing body is retained exactly; only a dated Update is appended. Existing banned content blocks an edit until a separately authorized resolution is agreed.
- Latest body and state are re-read immediately before writing. Changed content is incorporated and reviewed before approval of a revised result.

## Authorization and completion (after content review)

- Exact destination, operation, title/body and labels shown; session approval covers this specific write. Pending approval is not a content failure.
- Body file matches the approved text. Labels already exist and are approved.
- Write outcome inspected before any retry. Post-write read confirms approved content and preserved history; otherwise report publication unverified.
