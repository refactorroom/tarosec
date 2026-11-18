# Panda Suite migration assessment

The local Tarosec baseline was commit `1e6e33f` with 21 passing tests. Its
design notes described Panda Suite 1.8.0, where one Recon skill covered multiple
roles. Panda Suite 1.9.0 has separate Security, Red, and Blue skills. The
inspection used public HEAD `8c4aae1ee1b4a978957a8421b2b797bb7add3c0c`, the
matching installed release, and the public skill catalog.
[Panda Suite source](https://github.com/refactorroom/panda-suite/tree/8c4aae1ee1b4a978957a8421b2b797bb7add3c0c) · [Skill catalog](https://refactorroom.github.io/panda-suite/)

| Capability and source | Target | Reuse and change | Regression worth preserving | Compatibility risk |
| --- | --- | --- | --- | --- |
| Static security audit and review contract. `skills/panda-security/SKILL.md`, `references/`, `assets/findings.schema.json` | Audit | Adapt review guidance. Recode reports as Tarosec finding records and keep source locations. The upstream audit is skill guidance. | `test_security.py` report contract. Tarosec checks a source fixture and its correct control. | Field names, enums and routing differ. |
| Engagement, inventory and scan import. `skills/panda-red/scripts/red.py`, `scan.py`, and `schemas/` | Red | Preserve scope, evidence limits and report provenance. Tarosec handles supplied records and leaves scanner execution to external tools. | `test_red_scan.py` scope, bounded input, redaction, missing reports and producer errors. | Panda command modes and report bundles are a separate interface. |
| Triage, evidence, and case records. `skills/panda-blue/scripts/blue.py`, `case_core.py`, `schemas/` | Blue and shared case | Adapt investigation guidance. Use a small reference-based case record. | `test_red_blue_shared.py` shared-record compatibility. Tarosec checks case references and preserves timestamps and evidence IDs. | Panda state transitions and embedded records require mapping. |
| Advisory correlation and cached intelligence. `skills/panda-blue/scripts/intel*.py` and `references/threat-intelligence.md` | Audit and Blue guidance, future Intel | Preserve provenance, freshness and verified public identifiers in guidance. | `test_blue_intel.py` denied network, stale cache, and failed refresh. Revisit when adding an adapter. | Upstream registry and storage lifecycle are coupled to Panda commands. |
| Exercise and detection expectations. `skills/panda-red/references/validation.md` and `skills/panda-blue/references/verification.md` | Purple | Build a dedicated workflow and an independently authored classifier for recorded evidence. Preserve execution, telemetry and detection as separate facts. | Tarosec mixed, attribution, partial detection, false-positive and retest checks. | Analyst observations must map to step IDs, rule IDs, and target hosts. |

Panda Red's current scan helper performs local report import, bounded discovery,
validation, redaction and canonical report output. Its tests cover invalid
targets, missing reports and path restrictions. Panda Blue's case and intelligence
helpers implement stateful workflows, and their tests exercise cache and opt-in
network behavior. Instructions govern permission decisions outside those helpers.
Tarosec ships the small subset its own offline workflows need. It imports no
upstream command or runtime modules.

## Record migration

Keep the original Panda case and its referenced evidence. Create a Tarosec case
with the original `id` when it fits the Tarosec ID pattern and does not collide.
Otherwise choose a new `id` and store the exact original in `legacyId`. Map
`engagementId` to `engagementRef`, map embedded asset, finding and evidence IDs
to the corresponding `*Refs` arrays, and keep timestamps on known history events.
Map `closed` to `closed` and review other states individually. Document uncertain
mappings in the case activity log.

Each referenced record must be reviewed against the target contract before use.
Retain original finding IDs, hashes and provenance where available. Imported
claims remain reported observations until verified. v0.1 uses a manual mapping.
[Panda case schema](https://github.com/refactorroom/panda-suite/blob/8c4aae1ee1b4a978957a8421b2b797bb7add3c0c/skills/panda-blue/schemas/case.schema.json)

[Source notices and license](../SOURCE_NOTICES.md)
