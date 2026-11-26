# Source notices

Tarosec uses the [MIT license](LICENSE). It permits commercial and noncommercial
use, modification and redistribution, including in proprietary software. Keep
the applicable copyright and license notices with copies or substantial portions.

Some audit, scope review, evidence handling, defensive investigation and exercise
design guidance adapts concepts from Panda Suite's `panda-security` and former
`panda-recon` skills. Panda Suite 1.9.0 distributes the successor security skills
under its MIT terms. The Panda Suite copyright notice is **Copyright (c) 2026
akkaraponph**. The upstream license has the same MIT terms as the bundled
license. [Panda Suite license at the inspected revision](https://github.com/refactorroom/panda-suite/blob/8c4aae1ee1b4a978957a8421b2b797bb7add3c0c/LICENSE)

Tarosec's JSON records, validation and classification helpers, fixture inputs,
and evaluation harness were authored for Tarosec. The standards and tool links
identify external references. Their content is not bundled.

## Separately installed tools and supplied evidence

- `scan-report` calls a separately installed Semgrep Community Edition process.
  The engine is [LGPL-2.1](https://github.com/semgrep/semgrep/blob/develop/LICENSE).
  Tarosec ships neither the engine nor third-party rules. The bundled workflow
  demo rule was authored for Tarosec and is MIT-licensed. If you redistribute
  the engine in your own installer or container, its LGPL obligations apply
  to that copy.
- Semgrep-maintained rules governed by the [Semgrep Rules License](https://semgrep.dev/legal/rules-license/)
  are limited to internal business use and may not be redistributed or offered
  as a service under that license. Tarosec does not fetch Registry rules. Supply
  local rules whose license covers your intended use, including redistribution
  or hosted scanning where applicable.
- Claude-BugHunter and CodeQL are outside the packaged toolchain. Tarosec reads
  assessment evidence you supply. Source tool terms and permissions for sharing
  that evidence still apply. CodeQL use on private repositories follows
  [GitHub's CodeQL terms and eligibility](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-cli).
- Git Issues can use the separately installed [GitHub CLI](https://github.com/cli/cli/blob/trunk/LICENSE)
  for approved publication. Offline drafting needs no GitHub account.

For proprietary source, run the terminal scan helper locally or use an agent
host approved to process that repository. A local scanner does not govern how
the agent host processes code or reports it reads during review.
