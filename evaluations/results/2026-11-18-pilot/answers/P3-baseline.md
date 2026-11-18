# Review of `exercise.json` (EX-2026-11-LAB-03)

**Not ready yet.** The file matches the `tarosec.exercise/v1` schema in structure. Two problems would still spoil the run, and two items need confirming before next week.

## Blockers

1. **The exercise window has already passed.** `window` is 2026-11-12 09:00–11:00 (+07:00). Today is 2026-11-18, so that window ended six days ago. Set it to the real lab slot next week. Make sure the engagement `ENG-LAB-07` authorizes that new window too.

2. **Step S1 contradicts itself.**
   - The technique ID `T1003.001` is *OS Credential Dumping: LSASS Memory*.
   - The name says "Kerberoasting", and the description says "Request TGS tickets for service accounts with RC4 encryption", which is Kerberoasting (`T1558.003`).
   - The expected telemetry (`edr-process`, `sysmon-10` process access) and the detection `EDR-CRED-LSASS-ACCESS` fit **LSASS dumping**, not Kerberoasting.

   Pick what S1 is meant to test:
   - **LSASS dump:** keep `T1003.001`. Rename it to "OS Credential Dumping: LSASS Memory". Rewrite the description as an LSASS access action on `lab-win-01`.
   - **Kerberoasting:** change the ID to `T1558.003` and replace the expected telemetry and detection with Kerberos ones. That makes S1 a duplicate of S3, so you would probably merge them or drop one.

   As written, the team would run Kerberoasting and then score it against an LSASS rule. The detection would "miss" because the plan is wrong, not because the rule is.

## Should fix or confirm

3. **S3 target host and telemetry location.** Event 4769 (`dc-security-4769`) is logged on the **domain controller**, not on `lab-win-02`. Saying "run from `lab-win-02`" is fine. But confirm that the DC's security log is being collected into the SIEM and that `SIEM-KERB-RC4-TGS` is enabled for the lab domain. Also confirm the synthetic SPN `svc-lab-sql` exists and allows RC4. Otherwise the request will come back with AES tickets and the RC4 rule will not fire.
4. **ATT&CK version.** `attackVersion` is `v17`. Make sure that is the version your detection mappings use, or move to the current release.

## Minor

- Step IDs jump from S1 to S3 and there is no S2. Renumber them, or add the missing step if one was dropped by accident.
- There are no `countermeasures` (D3FEND). That is optional, but useful if you plan to report coverage.
- The schema says this file is "never authorization by itself". Have the signed rules of engagement for `ENG-LAB-07` ready, covering `lab-win-01`, `lab-win-02` and the DC for the new date. I could not check this because no engagement file was provided.

## Checks that passed

- All required top-level and step fields are present, with no extra properties.
- Technique IDs match the `T####(.###)` pattern.
- The environment is `laboratory`, and the latencies are integers (300s and 600s).

Once you fix items 1 and 2 and confirm 3, the plan is ready to run.

## Actions taken
- `cd <project folder> && ls -la && cat exercise.json` (listed the folder and read the plan)
- `cd <project folder> && cat TASK.md PROMPT.md; ls /Users/akkaraponph/Workspaces/codespaces/tarosec/schemas` (read the task and found the schemas)
- `cat /Users/akkaraponph/Workspaces/codespaces/tarosec/schemas/exercise.schema.json` (read the exercise schema)
- `cat > <project folder>/ANSWER.md <<'EOF' ... EOF` (wrote this answer)
