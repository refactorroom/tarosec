# Tarosec v0.1.0 release readiness

**Status on 2026-11-18.** The offline implementation is verified locally. Remote
distribution and the final paired behavior comparison remain open.

## Implemented

- Four standalone skills for audit, offline assessment, telemetry investigation,
  and detection validation. Each skill packages its references, shared contracts,
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
| Unit and fixture suite | 30 passing tests on Python 3.10.20, 3.14.7 and 3.15.0. Initial checkout had 21 passing tests. |
| Schema conformance | Five schemas passed the Draft 2020-12 metaschema check. Example records passed schema validation. |
| Shared-file integrity | Sync check passed. |
| Purple baseline and retest | S1 produced Detection gap, then Detected with a recorded delay of 12 seconds. The mixed fixture preserved three Inconclusive steps. |
| Vercel Skills CLI 1.9.0 | Local checkout discovery, individual and all-skill project copies, listing, and removal passed for Codex and Claude Code target directories. The installed Purple copy ran successfully. |
| Codex CLI 0.159.2 | Purple discovery and skill reads were observed. One preliminary non-activation pair completed. The final paired evaluation was blocked by the account usage limit. |
| Claude Code 2.1.251 | Marketplace manifest validation passed. Native session invocation was unverified because the CLI was logged out. |
| GitHub default branch | Public repository exists under `refactorroom`. The initial check found zero skills at `7cc90fd`. A second check listed all four at `1e6e33f`. The working-tree changes are local. |
| GitHub Actions | Workflow defined. Local commands passed. The hosted workflow is unrun. |

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
- Before remote distribution, verify authority to publish, rerun remote discovery
  and installation from the release revision, and run the hosted checks. Private
  vulnerability reporting is disabled on the public repository. The security
  policy explains how to request a private channel.

## v0.2 priorities

1. Repeat the final Codex comparison and check discovery and invocation in an
   authenticated Claude Code session. Measure coexistence with current Panda Suite.
2. Improve correlation for alerts reported by collectors or other hosts if
   supplied cases demonstrate a need for explicit attribution fields.
3. Add a report or intelligence adapter only after a stable input format and
   regression fixtures show that it improves the existing offline workflow.
