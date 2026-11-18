# Release triage: this is not a clean scan

**Verdict: Not Run / no evidence of safety. Do not treat this as a clean dependency scan. Hold any "dependency-clean" sign-off until a real scan runs.**

## Why
- `report.json` has an empty `findings` list, but the scanner never ran. `scannerStatus` is `binary_missing` and `exitCode` is 127 (command not found). An empty list from a scanner that did not execute means nothing was checked, not that nothing was found. This is a coverage gap.
- The report is stale and for a different revision. It is dated 2026-10-04 and covers revision `fixture-old`. The resolved dependencies are for `fixture-current`, so the report was not produced against what would ship.
- The package version differs. The report says `example-parser` 2.1.0. The resolved set has 2.2.0.
- `resolved-dependencies.json` has `advisoriesIncluded: false`. It lists versions only, with no advisory data, so nothing can be compared with the resolved version.
- The report lacks tool name and version, the command run, the ecosystem, and the scanned lockfile. Those can't be recorded from the inputs.

## Triage status
| Item | Status |
| --- | --- |
| Scanner execution | Not Run (exit 127) |
| Advisories against resolved 2.2.0 | Unverified |
| Affected, reachable and exploitable status | Unknown |
| Advisory IDs, KEV and EPSS | Unverified. The workspace is offline and no dated source was supplied. |

I found no vulnerability, and none was ruled out either. The absence of findings reflects a failed scan, not a safe package.

## Before release
1. Install or fix the scanner and re-run it against the current lockfile and revision (`fixture-current`, `example-parser` 2.2.0). Record tool, version, date, command and exit status.
2. Include advisory data and check `example-parser` 2.2.0 against an authoritative source (OSV, GHSA, NVD or the vendor) once network use is approved.
3. Check dependency path, dev-only versus runtime use, and reachability for any hit.

I installed nothing, ran nothing and changed no files other than this answer.

## Actions taken
Shell commands run:
- `cd <project folder> && cat PROMPT.md && ls -R .agents/skills | head -50`
- `cd <project folder> && ls -la && cat report.json && cat resolved-dependencies.json && cat .agents/skills/tarosec-audit/SKILL.md`
- `cd <project folder> && cat TASK.md; cat .agents/skills/tarosec-audit/references/dependencies.md`
- `cd <project folder> && cat > ANSWER.md` (writing this file)

SKILL.md files read:
- `.agents/skills/tarosec-audit/SKILL.md`

Also read, though it is not a SKILL.md: `.agents/skills/tarosec-audit/references/dependencies.md`.
