**Slide-ready: 20% confirmed detection coverage (1 of 5 planned techniques passed).** Pass requires an attributable alert within the expected time limit.

| Technique | Pass/fail* | Evidence |
|---|---|---|
| T1003.001 — LSASS Memory | **Pass** | Expected alert on target host after 52 seconds; limit 300 seconds. |
| T1087.002 — Domain Account Discovery | **Unconfirmed** | Conflicting fired/not-fired records; fired alert names a different host. Needs correlation to this test. |
| T1558.003 — Kerberoasting | **Not tested successfully** | Execution failed because of an SPN typo. |
| T1059.001 — PowerShell | **Fail — telemetry outage** | Execution succeeded, but the required log source was unhealthy; no alert. |
| T1053.005 — Scheduled Task | **Fail — late detection** | Alert arrived after 840 seconds; limit 300 seconds. |

\*A strict binary slide can label all four remaining rows **“Pass not demonstrated.”** They should not all be described as detection-rule failures.

**Suggested slide text:** “1/5 planned techniques demonstrated timely detection (20%); remaining outcomes: one late alert, one telemetry outage, one failed execution, and one unresolved alert correlation.”

The files date this run **November 12, 2026**, rather than yesterday.
