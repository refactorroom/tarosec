# Tarosec

**Assess. Defend. Validate. Improve.**

Tarosec is an offline cybersecurity skill suite for developers, security
reviewers, and detection engineers using AI coding agents. It helps agents turn
source code, assessment records, and telemetry into evidence-backed findings.

| Skill | Use it for | Modes |
| --- | --- | --- |
| [Tarosec Audit](skills/tarosec-audit/SKILL.md) | Audit source, dependencies, CI/CD, MCP and Agent Skills | `quick`, `deep`, `dependencies`, `agents`, `verify` |
| [Tarosec Red](skills/tarosec-red/SKILL.md) | Review scope, inventory exposed assets, and triage supplied assessment results | `recon`, `scan`, `simulate`, `bounty`, `validate` |
| [Tarosec Blue](skills/tarosec-blue/SKILL.md) | Investigate supplied telemetry and design or verify detection logic | `hunt`, `triage`, `logs`, `detect`, `verify`, `monitor` |
| [Tarosec Purple](skills/tarosec-purple/SKILL.md) | Compare recorded exercise steps with expected telemetry and alerts | `plan`, `exercise`, `emulate`, `validate`, `coverage`, `retest` |

Use the modes as cues in an agent request. The deterministic Python helpers
require Python 3.10 or later.

## Install from a local checkout

Run from the project where you want to use Tarosec. Replace the source path with
the absolute path to this checkout.

```bash
npx skills@1.9.0 add /path/to/tarosec --list
npx skills@1.9.0 add /path/to/tarosec --skill '*' --agent codex claude-code --copy -y
npx skills@1.9.0 list --agent codex claude-code
```

Select a single skill with `--skill tarosec-purple`, or choose one agent with
`--agent codex` or `--agent claude-code`. These project-level commands were
checked locally with Vercel Skills 1.9.0. For a session-only Claude Code plugin,
use `claude --plugin-dir /path/to/tarosec`. See [installation and troubleshooting](docs/install.md).

## Try it offline

Open this checkout with the desired skill installed, then give the agent one
of these requests. Fixture inputs are under [evaluations](evaluations/fixtures).

- **Audit** — Review `evaluations/fixtures/A1-audit-green-idor/app/invoices.py`
  and the tests beside it. Check invoice read and refund authorization against
  the policy in the fixture's `TASK.md`. Cite the effective guard and coverage gaps.
- **Red** — Review `evaluations/fixtures/R1-red-scope/engagement.json` and
  `recon-notes.md`. List supplied assets and separate in-scope, excluded and
  unverified entries. Keep the assessment offline.
- **Blue** — Triage `evaluations/fixtures/B2-blue-false-positive/events.jsonl`.
  Correlate the alert with the change approval and job run. State which evidence
  would change your conclusion.
- **Purple** — Compare `examples/exercise.example.json` and
  `examples/exercise.retest.json`. Report the outcome for S1 and cite the evidence IDs.

The standalone Purple helper applies the same outcome table:

```bash
python3 -B skills/tarosec-purple/scripts/classify_exercise.py examples/exercise.example.json --json
python3 -B skills/tarosec-purple/scripts/classify_exercise.py examples/exercise.retest.json --json
```

The supplied event initially has a **Detection gap**. The retest records
**Detected** with a 12-second delay. Both runs use synthetic records. See the
[worked example](examples/README.md) for the evidence chain and inconclusive case.

## Boundaries and limitations

Tarosec v0.1 works from supplied artifacts and benign synthetic data. It
supports offline asset inventory, scan-report review, defensive investigations,
and detection exercises. Active scans, exploitation, live emulation, and
production execution are outside the release scope.

An engagement record documents scope. Authority comes from the operator.
Skill guidance depends on the host for tool, filesystem and network restrictions.
Use the [authorization rules](references/authorization.md) and
[evidence-handling guidance](references/evidence-handling.md) when reviewing private data.

## Development

```bash
python3 -B scripts/sync_shared.py --check
python3 -B -m unittest discover -s tests -v
```

Each directory under `skills/` bundles its instructions, references, schemas,
validator and license notices. Edit shared files at the repository root and run
`python3 -B scripts/sync_shared.py`. See the [architecture and roadmap](docs/design.md),
[migration assessment](docs/migration.md), [evaluation instructions](evaluations/README.md),
[release readiness](docs/release-readiness.md), and [contribution guide](CONTRIBUTING.md).

[MIT license](LICENSE) · [Source notices](SOURCE_NOTICES.md) · [Security policy](SECURITY.md)
