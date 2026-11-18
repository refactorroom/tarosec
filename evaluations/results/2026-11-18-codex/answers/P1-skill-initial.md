**On-time detection coverage: 20% (1 of 5 planned techniques).** Including late alerts, observed detection coverage was **40% (2 of 5)**.

For the slide, “FAIL” means the detection requirement was **not demonstrated**, including inconclusive tests.

| Technique (supplied ATT&CK v17 mapping) | Result | Deciding evidence / next action |
|---|---|---|
| T1003.001 — LSASS Memory | **PASS — Detected** | Alert in 52s; 300s budget. `EV-ALERT-1`. |
| T1087.002 — Domain Account Discovery | **FAIL — Inconclusive** | Alert names `lab-dc-01`, expected `lab-win-02`; conflicting export records. Correlate `EV-ALERT-2` with `EV-RUN-S2`. |
| T1558.003 — Kerberoasting | **FAIL — Inconclusive** | Execution failed due to SPN typo (`EV-RUN-S3`). Correct setup and retest. |
| T1059.001 — PowerShell | **FAIL — Inconclusive** | Collector unhealthy; missing heartbeat (`EV-HEARTBEAT-W03`). Restore collection and retest. |
| T1053.005 — Scheduled Task | **FAIL — Detected late** | Alert in 840s; 300s budget. Investigate alert delay. |

**Outcome breakdown:** 1 detected on time, 1 detected late, 3 inconclusive; **no confirmed detection gaps**. Kerberoasting did not successfully execute.

Scope: supplied lab records only; no retesting performed. Records are dated **November 12, 2026**, rather than yesterday. ATT&CK mappings are supplied as v17 and were not independently verified. These percentages describe this exercise, not organization-wide ATT&CK coverage.
