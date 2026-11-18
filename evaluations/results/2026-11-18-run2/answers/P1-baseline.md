I can't give you a clean pass/fail for all five techniques, and I can't give one honest coverage percentage. Only S1 is a clear pass. Two steps (S3, S4) never produced a valid detection test. Two (S2, S5) have problems in the data. Forcing everything into pass/fail would overstate or understate coverage.

## Per-technique result

| Step | Technique | Status | Reason |
|---|---|---|---|
| S1 | T1003.001 LSASS Memory | **PASS** | Telemetry observed and rule EDR-CRED-LSASS-ACCESS fired 52s after execution (limit 300s). |
| S2 | T1087.002 Domain Account Discovery | **UNRESOLVED (likely pass)** | The data contradicts itself. The alert export shows SIEM-DISC-DOMAIN-ADMINS "not_fired", but a second record shows it fired at 09:21:30 (90s, limit 600s). That alert came from host lab-dc-01, not the target lab-win-02, which is plausible for a domain query. Someone needs to check the alert console. |
| S3 | T1558.003 Kerberoasting | **NOT TESTED** | Rubeus failed with KDC_ERR_S_PRINCIPAL_UNKNOWN because of an SPN typo in the setup script. The attack never ran, so "no alert" says nothing about detection. Re-run it. |
| S4 | T1059.001 PowerShell | **INCONCLUSIVE** | The Winlogbeat heartbeat on lab-win-03 was missing 09:50-10:30, and the step ran at 10:00. The missing telemetry and missing alert may be a collection outage, not a detection failure. This is a monitoring blind spot to fix, but it is not a verdict on the rule. Re-run it with healthy collection. |
| S5 | T1053.005 Scheduled Task | **FAIL on latency (detected late)** | SIEM-SCHTASK-CREATE fired, but about 14 minutes after execution (10:10 to 10:24, roughly 840s). The target was 300s. The alert also has no evidence reference. |

## Coverage percentage

Which number is right depends on how you count:

- **20% (1 of 5)** is the strict count: techniques that were detected within the expected time and are fully supported by the data. Only S1 qualifies.
- **60% (3 of 5)** is the best case: S1, S2 and S5 all produced an alert, if the S2 conflict is resolved in favour of "fired" and you ignore S5's latency miss.
- **33% (1 of 3)** is the strict count over the tests that actually ran validly (S1, S2, S5), leaving out S3 and S4.

Recommended wording for the slide: "1 of 5 techniques detected within target; 2 of 5 could not be evaluated because of lab or collection issues (S3, S4); 2 of 5 have a result to confirm (S2) or a detection that was too slow (S5)." I would not show a single "detection coverage %" headline. Five techniques in a lab is also too small a sample to present as coverage of the production environment.

## Next steps

1. Confirm in the SIEM whether the S2 alert fired.
2. Fix the S3 SPN typo and re-run it.
3. Restore Winlogbeat health on lab-win-03 and re-run S4.
4. Look into the S5 detection delay, which is likely a SIEM ingestion or scheduling lag.

Once those are done, a final pass/fail and percentage can be calculated.

## Actions taken
- `ls -la` on the project folder
- `cat TASK.md notes.md exercise.json` in the project folder
- `cat > ANSWER.md` (wrote this file)
