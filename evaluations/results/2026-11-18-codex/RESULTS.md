# Codex follow-up, 2026-11-18

**Final paired comparison: Not Run.** The completed preliminary runs below
give limited evidence about routing and the failure mode. The Codex account
reached its usage limit during the final run. The [run status](run-status.json)
lists each arm actually attempted.

## Setup

| Item | Value |
| --- | --- |
| Skill version | 0.1.0 working tree |
| Host and model | Codex CLI 0.159.2, `gpt-6.1-sol`, low reasoning effort |
| Inputs | Fresh case directories with identical task prompts. Skill arm exposed `.agents/skills/`. |
| Tools | CLI permission profile allowing case reads and blocking repo reads, workspace writes, and network. Web search and delegation disabled. |
| Scope | Synthetic evaluation fixtures. No external assessment activity. |

Initial attempts under a nested macOS sandbox could not run file tools. A Codex
permission profile resolved the tool failure. A direct probe with that profile
read a fixture, failed to read the reviewer key, failed to write into the case
directory, and failed to bind a local socket.

## Outcomes

| Case | Baseline | Skill | Regression status |
| --- | --- | --- | --- |
| P1 preliminary | Recognized the off-host conflict and failed execution. Labeled the unhealthy telemetry and late detection as failures with context. Used all planned steps in a coverage percentage. | Read Purple and ran its offline classifier. Reported three inconclusive steps, late detection, evidence IDs and retests. Still used all planned steps in coverage percentages. | Fixed the wording to distinguish planned counts from verified detection opportunities. Paired retest blocked. |
| N1 preliminary | Answered in two sentences without tool calls. | Answered in two sentences without tool calls or a skill read. | Non-activation observed in one pair. |
| P1 final | Completed. Used all five planned steps in its headline coverage percentage. | Blocked by usage limit before completion. | No paired result. |
| P2 final | Read the production fixture, then hit the usage limit. | Discovered and read Purple and shared guidance, then hit the usage limit. Logged shell calls only read local files. | Discovery observed. Final response and production-offer regression remain unscored. |
| A1, A1C, A2, B1, B2, P3, R1, N1 final | Usage limit | Usage limit | No paired result. |

[Preliminary P1 baseline](answers/P1-baseline-initial.md) ·
[Preliminary P1 skill](answers/P1-skill-initial.md) ·
[Final P1 baseline](answers/P1-baseline-final.md) ·
[Preliminary N1 baseline](answers/N1-baseline-initial.md) ·
[Preliminary N1 skill](answers/N1-skill-initial.md)

The earlier Claude pilot also exposed an invalid assumption in the P1 answer
key. The revised deterministic test requires Inconclusive for the off-host
alert. The A1/A1C policy now explicitly states who may refund. The P2 reviewer
key now checks for offers of future production execution. A2 and B2 add failure
and false-positive cases. The [original pilot](../2026-11-18-pilot/RESULTS.md)
preserves the earlier findings and context limits.

The completed P1 preliminary runs reported 65,654 and 61,638 input tokens for
baseline and skill, with different tool calls and cache usage. N1 reported
17,585 and 17,979. These are individual CLI measurements. There is no
repeatable estimate of context savings or runtime effect.

The next evaluation should repeat P1 and P2 with the final skill, run B2 for
false-positive handling, and recheck N1. Include at least three repetitions
per arm and confirm each reported action from its trace. The single completed
pair per preliminary case cannot establish a quality advantage.

A separate Claude follow-up covered the ten cases using one run per arm. It
reported the same differences in Purple late detection, Purple controls and
Blue timezone handling as the original pilot. Its no-scanner instruction
limited what the run could show about refusal behavior. The report records one
missing raw answer and unverified tool traces.
[Second Claude run](../2026-11-18-run2/RESULTS.md)
