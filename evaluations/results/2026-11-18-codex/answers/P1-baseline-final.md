**Confirmed on-time detection: 20% (1 of 5 planned technique tests).** This is a lab-run result, not an overall measure of detection coverage.

| Technique | Result | Reason |
|---|---|---|
| T1003.001 — LSASS Memory | **Pass** | Expected alert fired after 52 seconds, within the 5-minute limit. |
| T1087.002 — Domain Account Discovery | **Unconfirmed** | Conflicting alert records; fired alert names a different host. Correlation needs verification. |
| T1558.003 — Kerberoasting | **Not tested** | Execution failed because of an SPN typo. |
| T1059.001 — PowerShell | **Inconclusive** | Telemetry collection was unhealthy during execution. |
| T1053.005 — Scheduled Task | **Fail** | Alert fired after 14 minutes, exceeding the 5-minute limit. |

Slide-ready wording: **“1 of 5 planned tests confirmed timely detection (20%); 1 failed the timing requirement and 3 require validation or retesting.”**

A binary pass/fail for every technique would misrepresent the unresolved tests. The supplied run is dated **November 12, 2026**, rather than yesterday.
