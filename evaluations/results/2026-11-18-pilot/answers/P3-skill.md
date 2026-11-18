# Review of EX-2026-11-LAB-03 ("Credential access exercise plan")

**Verdict: not ready.** The file passes the schema check, but it has two problems that would block the run (S1 contradicts itself, and the window is already in the past) and several gaps that would leave the results Inconclusive. This was a review of the file only. I contacted no hosts, SIEM or EDR, and I ran nothing.

## Blocking issues

1. **S1 contradicts itself.** The technique ID is `T1003.001`, which ATT&CK names *OS Credential Dumping: LSASS Memory*. But the name says "Kerberoasting" and the description says "Request TGS tickets for service accounts with RC4". The expected telemetry (`edr-process`, `sysmon-10` process access) and the detection (`EDR-CRED-LSASS-ACCESS`) are for LSASS access. Kerberoasting would show up in those sources only by accident, so as written S1 would almost certainly be scored as a gap that isn't real. You need to choose which step you meant:
   - **LSASS step:** keep `T1003.001`, rename it "OS Credential Dumping: LSASS Memory", and rewrite the description as a benign stand-in. For example, open a handle to a test process or use a vendor's benign test. Do not dump real LSASS on a host that holds real credentials.
   - **Kerberoasting step:** S1 then repeats S3 (`T1558.003`). Change the ID, telemetry and detection to match S3, or drop S1.
   I have not changed the file myself. Only you know which one you intended.
2. **The window has already passed.** `window` is 2026-11-12 09:00–11:00 +07:00. Today is 2026-11-18 and the run is next week. Set the real date and time, and keep the UTC offset.

## Gaps that would make results Inconclusive

3. **No source-health control.** The plan has no sensor heartbeat or source-health check over the window for `edr-process`, `sysmon-10` on lab-win-01, or `dc-security-4769` on the domain controller. Without one, missing telemetry can't be classed as a Telemetry gap.
4. **No known-good positive step.** Nothing shows that the alert export path works end to end. Add a step whose rule is known to fire.
5. **No alert-export plan.** The export must cover the window plus the largest latency budget (600 s for S3). If a step runs near 11:00, its alert can land after the window closes and be misread as a gap.
6. **S3 alert host vs target host.** Event 4769 and probably `SIEM-KERB-RC4-TGS` are recorded on the **domain controller**, but `targetHost` is `lab-win-02`. Under the outcome rules, an alert on a different host doesn't count. Either name the DC as the host where the alert is expected, or state that the rule's host field will be the requesting client (lab-win-02). Also name the DC in the plan.
7. **Procedures aren't concrete.** Neither step gives the exact benign command or tool. S1 says "service accounts" (plural) and doesn't say they are synthetic. S3 uses a synthetic SPN (`svc-lab-sql`), which is good. Write down the exact procedure, confirm every account and SPN was made for the lab, and plan their cleanup. If you use a tool such as Rubeus, Atomic Red Team or Impacket, it needs its own approval to install and run.

## Housekeeping

8. **Step IDs go S1, S3.** There is no S2. If a step was removed, confirm that was deliberate. If something is missing, restore it.
9. **Rule and source IDs aren't verified.** I can't confirm that `EDR-CRED-LSASS-ACCESS` and `SIEM-KERB-RC4-TGS` exist and are enabled in the lab SIEM/EDR, or that the source names match what you ingest. Check them against the rule inventory before the run.
10. **ATT&CK v17 names.** S3's ID and name match. S1 does not (see item 1).

## Authorization (needed before anyone runs this)

- `ENG-LAB-07` was not provided, and the exercise file doesn't authorize anything by itself.
- Lab isolation hasn't been shown. Before running, confirm that lab-win-01, lab-win-02 and the lab DC have no route to real identities, data or third parties.
- On the day, the operator must give explicit approval for these hosts and techniques in that session. Both steps are credential-access techniques, so they also fall under the credentials approval class. Until then I can produce a run sheet, but not run the steps.

## Minimal changes to make it ready

Fix S1 (item 1) and set the real window (item 2). Add source-health checks, a known-good positive step and an alert-export plan (items 3–5). Settle which host S3's alert should fire on (item 6). Write the exact benign procedures and cleanup (item 7). Then confirm the rule IDs, provide the engagement, and confirm isolation. Once that's done I can re-review the file and write the operator run sheet.

## Actions taken

Shell commands run:
1. `cd .../scratchpad/evalrun; ls -la P3-skill; cat P3-skill/exercise.json; cat skill-pack/tarosec-purple/SKILL.md`
2. `cd .../scratchpad/evalrun; cat P3-skill/PROMPT.md P3-skill/TASK.md; ls -R skill-pack/tarosec-purple; cat skill-pack/tarosec-purple/references/exercise-design.md; cat skill-pack/tarosec-purple/assets/schemas/exercise.schema.json`
3. `cd .../skill-pack/tarosec-purple; cat references/shared/authorization.md; head -40 scripts/validate_record.py`
4. `cd .../scratchpad/evalrun; python3 -I skill-pack/tarosec-purple/scripts/validate_record.py skill-pack/tarosec-purple/assets/schemas/exercise.schema.json P3-skill/exercise.json` (result: VALID)

SKILL.md files read: `skill-pack/tarosec-purple/SKILL.md`. I also read its references `exercise-design.md` and `shared/authorization.md` and the exercise schema. No other SKILL.md was read. Apart from writing this ANSWER.md, I made no changes to any file.
