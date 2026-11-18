# Tarosec

**Assess · Defend · Validate · Improve**

Agent-native cybersecurity skills for Red, Blue and Purple teams. Each skill is a
self-contained [Agent Skill](https://agentskills.io/specification); the suite
shares one authorization model, evidence rules and JSON record schemas.

| Skill | Role | Modes (request cues, not CLI subcommands) |
| --- | --- | --- |
| [`tarosec-audit`](skills/tarosec-audit/SKILL.md) | Code, dependency, CI/CD, MCP and Agent Skill auditing | `quick` `deep` `dependencies` `agents` `verify` |
| [`tarosec-red`](skills/tarosec-red/SKILL.md) | Authorized recon, scoped validation, bounty evidence | `recon` `scan` `simulate` `bounty` `validate` |
| [`tarosec-blue`](skills/tarosec-blue/SKILL.md) | Hunting, triage, log analysis, detection engineering | `hunt` `triage` `logs` `detect` `monitor` |
| [`tarosec-purple`](skills/tarosec-purple/SKILL.md) | Detection validation: expected vs observed per emulation step | `exercise` `emulate` `validate` `coverage` `retest` |

`tarosec-purple` is the core: it classifies each step as **Detected, Detected
(late), Prevented, Detection gap, Telemetry gap, Inconclusive** or **Not run**,
so a missing alert is never automatically reported as a gap.
`skills/tarosec-purple/scripts/classify_exercise.py` applies that table offline.

Planned, not shipped: `tarosec-intel`, `tarosec-incident` (v0.2),
`tarosec-threat`, `tarosec-posture` (v0.3). See [design](docs/design.md).

## Safety model

Read-only analysis is the default. Target contact, emulation, credential use,
containment and production changes need explicit approval from the operator for
that action. An engagement or exercise file narrows scope; it never grants it.
See [authorization](references/authorization.md). The skills are instructions,
not a sandbox: enforce boundaries with host permissions as well.

## Use

Claude Code (local checkout, session-only):

```bash
claude --plugin-dir /path/to/tarosec
```

Example prompts: `Use tarosec-purple to validate examples/exercise.example.json`,
`tarosec-audit deep ./project`, `tarosec-blue hunt ./logs`.

Other Agent Skills hosts: copy a directory from `skills/` into the host's skill
folder. Each skill directory is complete on its own.

## Layout

```
skills/<skill>/        SKILL.md, references/, scripts/, assets/schemas/ (shared copies)
references/            canonical shared guidance (authorization, evidence, standards)
schemas/               canonical JSON schemas: engagement, evidence, finding, exercise
scripts/               validate_record.py, sync_shared.py, prepare_eval.py
evaluations/           blind fixtures + reviewer-only answer key
examples/              schema-valid sample records
tests/                 structural, helper and fixture tests
```

Edit shared files only at the root, then run `python3 scripts/sync_shared.py`.

## Development checks

```bash
python3 -B -m unittest discover -s tests
```

```bash
python3 -B scripts/sync_shared.py --check
```

```bash
claude plugin validate .
```

These check structure, helpers and fixtures. They do not measure model behavior;
see [evaluations](evaluations/README.md).

## License

MIT. Derived in part from guidance in Panda Suite `panda-security` and
`panda-recon` (same author, MIT).
