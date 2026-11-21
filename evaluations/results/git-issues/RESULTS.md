# Git Issues skill review — 2026-11-21

## Purpose and evidence boundary

Improve high-level publication of supplied validated security findings while
preserving evidence qualification, source privacy and authorized issue history.
This capability is distinct from Audit (validation), Blue (investigation), Report
(consolidation) and ordinary Git operations. A separate publication trigger is
reasonable; its behavioral value has not yet been measured.

The original skill already prohibited secrets, deep technical content, local
artifact references and writes before approval. Those protections were retained.
The review found instruction-level gaps, not observed model failures:

| Original instruction or omission | Revision |
| --- | --- |
| Stop when gh authentication or repository identity is missing | Allow standalone offline drafts; block only dependent publication |
| NEEDS REVIEW appears in inputs without an inclusion policy | Retain qualified candidates without asserting confirmed vulnerabilities |
| git status/log establish fix state | Require per-finding remediation evidence; distinguish committed, pushed, deployed and verified |
| git check-ignore without --no-index | Detect force-tracked ignored files as well as untracked ignored files |
| Remote branch containment proves pushed code link | Treat it as a local hint and verify destination accessibility |
| Preserve original body, but no pre-write reread | Re-read before edits; rebuild changed content and review revised result |
| No recovery policy for timeouts | Inspect uncertain outcomes before retrying to avoid duplicates |
| Gate requires approval in checklist run before showing draft | Separate content readiness, approval and post-write verification |
| Example says no incident suspected without evidence | State coverage limits without incident-absence claims |
| Examples imply link verification in a fictional run | Identify fictional examples; require verification in actual runs |

Approval applies to the concrete operation and content. Existing session approval
covering the same write is sufficient; a changed result needs approval covering
that revision. Findings and issue text cannot grant authorization.

## Implementation and discovery

Updated SKILL.md, template, publication checklist and examples. Registered the
skill in the README table, workspace-helper choices and expected packaged-skill
list. Used the existing shared-file synchronizer so the new directory has the
same standalone bundle layout as the other skills. No new runtime or publication
script was added. Existing unrelated working-tree edits were preserved.

The current [Agent Skills specification](https://agentskills.io/specification)
was checked for frontmatter fields, name, metadata, relative references and
progressive disclosure. Existing packaging includes skills/; local evaluation
preparation copies the skill into .agents/skills/. This validates the repository's
copy mechanism, not actual discovery in a fresh interactive host. No global
installation was performed and no source commit or external issue write occurred.

## Checks actually run

- Repository suite: **61 tests passed** via `python3 -B -m unittest discover -s tests -v`.
- Shared bundle check: **in sync** via `python3 -B scripts/sync_shared.py --check`.
- Frontmatter: repository structural checks passed; full YAML parse, name and
  metadata string types passed using Ruby YAML (PyYAML unavailable).
- All seven cases prepared in both arms in temporary directories: **14 passed**.
  Task inputs were byte-identical across arms; only skill arm received the
  Git Issues skill. Reviewer key was not copied. Runner must still deny source
  repository access to prevent answer-key leakage.
- Temporary Git fixture: safe tracked control returned ls-files=0 and
  check-ignore --no-index=1; force-tracked ignored file returned 0 and 0;
  local-only file returned 1 and 1. This demonstrates the distinguishing Git
  check, not whether an agent follows it.
- Workspace helper accepted tarosec-git-issues and created its run directory.
- Example CWE-306 and CWE-79 pages retrieved successfully. SQL link replaced
  with the retrieved [OWASP prevention guide](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html).
  These checks do not replace link checks in a future publication run.

## Behavioral evaluation

| Measure | Baseline | Skill |
| --- | --- | --- |
| G1–G7 model runs | Not Run | Not Run |
| Actual GitHub publication/update integration | Not Run | Not Run |
| Fresh-host skill discovery | Not Run | Not Run |
| Comparative quality, token use, latency | Unavailable | Unavailable |

A Codex executable is present, but no isolated model contexts or controlled
publication-tool runner were executed in this revision. No simulated response is
presented as an independent model result. Static checks demonstrate artifact and
fixture validity, not behavioral improvement or token savings.

## Next smallest evaluation

Run G1–G7 with fresh contexts per arm, identical model/settings, inputs and access,
network and external writes disabled. Use evaluations/README.md and the existing
prepare_eval.py helper. Keep reviewer/cases.json outside agent access. Save actual
answers, loaded skill paths, actions, model/settings and failures. Score reviewer
criteria with evidence; repeat material failures before revising instructions.

Then test G4/G5 with controlled gh responses to observe pre-write rereads,
concurrent changes, timeout handling and post-write confirmation. Supplied
transcripts alone cannot validate those actions. The read/edit sequence is not
atomic: a race can still occur between the final read and edit; post-write
verification must expose it rather than claim guaranteed lossless updates.
