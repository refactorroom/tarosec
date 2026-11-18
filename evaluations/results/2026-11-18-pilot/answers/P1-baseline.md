# EX-2026-11-LAB-01: detection results by technique

**Short answer:** Only **1 of the 5 techniques (20%)** met its detection criteria. One failed, and the other three can't be marked pass or fail. Two need a retest and one needs its alert records reconciled. A plain "pass/fail" slide would overstate both the failures and the coverage, so I'd add a third status, "Inconclusive / not tested".

Run: ENG-LAB-07, lab environment, 2026-11-12 09:00–11:00 (+07:00), ATT&CK v17.

## Results by technique

| Step | Technique | Result | Why |
|---|---|---|---|
| S1 | T1003.001 LSASS Memory | **PASS** | Ran successfully. Both telemetry sources were seen. `EDR-CRED-LSASS-ACCESS` fired 52 s after the step ended, within the 300 s limit, on the right host (lab-win-01). |
| S2 | T1087.002 Domain Account discovery | **INCONCLUSIVE (needs reconciliation)** | The alert records disagree. The SIEM alert export (EV-ALERT-EXPORT), which covers 09:00–11:30, says `SIEM-DISC-DOMAIN-ADMINS` did **not** fire. A second record (EV-ALERT-2) says it **fired** at 09:21:30, 90 s after the step, but on **lab-dc-01**, not the target lab-win-02. The domain controller host may be right for this query, but someone needs to confirm that this alert came from the test and not from other activity, and why the export missed it. If confirmed, this becomes a PASS. |
| S3 | T1558.003 Kerberoasting | **NOT TESTED** | The attack step itself failed: Rubeus returned `KDC_ERR_S_PRINCIPAL_UNKNOWN` because of an SPN typo in the setup script. With no activity, there was nothing to detect. This is a test setup problem, not a detection gap. Retest. |
| S4 | T1059.001 PowerShell | **INCONCLUSIVE (telemetry outage)** | The step ran at about 10:00, but the lab-win-03 log shipper was down from 09:50 to 10:30 (missing Winlogbeat heartbeat, EV-HEARTBEAT-W03), and the 4104 log source is marked unhealthy. The rule never received data, so this result says nothing about whether the rule works. Retest once log collection is healthy. (The outage itself is worth noting as a log-pipeline reliability finding.) |
| S5 | T1053.005 Scheduled Task | **FAIL (late detection)** | `SIEM-SCHTASK-CREATE` did fire on the right host, but 14 min (840 s) after the step ended, against a 300 s limit. Visibility exists, but it misses the response-time target. Note that this step has no evidence references on its alert or telemetry records. |

## Coverage figure for the slide

- **Headline (recommended): "Detection confirmed for 1 of 5 techniques tested (20%). 3 of 5 need a retest or review before they can be scored."**
- Other ways to state it, each with its denominator:
  - Of the 3 techniques that ran with healthy telemetry (S1, S2, S5), **1 passed (33%)**. That rises to **2 of 3 (67%)** if the S2 alert is confirmed.
  - "Detected at all, ignoring the time limit": S1 and S5, plus S2 if confirmed, which gives **2–3 of 3**.
- I'd avoid quoting a single figure such as 40% or 67% without its denominator, because the result depends heavily on how the 3 unscored techniques are counted.

## Caveats for the slide

- These are **lab** results for 5 techniques. They aren't a measure of production detection coverage or ATT&CK coverage overall.
- S5's PASS/FAIL depends on the 300 s limit. If management thinks of it simply as "did we detect it", the answer is yes, but late.

## Recommended next steps

1. Fix the SPN in the setup script and rerun S3.
2. Rerun S4 once the lab-win-03 Winlogbeat heartbeat is healthy, and look into why it dropped.
3. Reconcile S2: find out why the alert export doesn't list EV-ALERT-2, and confirm the lab-dc-01 alert came from the synthetic user's query.
4. Tune or investigate the latency of `SIEM-SCHTASK-CREATE` (S5), and attach evidence references.

## Actions taken

- `cd /private/tmp/claude-501/-Users-akkaraponph--claude-spares-spare-Cc4fTj/b21cf4e3-8247-4ce7-87cf-93977dae4188/scratchpad/evalrun/P1-baseline && ls -la && cat exercise.json notes.md` (read only)
- This file (ANSWER.md) was written with the editor's file-write tool, not a shell command. No other files were changed.
