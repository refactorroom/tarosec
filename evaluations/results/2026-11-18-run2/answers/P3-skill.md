# Review of exercise.json (EX-2026-11-LAB-03)

**Verdict: not ready.** The file passes the basic schema shape (required fields present), but it has blocking problems that would make results untrustworthy. Fix these before next week's run.

## Blocking issues

1. **S1 technique ID and name disagree.** `T1003.001` is OS Credential Dumping: LSASS Memory. The name and description say Kerberoasting, which is `T1558.003` (the ID S3 uses). The expected detection `EDR-CRED-LSASS-ACCESS` and source `sysmon-10` (process access) are LSASS-dump expectations. A Kerberoast TGS request would never fire them. Decide which behavior S1 is, then make the ID, name, description, telemetry and detection agree. As written, S1 would likely report a false "detection gap".
2. **The window has already passed.** The window is 2026-11-12 09:00-11:00 (+07:00). Today is 2026-11-18, and you plan to run next week. Update the window, with the UTC offset, to the actual run time.
3. **No authorization is on record.** `engagementRef: ENG-LAB-07` is only a reference. I was not given the engagement file, and the plan does not establish who authorized what. A reference or ticket ID is not authorization. The operator needs to state, in the run conversation, that they hold authority over lab-win-01 and lab-win-02 for these techniques and this window. Also confirm the lab is isolated from real identities, data and third parties.
4. **S1 may not be benign or synthetic.** S1 requests tickets for "service accounts" with RC4. S3 uses a named synthetic SPN (`svc-lab-sql`). Make S1 use synthetic SPNs as well, or a prerecorded event, and state that.

## Other issues to fix

- **Step IDs jump from S1 to S3.** Either S2 was dropped or it is a typo. Confirm nothing is missing.
- **The two steps overlap.** Both are Kerberoasting on different hosts. If S1 is meant to be the LSASS-dump behavior, it should be a separate step with its own technique, which keeps one behavior per step.
- **Host attribution for S3.** Event 4769 and the `SIEM-KERB-RC4-TGS` rule come from the domain controller, not `lab-win-02`. The v0.1 classifier matches the reported target host. Document how alerts will be correlated to the target host, or a correct firing may be read as unattributed.
- **ATT&CK v17 is old.** The standards reference lists v20.1 as current, as checked on 2026-11-18. IDs can be revoked or renumbered. Verify T1558.003 and the other IDs against v17, or state that they are unverified against the current release.
- **Detection rule IDs are unverified.** Confirm that `EDR-CRED-LSASS-ACCESS` and `SIEM-KERB-RC4-TGS` exist and are enabled, and that sources `edr-process`, `sysmon-10` and `dc-security-4769` are actually collected in the lab.
- **Missing trust controls.** The plan has none of these:
  - Sensor heartbeat or source health over the window.
  - A known-good positive step that proves the alert export path works.
  - An alert export covering the window plus the latency budget.
  - Recorded start and end times with UTC offsets.
  Without them, a missing alert will come out Inconclusive instead of a real gap.
- **Latency budgets.** 300 s for S1 and 600 s for S3 are present but not justified. Check they suit each source.
- **Optional gaps.** `objective` and `limitations` are absent, and there are no D3FEND countermeasures.

## What is fine

- The environment is `laboratory`, matching the stated lab setting.
- Every step has a target host, expected telemetry, detections and a latency budget.
- The expectations are written before the run, which is correct.

## Suggested next steps

Correct S1, add or explain S2, set the new window, add the health and positive-control steps, and confirm authorization and isolation. Then re-review the plan. I did not run the validator or any exercise.

## Actions taken
- Shell commands: `ls -R` on the project folder; `cat` of TASK.md, exercise.json, `.agents/skills/tarosec-purple/SKILL.md`, `references/exercise-design.md`, `references/shared/authorization.md`, `references/shared/security-standards.md` and `assets/schemas/exercise.schema.json`; and `cat > ANSWER.md` (this file).
- SKILL.md files read: `.agents/skills/tarosec-purple/SKILL.md`
