# Tarosec Report evaluation

The earlier entry-point fallback summarized records and cited evidence IDs.
It provided no common cross-file reconciliation or bundle validator. That
contract gap was observed in the implementation. Whether an agent produces
more accurate or useful reports with the specialist is a separate question.

## Deterministic checks

The repository suite covers missing and conflicting evidence, digest mismatch,
timestamps, false positives, coverage, retests, redaction, and reproducible
bundles. Skills CLI 1.9.0 discovered seven skills and copied Report individually
for Codex and Claude Code in a disposable project. The installed Codex copy's
Python helpers generated and validated a bundle. An npm pack dry run included
the reporting skill, helpers and schema.

## Behavioral comparison

**Not Run to completion.** Both S1 arms started in fresh Codex CLI 0.159.2
sessions using gpt-6.1-sol with low reasoning effort. The baseline had the
entry point only, including its summary fallback. The skill arm also had
Report. Both had identical synthetic inputs. A preflight verified that the
profile could read the fixture and blocked reviewer-key access, workspace
writes and a loopback connection.

| Case | Baseline | Report skill |
| --- | --- | --- |
| S1, incomplete evidence | Usage limit before final answer | Usage limit before final answer |
| S2, conflicts and stale export | Not Run | Not Run |
| S3, missing retest | Not Run | Not Run |
| S4, conceptual request | Not Run | Not Run |

[S1 baseline trace](S1-baseline.json) · [S1 skill trace](S1-skill.json).
The partial traces cannot establish report quality, non-activation or overhead.
Native Claude Code invocation and published distribution remain unverified for
this change. Repeat the paired cases when model access is available.
