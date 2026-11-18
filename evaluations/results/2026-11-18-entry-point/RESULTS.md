# Entry point evaluation on 2026-11-18

Three paired cases ran in fresh Codex CLI sessions using gpt-6.1-sol at low
reasoning effort. Both arms had identical task files and a local read-only
permission profile. Web search and delegation were disabled. The profile denied
reads from the source repository. The skill arm received all six skills, except
T2 which received only the entry point.

| Case | Baseline | Skill arm |
| --- | --- | --- |
| T1, local project with hostname | Recommended a local source review and called the workflow name unverified. | Read the entry point, ran its helper and opened Audit. Selected quick read-only Audit. |
| T2, entry point only | Explained that a specialist was needed. Could not verify the name. | Ran the helper and named the missing `tarosec-simulate` selector. Explained the read-only fallback. |
| N1, conceptual question | Answered without calling tools. | Answered without calling tools or reading a skill. |

All six runs completed. The stored responses and shell traces show no host
contact, assessment execution, installation, or writes. The new entry point
made the workflow names and missing-dependency response verifiable in these
cases. Both arms interpreted the scope safely. This single pair per case does
not establish a general behavior improvement.

Both security cases also encountered an inherited reference to an absent
`RTK.md`. The JSON files record failed reads, final answers, and token counts.
Token counts include different tool call and cache behavior. This sample
does not establish an overhead effect.

A fresh Codex session also ran the exact `$tarosec simulate suspicious-login`
request with a writable disposable workspace and network access disabled. It
selected Simulate, generated five synthetic events, and reported Inconclusive
because independent observations were absent. The output matched the repository
example byte for byte. [Demo trace](simulation-demo.json) ·
[Captured report](../../../examples/simulation/suspicious-login/report.md)
