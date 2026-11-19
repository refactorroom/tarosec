# Tarosec foundation verification

## Gaps and changes

The starting suite passed 56 tests. The shared initializer still wrote the
target's ignore file and rejected the Report skill name. Report comparison
accepted both a finding ID reused by another producer and previously seen
evidence bytes relabelled with a different ID. The login fixture catalog
provided the suspicious pattern without a matched benign retry control.
The dispatcher covered a single route and left multi-stage completion rules
implicit.

| Area | Changed files and contract |
| --- | --- |
| Workspace | `scripts/init_workspace.py` and all seven synchronized copies create one private directory outside the resolved project and return its path on stdout. All seven skill names are accepted. Answer-only requests stay in chat. |
| Skill guidance | The seven `SKILL.md` entry points, `skills/tarosec/references/routing.md`, and Report's reporting guide clarify when to write output, retain IDs, report gaps, and check evidence. |
| Reporting | `skills/tarosec-report/scripts/report_model.py` checks producer identity and requires a new evidence ID with different hash-matched bytes for a recorded fix or regression. Content review is still needed to verify that the evidence demonstrates the change. |
| Simulation | `skills/tarosec-simulate/assets/scenarios/auth.benign-login-retry/` adds a deterministic comparison input with two failed attempts followed by a successful login. |
| Regression and documentation | `tests/test_workspace.py`, `tests/test_report.py`, and `tests/test_simulation.py` cover the changed helpers. W1 and T3 use the existing blind fixture and reviewer-key layout. The README, design, simulation, release-readiness and evaluation docs describe the changes. |

The canonical schemas and mode names retain their existing versions. The
dispatcher passes the same external directory and supplied assessment, finding
and evidence IDs through a handoff. Specialists remain independently usable.
The lifecycle guidance records per-stage outcomes in the response. Persisted
state and enforcement of lifecycle transitions are pending. Existing project
run directories remain usable as supplied evidence. Scripts that assumed an
in-project destination should consume the initializer's stdout. Previously
generated reports can still receive structural validation. Source recomputation
can disagree with a historic comparison whose assessment changes under the
new evidence rules.

## Skill matrix

| Skill | Existing work | This iteration | Verification and limits |
| --- | --- | --- | --- |
| Tarosec | Offline routing, help, missing-specialist summary | Stage outcomes and ID-preserving handoff guidance, external workspace | T3 exercised a missing Report stage. Persisted workflows and custom host handoff support remain untested. |
| Audit | Quick, deep, dependencies, agents and verify | Read-only default, coverage table, and explicit finding/revision/evidence checks for verification | W1 and workspace tests. Shared machine-readable coverage remains pending. |
| Red | Offline inventory, scope and supplied evidence review | External output follows the shared workspace rules | Bundled helper exercised. Offline scope behavior has existing fixtures. |
| Blue | Hunt, triage, timeline, detection and monitoring review | Guidance for citing correlation keys and handling missing or conflicting keys | Bundled helper exercised. Behavioral comparison of correlation guidance deferred. |
| Purple | Exercise and retest classification | Guidance for identifying generation, event observation and alert evidence independently | Existing classifier regressions passed. New guidance awaits behavioral comparison. |
| Simulate | Catalog generation and sanitized replay | Matched benign retry control | Reproducibility and hash checks passed across all four catalog entries. The control has no detector export. |
| Report | Consolidation, validation, audience views and comparisons | Rejects cross-producer remediation matches and aliased bytes as retest evidence | Positive and negative test controls passed. Richer lifecycle and verification record semantics remain pending. |

## Deterministic verification

| Check | Result |
| --- | --- |
| Baseline, Python 3.15 | 56 passed, zero failed or skipped. Shared files in sync. |
| Regression probes on prior code | Four workspace assertions failed as expected. Two comparison subcases incorrectly returned `recorded-fix`. The benign catalog case failed because its ID was absent. The independent retest positive control passed. |
| Updated suite | 60 passed on Python 3.14 and 60 passed on Python 3.15. Zero failures or skips in either run. |
| Sync and formatting | `scripts/sync_shared.py --check` and `git diff --check` passed. |
| Schemas | Draft 2020-12 checked all ten canonical schemas and twenty example/generated records. |
| Skill format and packaging | Agent Skills reference validator passed all seven directories. Skills CLI 1.9.0 copied all seven skills for Codex and Claude Code into a disposable project. All 14 installed workspace helper invocations succeeded outside the target tree. The npm dry run included seven entry points and the benign fixture. |
| Claude manifest | Claude Code 2.1.327 validated the manifest and reported an existing plugin icon warning. A native Claude conversation was not run. |

Python 3.10 and Windows were not run for this iteration. The hosted CI matrix,
published packages, and additional agent hosts were not part of these checks.

## Behavioral evaluation

Eight fresh local Codex CLI 0.170.0 sessions used gpt-6.1-sol with low reasoning
effort. Each case used identical fixture inputs across its arms. The skill arm
had the relevant repository skill copies, while the baseline had no Tarosec
workspace copy. W1 included the prior Audit copy from `97089c9` as a third arm.
The same host configuration applied to all arms. Native user-level metadata
may still be visible, so the baseline controls for the workspace copy only.
The preflight allowed fixture reads and denied reviewer-key reads, fixture
writes, and loopback binding. All eight processes exited successfully.
Fixture hashes and file inventories were identical before and after each run.

| Case | Baseline | Skill | Follow-up |
| --- | --- | --- | --- |
| W1, answer-only audit | Pass. Reviewed both fixture files and made no workspace writes or initialization calls. | Pass. Read the Audit skill and both files. Made no workspace writes or initialization calls. | The prior Audit arm also passed. The observed change is in the helper contract. This single stress case shows no behavioral gain. |
| T3, missing Report stage | Partial. Kept all IDs and left validation pending. Omitted the selector and attributed the gap to permissions without a recorded lookup error. | Partial. Kept all IDs and labelled the fallback. Omitted the selector and also attributed the gap to permissions. | The revised dispatcher arm used the routing guide and helper, marked the workflow partial, and named the selector. It still incorrectly attributed the reported `missing` result to a permission denial. |
| N1, conceptual non-activation | Pass. Answered in two sentences with no tool calls. | Pass. Answered in two sentences with no tool calls. | No observed activation in either arm. |

[Executed commands and responses](runs.json) retain the initial and follow-up
results. Git checks in W1 were limited by the sandbox. Its read-only profile
would have blocked writes in either arm, so the traces were checked for
attempted initialization as well as filesystem changes. These are single-run
comparisons. They do not establish suite-wide behavioral improvement or
context savings. Other behavioral cases were **Not Run** in this iteration.

## Remaining work

1. High. Retest the dispatcher against distinct missing and permission-denied
   specialist fixtures. Anchor the explanation to the observed lookup result.
2. Medium. Define a shared coverage record and explicit remediation provenance
   before adding lifecycle transitions or report closure claims. Exercise both
   incomplete coverage and supplied positive retest evidence.
3. Medium. Evaluate multi-stage continuity and the Blue and Purple guidance
   in native hosts. Record a reproducible trace before claiming integration
   support or behavioral improvement.
4. Lower. Add more inert telemetry controls only where an evaluation question
   requires them. The recent negative control covers the login sequence.
