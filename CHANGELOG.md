# Changelog

## 0.3.0 (unreleased)

- Added `scan-report` to the existing dispatcher. It combines local Semgrep evidence, source review, and an optional sanitized external assessment. Each run saves its effective settings under `.tarosec/reports/`.
- Added an offline quickstart with a local demo rule. Production reviews require rules appropriate to the project.
- Keep Semgrep logs and settings in the run directory so scans can run in a project-scoped agent sandbox.
- Added `run.json` stage records that Report can read from both workspace layouts. Earlier evidence records remain supported.
- Added Audit diff review, optional `SECURITY_MODEL.md` context, and focused tenant isolation, document intake, and agent permission guides. Report marks its assessment confidence unknown for a source finding that claims verification without recording the safeguard review.
- Added Git Issues for sanitized drafts and explicitly authorized publication.

### Upgrading from 0.2.0 or an earlier development build

- Use a trusted local Semgrep rule file by default. If you keep public Registry packs in existing `tarosec.json` settings, pass `--allow-registry` on runs intended to fetch those packs.
- Pass `--update-gitignore` when you want Tarosec to add a project ignore rule. Ordinary and answer-only reviews continue to avoid writing artifacts.

## 0.2.0 (2026-11-18)

- Added Tarosec Report for offline evidence reconciliation, report validation, and baseline/retest comparisons.
- Added deterministic Markdown, JSON, and evidence manifest exports.

## 0.1.0 (2026-11-18)

- Unified Tarosec entry point with specialist availability checks and an offline fallback.
- Standalone simulation skill with a three-scenario catalog, reproducible replay, and evidence reports that feed Purple.
- Four standalone skills for source audit, offline assessment, defensive investigation and detection validation.
- Five versioned record schemas for engagement, finding, evidence, case and exercise data.
- Offline Purple classifier with per-rule evidence, partial detection and inconclusive attribution.
- Prerecorded detection and retest examples, split evaluation fixtures and repository CI checks.
- Project installation through the Agent Skills CLI and a local Claude Code plugin manifest.
- Public npm distribution as `tarosec@0.1.0` and a GitHub Pages project site.
