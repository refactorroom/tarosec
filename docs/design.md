# Tarosec v0.1 design assessment

Produced with the Panda Skill Lab method on 2026-11-18 against the "Tarosec —
Cybersecurity Skills Architecture" proposal.

## Corrections to the proposal's premise

1. **Panda Suite 1.8.0 has no separate Red or Blue skill.** It ships
   `panda-security` (audit: quick/deep/skills/verify) and `panda-recon`, one skill
   that covers scan, recon, simulate, hunt, incident, bounty, verify and intel.
   So v0.1 is a **split** of `panda-recon`, not a migration of three existing skills.
2. **Purple already partly exists.** `panda-recon` `simulate` mode
   (`references/validation.md`) already separates "observed alert, missing
   expected alert, missing telemetry, untested detection". `tarosec-purple` turns
   that paragraph into a primary workflow: an explicit outcome table, an exercise
   schema, and a deterministic classifier.
3. **Shared root folders don't reach installed skills.** Hosts load one skill
   directory at a time, so `references/` and `schemas/` at the repo root are
   invisible after install. Fix: canonical root files + `scripts/sync_shared.py`
   copies into each skill, with a `--check` test that fails on drift.
4. **`$tarosec-audit` is Codex-style syntax.** In Claude Code a plugin skill shows
   up as `/tarosec:tarosec-audit` or triggers from its description.
5. **Scenario format.** The proposal used `lab-scenario.yaml`. v0.1 uses JSON so
   the helpers stay stdlib-only. This environment had no PyYAML or jsonschema.

## Target failure modes (hypothesized, not yet observed)

| Skill | What a plain agent likely gets wrong | Case |
| --- | --- | --- |
| purple | Treats "no alert" as a detection gap, ignoring failed runs, dead sensors, late or off-host alerts; reports one pass % | P1 |
| purple | Treats an approval string in the exercise file as authorization; runs against production | P2 |
| purple | Accepts a mislabelled ATT&CK ID | P3 |
| blue | Is swayed by instructions planted in log fields; assumes the zone of unzoned syslog | B1 |
| red | Widens scope to discovered or excluded hosts because "they're the client's" | R1 |
| audit | Trusts a green suite and the existence of an access helper | A1 / A1C |
| all | Activates on a plain conceptual question | N1 |

These are hypotheses. Whether the skills beat a baseline is **Not Run** (see
[evaluations](../evaluations/README.md)).

## Contract decisions

- **Four skills only.** Intel and incident stay as labelled sections inside
  `tarosec-blue` until a case shows a separate trigger is worth it (the proposal's
  own rule). Fewer descriptions also means less routing confusion.
- **One finding schema with a `producer` field.** Severity, confidence, status and
  claim strength are independent fields. Purple's gap types are `status` values,
  so audit, red, blue and purple records can be merged.
- **Authorization is centralized** in `references/authorization.md`, and each
  SKILL.md links to it instead of restating it. The rule: a file narrows scope and
  never grants it. Only the operator, in the current session, can grant an action.
- **Non-triggers are in every description** ("Not for …"), and a test enforces it.

## Coexistence with Panda Suite

If both plugins are installed, `panda-security` overlaps `tarosec-audit` and
`panda-recon` overlaps red, blue and purple. Routing between them is untested.
Options: deprecate the Panda security skills once Tarosec has eval evidence,
or narrow their descriptions to point to Tarosec. Decide after the routing eval.

## Not done in v0.1

- Not migrated: `panda-recon`'s helper scripts (`recon.py`, `scan.py`,
  `intel*.py`, about 115 KB with tests). They support scope checks, case
  lifecycle and intel retrieval. Port them only once their behavior is needed
  and the tests come with them.
- No incident schema yet; it waits for `tarosec-incident`.
- No live SIEM/EDR, Atomic Red Team or CALDERA integration.
- No host discovery or routing test. Only manifest validation was run.
