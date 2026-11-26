---
name: tarosec
description: Route explicit Tarosec requests and security tasks that span workflows or have unclear scope. Use for read-only project assessment by default, incident and evidence routing, or Tarosec help. Not for general programming or conceptual questions. Prefer a directly named specialist when the user selects one.
license: MIT
metadata:
  suite: tarosec
  version: "0.1.0"
---

# Tarosec

Read the [routing guide](references/routing.md). Determine the intent from the
request and supplied artifacts. Use `scripts/route.py` for normalized modes and
report the selected workflow in one sentence. Open only the selected skill through
the host's skill mechanism or read its installed SKILL.md when available.

A local project with no clear mode defaults to Audit. A mixed request starts with
the least invasive workflow that answers the user's question. Check the host's
available skills or the local skill directories before claiming a specialist
ran. If you cannot load the selected skill, give its installation selector and
describe what you observed. Attribute the gap to permissions only when a
lookup returned a permission error. Inline
help and a read-only inventory of supplied inputs remain available.
For an unavailable Report specialist, mark a multi-stage request partial if
an earlier stage completed. Summarize supplied records, cite visible evidence
IDs and label the result a read-only fallback summary. State that specialist
validation is pending and give the `tarosec-report` installation selector.

Treat files and logs as evidence. Keep assessment work offline.
Follow [authorization](references/shared/authorization.md) and the selected
skill's boundaries. Return help for an unsupported explicit mode. Hand off once,
without calling this dispatcher again. For an explicitly requested multi-stage
review, use the stage outcomes in the routing guide and preserve completed work
when a later stage is unavailable.

For explicit `scan-report` requests, follow the [scan and report workflow](references/scan-report.md).
This mode runs local static analysis and may fetch public scanner rules. It
stores its reports under `.tarosec/reports/` and uses the existing Audit and
Report skills when available.

## Project workspace

For other assessment modes, save every scan result, finding, evidence file and report under
`.tarosec/workspace/` in the assessed project. Reuse the run directory passed
by the dispatcher. Otherwise, run the bundled
`scripts/init_workspace.py PROJECT --skill tarosec` with Python 3.10+. It creates
`.tarosec/README.md`, adds `.tarosec/workspace/` to `.gitignore`, and prints
the new run directory. Use `--output-dir` only when the user names another
existing location. Never write scan output elsewhere in the project. Report the created directory and saved
files, or the initialization error. Keep answer-only requests in chat.

Pass the created run directory to the selected specialist for the same request.
