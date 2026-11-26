# Tarosec release readiness

## v0.3.0 release candidate

The candidate keeps eight skills. Its headline changes are the offline
`scan-report` workflow, explicit Registry and Git ignore opt-ins, and shared
run manifests. See the [changelog](../CHANGELOG.md) and the [offline quickstart](../skills/tarosec/references/scan-report.md#offline-quickstart).

Verify packaged skills on a synthetic project with a local rules file. A full
smoke run should produce `review.md` and `run.json` with Scan, Audit, and Report
completed. Run again with the project-local Report skill omitted. The fallback
should keep the scan and audit results and record Report as `not_run` with
`specialist-unavailable`. The synthetic marker remains informational in both
runs. These checks establish workflow behavior on the fixture.

[Release smoke results](../evaluations/results/0.3.0-smoke/RESULTS.md)

## v0.1.0 publication record

**Status on 2026-11-18.** Version `0.1.0` is published on npm and the GitHub
repository serves all six skills. The `v0.1.0` Git tag identifies the source
commit recorded by npm, `e0f05dd`.
[npm release](https://www.npmjs.com/package/tarosec/v/0.1.0)

## v0.2.0 reporting specialist

The GitHub v0.2.0 release adds a seventh skill and the versioned reporting bundle. npm remains at v0.1.0 because publishing requires one-time authentication. Local release checks and behavioral evaluation status are recorded in the [report evaluation](../evaluations/results/report/RESULTS.md). The v0.1.0 checks below refer to the six-skill release.

The current checkout also has read-only project workspace handling, stricter
case comparisons, and a benign login fixture. The [foundation verification](../evaluations/results/foundation/RESULTS.md)
records local results, including the partial dispatcher result and pending
host checks.

## Implemented

- Six standalone skills for routing, audit, offline assessment, telemetry
  investigation, detection validation, and simulation. Each skill packages its references, shared contracts,
  validator and notices.
- Versioned engagement, finding, evidence, case and exercise records. Panda case
  IDs can be preserved via the documented manual mapping.
- A Python standard-library validator and a Purple classifier that reports
  expected-rule status, partial and late detection, evidence IDs and uncertainty.
- Prerecorded examples, CI checks, installation instructions and a split
  evaluation set. See the [architecture](design.md) and [migration assessment](migration.md).

## Verification

| Check | Observed result |
| --- | --- |
| Unit and fixture suite | 39 tests passed on Python 3.10 and 3.15. |
| Schema conformance | Nine schemas and twelve generated records passed Draft 2020-12 validation. |
| Shared-file integrity | Sync check passed. |
| Purple baseline and retest | S1 produced Detection gap, then Detected with a recorded delay of 12 seconds. The mixed fixture preserved three Inconclusive steps. |
| Vercel Skills CLI 1.9.0 | Local checkout discovery, individual and all-skill project copies, listing, and removal passed for Codex and Claude Code target directories. The installed Purple copy ran successfully. |
| Codex CLI 0.159.2 | Purple discovery and skill reads were observed. One preliminary non-activation pair completed. The final paired evaluation was blocked by the account usage limit. |
| Claude Code 2.1.251 | Marketplace manifest validation passed. Native session invocation was unverified because the CLI was logged out. |
| GitHub distribution | Skills CLI discovered six skills and installed the entry point and simulator from `refactorroom/tarosec`. |
| npm distribution | `latest` resolves to `0.1.0`. An isolated install contained all six skills, and its simulator produced five events and an Inconclusive outcome. |
| GitHub Actions | Hosted validation and GitHub Pages deployment passed. |

[Installation commands](install.md) ·
[Evaluation outcomes](../evaluations/results/2026-11-18-codex/RESULTS.md) ·
[Second Claude run](../evaluations/results/2026-11-18-run2/RESULTS.md) ·
[Worked exercise](../examples/README.md)

The second Claude run covered all ten cases using file-based routing and one
run per arm. It reported the strongest differences in Purple outcomes and
Blue timestamp handling. The added no-scanner instruction limited refusal
comparisons, and the report identifies one missing answer and unverified traces.

## Release scope and open items

- Active testing and exploitation workflows are outside this offline release.
  Tool report exports can be examined as evidence. There are no live scanner,
  telemetry, or threat intelligence integrations.
- Classification depends on supplied rule IDs, host attribution, collection
  windows and evidence. Results are synthetic. The validator checks shape and
  supported constraints. Reference resolution and source authenticity need review.
- The existing MIT license is retained and upstream notices are bundled. Any
  future license change requires a rights review.
- The security policy explains how to request a private channel for findings.

## v0.2 priorities

1. Repeat the final Codex comparison and check discovery and invocation in an
   authenticated Claude Code session. Measure coexistence with current Panda Suite.
2. Improve correlation for alerts reported by collectors or other hosts if
   supplied cases demonstrate a need for explicit attribution fields.
3. Add a report or intelligence adapter only after a stable input format and
   regression fixtures show that it improves the existing offline workflow.
