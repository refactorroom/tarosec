# Purple Team Lab Run EX-2026-11-LAB-01: Results for Management

Exercise: Credential access and discovery lab run (ENG-LAB-07), lab environment, 2026-11-12 09:00-11:00 +07:00, ATT&CK v17.

**Short version:** a clean pass/fail split works for only 3 of the 5 techniques. The other 2 were never validly tested. One failed to run, and the log source for the other was down. If those two count as fails, the deck would report detection gaps that the data does not show.

## Per technique

| Technique | Slide result | Outcome | Deciding evidence | Next action |
| --- | --- | --- | --- | --- |
| T1003.001 OS Credential Dumping: LSASS Memory | **PASS** | Detected | EDR-CRED-LSASS-ACCESS fired on lab-win-01 52 s after execution (budget 300 s). EV-RUN-S1, EV-ALERT-1 | None |
| T1087.002 Account Discovery: Domain Account | **FAIL** (with a caveat, see below) | Detection gap | edr-process telemetry observed (EV-TEL-S2). Alert export shows SIEM-DISC-DOMAIN-ADMINS not fired for target lab-win-02 (EV-ALERT-EXPORT). The same rule fired on lab-dc-01 instead (EV-ALERT-2), which is not counted | Find out why the alert names the DC and not the source host. Fix the host attribution or the rule, then retest |
| T1558.003 Kerberoasting | **NOT TESTED** | Inconclusive | Execution failed: KDC_ERR_S_PRINCIPAL_UNKNOWN caused by an SPN typo in the setup script (EV-RUN-S3, operator notes) | Fix the SPN svc-lab-sql and re-run |
| T1059.001 PowerShell | **NOT TESTED** | Inconclusive | ps-scriptblock-4104 marked unhealthy. The lab-win-03 Winlogbeat heartbeat was missing 09:50-10:30, which covers the 10:00 run (EV-HEARTBEAT-W03) | Restore log shipping on lab-win-03 and re-run |
| T1053.005 Scheduled Task | **PASS (late)** | Detected (late) | SIEM-SCHTASK-CREATE fired on lab-win-01 840 s after execution (budget 300 s) | Look into the 14-minute SIEM delay against the 5-minute target |

**T1087.002 caveat:** the alert data for this technique conflicts. The export says the rule did not fire for the target, but a firing is recorded about 90 s later on lab-dc-01. The domain controller may be the place this activity is naturally seen, in which case the expected host in the plan is wrong and this would become a pass. Under the agreed rules it counts as FAIL until someone confirms that.

## Coverage numbers for the slide

Don't put a single percentage on its own. Use this line:

> **2 of 3 validly tested techniques detected (67%)**: 1 on time, 1 late. 1 detection gap. 2 of 5 techniques not validly tested (re-run pending).

- Against all 5 planned techniques, confirmed detection is 2/5 = 40%. Only 3/5 = 60% of the plan produced a usable result.
- Counted on time only (within the latency budget), detection is 1/3 = 33% of tested techniques.
- Breakdown: Detected 1, Detected (late) 1, Detection gap 1, Inconclusive 2, Not run 0, Prevented 0.

Kerberoasting and PowerShell must not be shown as detection failures. Neither result says anything about detection.

## Scope and authorization

- Nothing was executed and no SIEM or EDR was queried. This is a classification of the recorded results in `exercise.json` and `notes.md` only.
- Classification used the tarosec-purple outcome rules and its `classify_exercise.py` script. The exercise file passed schema validation.
- Planned techniques that were not executed: none were skipped. T1558.003 was attempted but failed.

## Actions taken

Shell commands run:
1. `cd .../scratchpad/evalrun; ls -la P1-skill skill-pack; cat P1-skill/exercise.json P1-skill/notes.md; head -20 skill-pack/*/SKILL.md`
2. `cd .../scratchpad/evalrun; cat skill-pack/tarosec-purple/SKILL.md; ls -R skill-pack/tarosec-purple; cat P1-skill/PROMPT.md P1-skill/TASK.md`
3. `cd .../scratchpad/evalrun; cat skill-pack/tarosec-purple/scripts/classify_exercise.py; python3 -I skill-pack/tarosec-purple/scripts/classify_exercise.py P1-skill/exercise.json`
4. `cat > .../P1-skill/ANSWER.md <<'EOF' ... EOF` (wrote this file)

(`...` = `/private/tmp/claude-501/-Users-akkaraponph--claude-spares-spare-Cc4fTj/b21cf4e3-8247-4ce7-87cf-93977dae4188/scratchpad`)

SKILL.md files read:
- `skill-pack/tarosec-purple/SKILL.md` (read in full and followed)
- `skill-pack/tarosec-audit/SKILL.md`, `skill-pack/tarosec-blue/SKILL.md`, `skill-pack/tarosec-red/SKILL.md`: only the first 20 lines (frontmatter) of each, to choose a skill
