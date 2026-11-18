# Exercise design

## Step definition

Each step needs: stable ID, one ATT&CK technique (ID + name, version stated),
target host, benign procedure, expected telemetry sources, expected detection
rule IDs, and a latency budget in seconds. Optional: D3FEND countermeasures the
step is meant to exercise.

Write the expectation **before** running. An expectation written after seeing
results is a description, not a test.

## Choosing procedures

- Prefer benign, observable stand-ins: e.g. for `T1003.001 LSASS Memory`, open a
  handle to a *test* process or use a vendor-supplied benign test, not a real dump
  of a host holding real credentials.
- Use synthetic accounts and data created for the lab; destroy them afterwards.
- Avoid techniques with uncontrolled spread, persistence on shared hosts, or
  third-party contact. Tooling such as Atomic Red Team or CALDERA is optional and
  needs its own approval to install and run.
- One behavior per step, so a missing alert points at one cause.

## Controls for a trustworthy result

| Control | Why |
| --- | --- |
| Sensor heartbeat / source health over the window | Separates telemetry gap from a dead pipeline |
| Known-good positive step (a rule known to fire) | Proves the alert export path works end to end |
| Recorded end time with UTC offset | Makes latency measurable |
| Alert export covering window + latency budget | Late alerts are not misread as gaps |

If a control is missing, results that depend on it are Inconclusive.

## Retest

Keep the original step ID, technique and expectation. Record what changed (rule
version, sensor config). Report both original and new outcomes; a retest that
cannot run (environment changed, lab unavailable) is Not run, not fixed.
