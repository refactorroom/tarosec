# Offline simulation

Tarosec Simulate produces or replays event records. Purple owns detection
classification. Blue can investigate the event sequence, and Red can use the
evidence and scope as input to an offline assessment.

| Catalog ID | Event count | Captured report |
| --- | ---: | --- |
| `auth.benign-login-retry` | 3 | Benign retry control with the same authentication sequence |
| `auth.suspicious-login` | 5 | [Authentication and session indicators](../examples/simulation/suspicious-login/report.md) |
| `web.attack-patterns` | 3 | [Web request indicators](../examples/simulation/web-indicators/report.md) |
| `endpoint.ransomware-behavior` | 5 | [Unusual file activity indicators](../examples/simulation/file-activity/report.md) |

The catalog emits abstract event types at fixed logical times. Each example
directory contains its scenario, event evidence, Purple exercise, and result.
The three runs completed and returned Inconclusive because they had no
independent defensive observations.

Use the benign retry alongside `auth.suspicious-login` to evaluate rules that
look for unusual activity after a successful login. Both fixtures contain two
failures followed by a success. The benign control has no source-change or
unusual-session marker. A rule intended to detect the combined pattern should
fire only for the suspicious fixture. The synthetic runner reports both as
Inconclusive until there is a separate detector result.

```bash
python3 -B skills/tarosec-simulate/scripts/simulate.py list
python3 -B skills/tarosec-simulate/scripts/simulate.py replay examples/simulation/suspicious-login --output ./replayed-login
python3 -B skills/tarosec-purple/scripts/classify_exercise.py ./replayed-login/exercise.json --json
```

Replay accepts normalized JSON and NDJSON. It can compare observations with a
separately supplied rule export bound to the normalized event digest. A complete
export with explicit non-firings supports a detection gap when expected telemetry
is present. A rule firing without all expected telemetry is partial. Synthetic
evidence and a supplied export establish only what the fixture demonstrates.
[Replay contract](../skills/tarosec-simulate/references/simulation.md)

Run on Python 3.10+ with directory-relative file access. The runner uses local
files, fixed basenames and size limits. It does no network or subprocess work.
Replay input directories should contain sanitized evidence only. Choose a new
output directory under a parent you control. `result.json` is the completion
record. An I/O interruption can leave partial artifacts in the new directory.

The incident tabletop, phishing, network and separate threshold-based
authentication scenarios remain catalog extensions. A tabletop can start with
the login report, then release separately saved evidence to Blue in stages.
Lab execution and live rule engines are outside the runner's capabilities.
