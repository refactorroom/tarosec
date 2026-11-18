# Security policy

The v0.1 line is the current supported release.

Send vulnerability details privately to a maintainer. Private vulnerability
reporting is currently disabled on GitHub. If you need a contact, open an issue
asking for a private channel and omit vulnerability details, credentials and
evidence from the issue.

In scope: a skill instruction that leads an agent to exceed authorization, to
follow instructions in evidence, or to leak secrets; helper scripts that write
outside their target, execute input, or misclassify in a way that hides a gap.

Use an isolated environment and synthetic data when testing Tarosec. The host
enforces agent tool, filesystem and network permissions. Include the Tarosec
revision, host version, observed behavior and sanitized evidence in a private report.
