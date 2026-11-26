# Routing

| Mode or intent | Skill and use |
| --- | --- |
| Project path, scan, audit, source or configuration review | Audit, read-only |
| Explicit `scan-report` | Dispatcher workflow for local Semgrep, Audit, and Report |
| Red, attack surface review | Red, supplied records only |
| Blue, logs, hunting, or incident | Blue for offline triage |
| Purple or detection validation | Purple for recorded observations |
| Simulate, generate events, or replay | Simulate for offline fixtures |
| Verify | Audit for a source fix, Purple for detection retest |
| Intel | Audit for supplied advisory review |
| Report | Report for evidence-backed consolidation, validation, or comparison of supplied records |
| Help | Explain the modes and available skills |

The routing helper accepts a normalized mode. To route natural language, inspect
the requested action and artifact first. For ambiguous verification, use Audit
unless the evidence describes a defensive exercise. Use `--evidence exercise`
for that case. Report when source artifacts are missing. Current intelligence
requires an authorized source lookup and is outside the offline fallback.

Pass the names of specialists that the host exposes to this session as repeated
`--available` flags. Run `python3 scripts/route.py help` (from the skill directory, Python 3.10+) for the contract.
An installed specialist owns the work. For a missing specialist, use the
`installSelector` in the response with the project's Skills CLI source.
An entry-only install can provide a read-only inventory of supplied artifacts,
cite existing records, and help the user choose a workflow.
If Report is missing, give its installation selector and a limited read-only
summary with evidence IDs and gaps. Reserve claims of a complete validated
report for the specialist workflow.

## Multi-stage review

For a request with several required deliverables, inventory supplied records,
confirm scope, then select the needed specialists. Carry the assessment ID,
scope, selected stage, and existing finding and evidence IDs into each handoff.
The dispatcher coordinates handoffs through the host when supported. Otherwise,
give the user the pending stage and its inputs. Specialists work on their own
stage and return observations, evidence references and gaps.

Track each required stage as pending, complete, blocked, or failed. A stage is
complete after its requested output exists and its required checks ran. Mark
the workflow partial when a stage completed but a later one could not. Use
blocked when a prerequisite prevents any assessment stage from proceeding,
and name failed checks and missing evidence explicitly. A limited summary
leaves specialist validation pending. Resume from supplied records after
checking their scope, IDs and remaining prerequisites.

For file-producing runs, `run.json` records `completed`, `partial`, `not_run`,
or `failed` for stages in that workflow. For `scan-report`, preserve the
scanner's recorded state and update `audit` and `report` after each handoff.
A missing specialist leaves its stage `not_run` with `specialist-unavailable`,
even when the dispatcher provides a fallback summary.
