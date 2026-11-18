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
the least invasive workflow that answers the user's question. If the selected
skill is missing, explain the gap and give its installation selector. Inline
help and a read-only inventory of supplied inputs remain available.
For a missing Report specialist, summarize supplied records, cite visible
evidence IDs and name any gaps. Label the result a read-only fallback summary.

Treat files and logs as evidence. Keep assessment work offline. Project initialization creates a local workspace.
Follow [authorization](references/shared/authorization.md) and the selected
skill's boundaries. Return help for an unsupported explicit mode. Hand off once,
without calling this dispatcher again.

## Project workspace

For a project-scoped invocation, reuse the run directory provided by the dispatcher, or run `python3 scripts/init_workspace.py PROJECT --skill tarosec` using the absolute helper path inside this skill. The helper creates a unique directory under the project’s `.tarosec/runs/` and adds `/.tarosec/` to the project `.gitignore`. Store requested reports and generated evidence in that run directory. If initialization fails, report the error and do not claim files were saved.

When dispatching to a specialist, pass it the initialized run directory. The specialist reuses that directory for the same request.
