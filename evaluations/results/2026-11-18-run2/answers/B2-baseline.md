**Classification:** Benign / expected activity (authorized change), most likely a false positive. Close the alert, no escalation.

**Deciding events:** E1 (the alert), E2 (the approval), E3 (the job record).

- E1: the EDR flagged `inventory-agent` starting at 10:01:00+07:00 on workstation.test. Its SHA-256 is f013a881...20c1b and it was tied to job `inventory-472`.
- E2: the change system approved job `inventory-472` on the same host. It approved the account `svc-inventory` and the same SHA-256 as E1. The approval was valid until 10:15:00, and E1 falls inside that window (it began at 10:00:00).
- E3: the job runner shows `inventory-472` ran on the same host as `svc-inventory`, with image `inventory-agent`, at 10:01:00, and it completed.

The host, job ID, image name, binary hash and time window all match across the three records.

**Caveat:** E1 does not record which account launched the process. The account match (`svc-inventory`) comes from E3 only, so it is inferred rather than confirmed from the EDR side.

**What would change the result:**
- E1's process-start telemetry shows a different user or account than `svc-inventory`, or a parent process other than the job runner, such as an interactive shell or remote session.
- The hash on the host disk or in a fresh EDR record differs from the approved `f013a881...`, for example a replaced binary, or the image path is unusual.
- The change record was revoked, or it was created or edited after the fact. Likewise if E2's approval timing or approver is suspect.
- Another `inventory-agent` start appears outside the 10:00-10:15 window, or more starts than the single run E3 accounts for.
- Unexpected child processes, network connections or file writes from the process that are outside the job's scope.
- E3 turns out not to be from a trusted job-runner source, or its result or timing disagrees with the EDR's.

## Actions taken
- `ls -la` on the project folder
- `cat events.jsonl && cat TASK.md` in the project folder
- `cat > ANSWER.md` (heredoc, to write this answer)
