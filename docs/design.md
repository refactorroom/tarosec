# Architecture

Tarosec has four independently installable skills. Each has a short entry point,
task-specific references and a copy of the shared files. Agents read the skill
and the relevant references on demand. There is no service to start.

## Inputs and outputs

| Skill | Trigger and inputs | Output |
| --- | --- | --- |
| Audit | A security question about source, configuration, lockfiles, CI or agent integrations | Evidence-backed findings and coverage limits |
| Red | A scope or exposure question about supplied asset lists, engagement records or scan reports | Offline inventory, scope decisions and assessment evidence |
| Blue | A question about supplied logs, alerts, indicators or detection rules | Timeline, classification, alternate explanations and gaps |
| Purple | A question about whether a recorded or synthetic exercise produced expected observations | Per-step outcomes, deciding evidence and retest status |

General security explanations need no Tarosec workflow. Audit can pass a finding
ID to Red for corroboration. Blue can supply telemetry provenance or a rule
observation to Purple. Purple can return a detection or telemetry finding for
follow-up. Skills exchange records and IDs without invoking each other.

## Record contracts

Canonical JSON Schemas are in [schemas](../schemas). The record's
`schemaVersion` uses `tarosec.<kind>/v1`. Each schema has a unique URN.

| Record | Contents |
| --- | --- |
| Engagement | Responsible authority, listed assets, exclusions, time window, budgets and evidence handling |
| Finding | Stable ID, producer, confidence, severity, claim strength, evidence, impact, remediation and verification |
| Evidence | Artifact provenance, collection time, original timezone, optional hash and custody |
| Case | References to assets, findings, evidence, exercises and activities |
| Exercise | Expected observations per step, recorded observations, evidence and optional retest linkage |

The bundled validator checks field shape and supported JSON Schema constraints.
Cross-file references, coverage of an alert export, timestamps, scope and
authorization need review. Use IDs to cite evidence and keep raw artifacts in the
authorized evidence root. The classifier reads one exercise record and reports
outcomes with reasons and referenced evidence IDs.

Shared references, schemas, licenses and the validator are built into each skill
by `scripts/sync_shared.py`. The drift check ensures independent installs get
the same contracts.

## Execution and adapters

Python helpers parse local files and write diagnostics or results to stdout.
Supplied text and record fields are data. The helpers launch no external
processes and make no network requests. Host permissions control what the agent
can read and run. Keep tests on synthetic evidence and use bounded, isolated
tool permissions when checking safety behavior.

| Potential input or integration | v0.1 decision |
| --- | --- |
| Semgrep, Gitleaks, Trivy, OSV-Scanner | Review supplied report, tool version, exit status and scan coverage. Record supported findings and gaps. |
| Network scanner reports | Review supplied scope and exported inventory or scan metadata offline. |
| Zeek, Suricata, Sigma and SIEM exports | Read supplied evidence and document schema, coverage and time windows. Use recorded controls for detection verification. |
| Benign simulation | Read prerecorded marker and alert data. No emulation platform is required. |
| Panda Suite, Invaris, Evaris and Itervyn | Optional workflow companions. Integration depends on a verified interface and a demonstrated case for it. |

Any future report adapter needs a bounded supported format, provenance, failure
handling, redaction tests and versioned fixtures. Threat intelligence starts
with exact resolved versions and authoritative vendor or ecosystem records.
Record source and retrieval date, explain disagreement, and label status as
affected, not affected, unknown or unverified. Use locally supplied advisories
when network research is unavailable.

## Future skills

| Skill | Extract when |
| --- | --- |
| `tarosec-intel` | Dated advisory reconciliation and prioritization require their own inputs, outputs and routing tests |
| `tarosec-incident` | A full incident lifecycle, custody and handoff repeatedly exceed Blue triage |
| `tarosec-threat` | Repeated design reviews need a dedicated trust-boundary and abuse-case workflow |
| `tarosec-posture` | Baseline checks across infrastructure or cloud need distinct inventories and evidence |

Before adding a trigger, compare it with the closest existing workflow on
routing and outcome quality. Prioritize host and case evaluation before new integrations.
