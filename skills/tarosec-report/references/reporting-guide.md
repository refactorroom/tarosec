# Reporting modes

Mode names in an agent request are cues. Choose the mode that matches the
deliverable and cite the exact claim, source record, and supporting evidence.

| Mode | What to deliver |
| --- | --- |
| `summary` | Finding counts and their basis, leading risks, coverage limits, and unresolved verification questions. |
| `technical` | Affected components, supported causal analysis, preconditions, impact, evidence, remediation, and a proposed defensive regression check. Use the [technical template](templates/technical.md). |
| `executive` | Business risks, confidence, remediation priorities, and decisions. Use the [executive template](templates/executive.md). |
| `incident` | Recorded chronology, affected assets, classification, alternate explanations, response recommendations, and unknowns. Use the [incident template](templates/incident.md). |
| `coverage` | Per-step outcomes, evidence and control gaps, and an explicitly qualified detection denominator. Use the [coverage template](templates/coverage.md). |
| `remediation` | Prioritized actions, finding IDs, proposed owners where supplied, and verification criteria. Use the [remediation template](templates/remediation.md). |
| `compare` | Explicit baseline and retest IDs, linked steps or findings, comparability, observable changes, and unresolved results. |
| `validate` | Consistency, completeness, provenance and evidence-link review. State separately which sources were inspected and which claims could not be checked. |

Use clear English and adapt the sections to the audience. Include scope,
methodology, limitations, and an evidence appendix when they answer a question.
Skip empty sections. For existing tool exports, inspect the recorded tool
version, revision, exit status, collection window and coverage when available.
Report a stale or failed export and retain any uncertainty about its scope.
Use supplied source metadata to support each timeline or coverage claim.

## Deterministic local bundle

Python 3.10+ helpers use canonical Tarosec case, engagement, evidence, exercise,
finding and simulation-result records. Use a single JSON record or a dedicated
directory of records and artifacts. From the skill directory:

```bash
python3 -B scripts/generate_report.py ./cases --type technical --output ./reports
python3 -B scripts/validate_report.py ./reports/report.json --bundle --input ./cases
```

The helper exports a structured Markdown report, `tarosec.report/v1` JSON, and
an evidence manifest. The audience-specific narrative, source free text,
owners, incident classification, scanner metadata review and remediation advice
belong in the agent's report after it reviews sanitized sources. The CLI has
no input format for those claims beyond the canonical fields. Its technical
and remediation exports provide structured finding and verification facts for
that review.

Choose a new output directory in an existing parent, outside the supplied
inputs. `--overwrite` replaces the three files in an existing Tarosec bundle.
Use `--bundle` to check that all three files match. Generation exits 0 when
the bundle is written, including bundles with gaps. Validation exits 1 for
an inconsistency and 2 for usage or I/O errors. With `--input`, validation
also checks that the supplied records and artifact checks reproduce the report.
Timestamps are opt-in via `--generated-at` and require an explicit offset.

## Comparisons

```bash
python3 -B scripts/generate_report.py ./baseline --type compare --retest ./retest \
  --baseline-id CASE-BEFORE --retest-id CASE-AFTER --output ./comparison
python3 -B scripts/validate_report.py ./comparison/report.json \
  --bundle --input ./baseline --retest ./retest
```

Use separate snapshots when a stable finding ID has different versions. For
two exercise records in the same snapshot, use that directory once and supply
both exercise IDs. Tie the retest to the baseline with `retestOf`. Compare
stable step IDs, target, observations required, environment, and ATT&CK version.
Report a missing or incomparable row as inconclusive. A recorded fix needs a
fixed status and supporting retest evidence. A missing finding in a later
export alone leaves the result inconclusive.
