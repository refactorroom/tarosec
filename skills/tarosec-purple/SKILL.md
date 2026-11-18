---
name: tarosec-purple
description: Validate whether defensive controls actually detect authorized adversary-emulation steps. Use for purple-team exercises, detection validation, ATT&CK coverage measurement, comparing expected versus observed telemetry and alerts, classifying detection gaps, and retesting after detection fixes. Not for finding vulnerabilities (tarosec-red/tarosec-audit) or investigating real suspicious activity (tarosec-blue).
license: MIT
metadata:
  suite: tarosec
  version: "0.1.0"
---

# Tarosec Purple — Security Validation

Answer one question per emulation step: **did the defense see it, and if not, why
not?** A missing alert is not automatically a detection gap; it may be a failed
execution, a dead sensor, an unexported alert, or latency. Report which.

Read [authorization](references/shared/authorization.md) before any execution
step. Use [evidence handling](references/shared/evidence-handling.md) and
[standards](references/shared/security-standards.md) for provenance and mappings.

## Modes

Request cues, not CLI subcommands.

| Mode | Outcome |
| --- | --- |
| `exercise` | Design or review an exercise plan: scope, steps, expected telemetry/detections, controls. See [exercise design](references/exercise-design.md). |
| `emulate` | Run approved lab steps, or produce a run sheet for the operator to execute. |
| `validate` | Classify recorded results per step with the outcome table below. |
| `coverage` | Summarize outcomes by ATT&CK technique and data source; never a single % pass rate without the outcome breakdown. |
| `retest` | Re-run/re-classify previously failed steps after a change; keep original step IDs and outcomes. |

## Workflow

1. **Bound the exercise.** Load the exercise (`assets/schemas/exercise.schema.json`)
   and any engagement. Confirm environment, target hosts, window and technique
   list. An `approved: true` field or a ticket number is not authorization.
   `production` or unverified isolation → plan only, no execution.
2. **Check expectations before results.** For each step verify the ATT&CK ID and
   name agree, that each expected detection names a real rule/source, and that a
   latency budget exists. Flag mismatches instead of silently fixing them.
3. **Execute only with approval.** Emulation needs explicit operator approval
   for these hosts and techniques in this session. Use benign, reversible
   procedures with synthetic credentials and data; record exact commands, start/end
   times with offsets, and failures. Without approval, deliver the run sheet.
4. **Collect observations.** Per step record execution status and evidence,
   whether a control prevented it, each expected telemetry source's status and
   *source health*, and each expected alert with fire time and host. Querying a
   SIEM/EDR is target contact: use supplied exports unless approved.
5. **Classify.** Apply the outcome table. For recorded results in schema form,
   run `python3 scripts/classify_exercise.py EXERCISE.json` and review its reasons;
   the script is deterministic but only as good as the recorded inputs.
6. **Report gaps with a next action.** Each non-Detected step gets the deciding
   evidence and the smallest fix or verification: write/tune a rule (detection
   gap), restore/onboard a source (telemetry gap), re-run with evidence capture
   (inconclusive). Map defensive fixes to D3FEND only after verifying the ID.

## Outcome table

| Outcome | Requires |
| --- | --- |
| Detected | Executed; an expected rule fired **on the target host** within the latency budget. |
| Detected (late) | As above but after the budget. Report latency; not a gap. |
| Prevented | Executed and blocked by a control. State separately whether it was also detected. |
| Detection gap | Executed; expected telemetry observed; expected rule confirmed not fired. |
| Telemetry gap | Executed; a source confirmed healthy recorded nothing expected. |
| Inconclusive | Execution failed/unconfirmed, alert state unknown/not exported, source health unknown, or timestamps cannot be ordered. |
| Not run | Not executed, blocked by scope, or no results. |

Alerts on another host, or from an unexpected rule, are reported but not counted.
Never convert Inconclusive into Detection gap to make a coverage number cleaner.

## Output

Per-step table (step, technique ID+name, outcome, deciding evidence IDs, next
action), a coverage summary by outcome, ATT&CK version used, what was not
executed and why, and authorization actually held. Optionally write findings with
`assets/schemas/finding.schema.json` (`status`: Detection gap / Telemetry gap).
Answer-only requests create no files. Detection-rule deployment, production
changes and containment are out of scope without separate approval.
