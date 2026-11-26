# Tarosec 0.3.0 release smoke checks

Run on 2026-11-26 against the 0.3.0 release candidate. The host runs used fresh,
disposable projects populated from the local npm tarball. Each project had the
bundled one-rule Python demo and a synthetic external assessment note. The full
projects installed the dispatcher, Audit, and Report. The missing-specialist
project installed only the dispatcher and Audit. No real assessment data was
used in the host runs.

| Check | Observed result |
| --- | --- |
| Linux Python 3.10.22 and 3.14.10 | 70 tests and the shared-file check passed on each version in containers with networking disabled. |
| Offline quickstart, Semgrep 1.186.0 | One target, one demo marker, zero diagnostics. Ran with macOS network access denied. |
| npm and Claude plugin | Local tarball included all eight skills, the demo, and the changelog. Claude plugin validation listed eight skills and passed with the existing missing-icon advisory. |
| Codex CLI 0.171.0, workspace-write sandbox | After the sandbox compatibility fix, created `review.md` and recorded Scan, Audit, and Report as `completed`. |
| Claude Code 2.1.332, Sonnet | With the scanner, record validator, and local hash checks allowed, created `review.md` and recorded Scan, Audit, and Report as `completed`. |
| Claude Code 2.1.332, Report omitted | Created a fallback `review.md`. Scan and Audit were `completed`. Report remained `not_run` with `specialist-unavailable`. |

The first Codex run encountered Semgrep trust-store and home-log permission
errors. The corrected scanner environment uses a readable macOS PEM bundle
when no explicit bundle is set and keeps Semgrep logs and settings in its run
directory. A restricted Claude run produced a report marked `partial` when its
local validation commands were denied. The final Claude smoke allowed only the
additional local checks needed for validation.

Independent checks confirmed the final three native runs' manifest schemas,
evidence records and artifact hashes, the review file, the expected scan alert,
and unchanged demo source and Git ignore state. These are workflow smoke checks.
The paired baseline-versus-skill evaluation for finding accuracy was not run.
