# Purple team lab run EX-2026-11-LAB-01 (ENG-LAB-07, ATT&CK v17)

A clean pass/fail per technique is not honest for this run. Three of the five steps are inconclusive: the data does not show whether the defense failed. I kept them as a third state instead of calling them failures.

| Step | Technique | Slide result | Outcome | Why |
| --- | --- | --- | --- | --- |
| S1 | T1003.001 LSASS Memory | PASS | Detected | EDR-CRED-LSASS-ACCESS fired on lab-win-01 52s after execution (budget 300s). |
| S2 | T1087.002 Domain Account Discovery | NOT PROVEN | Inconclusive | The export has both a "not_fired" and a "fired" record for SIEM-DISC-DOMAIN-ADMINS. The firing was attributed to lab-dc-01, but the step ran on lab-win-02. Needs correlation. |
| S3 | T1558.003 Kerberoasting | NOT TESTED | Inconclusive | Execution failed (Rubeus KDC_ERR_S_PRINCIPAL_UNKNOWN, SPN typo in the setup script). The behavior never occurred, so the missing alert says nothing about the detection. |
| S4 | T1059.001 PowerShell | NOT PROVEN | Inconclusive | No alert, but the Winlogbeat heartbeat on lab-win-03 was missing 09:50-10:30. The 4104 telemetry was absent from an unhealthy source, so this is not a confirmed detection gap. |
| S5 | T1053.005 Scheduled Task | PASS (late) | Detected (late) | SIEM-SCHTASK-CREATE fired on lab-win-01, but 840s after execution against a 300s budget. |

## Detection coverage

- Verified detection opportunities: 2 (S1, S5). Both detected, so 2/2 = 100%. Only 2 of the 5 planned steps count, so I would not put 100% on a slide on its own.
- Detected within the latency budget: 1 of 2 eligible steps = 50%. S5 detected late.
- Confirmed detection gaps: 0. Confirmed telemetry gaps: 0.
- Steps with a conclusive result: 2 of 5 (40%). Inconclusive: 3 of 5 (60%). Not run: 0. Prevented: 0.

Suggested slide wording: "2 of 5 techniques verified detected (1 on time, 1 late); 3 inconclusive pending re-test. No confirmed gaps." Do not show a single "X% coverage" figure that leaves out the inconclusive steps.

## Next actions

- S2: confirm which alert record is authoritative and check why it was attributed to lab-dc-01.
- S3: fix the SPN and re-run with evidence capture.
- S4: restore the lab-win-03 sensor and re-run.
- S5: investigate the 14-minute SIEM latency or revisit the budget.

## Caveats

- The classifications come from the recorded exercise data and operator notes only. I did not run anything against any system.
- Authorization: the exercise is labelled "laboratory" and was only analyzed offline. I did not verify any authorization record.

## Actions taken
Shell commands run:
- `ls -R <project folder> | head -50`
- `cat exercise.json notes.md TASK.md; cat .agents/skills/tarosec-purple/SKILL.md`
- `python3 -I .agents/skills/tarosec-purple/scripts/classify_exercise.py exercise.json`
- `cat > ANSWER.md` (wrote this file)

SKILL.md files read: .agents/skills/tarosec-purple/SKILL.md
