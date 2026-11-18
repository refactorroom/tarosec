# Install Tarosec

Run the installer from the project directory. The Agent Skills CLI needs Node.js.
Python 3.10 or later is only required for the included Python helpers.

## Project installation

Use `--skill '*'` for the complete entry-point experience. This command installs
the entry point and simulation without the other specialists.

```bash
npx skills add /path/to/tarosec --skill tarosec tarosec-simulate --agent codex claude-code --copy -y
```

```bash
npx skills@1.9.0 add /path/to/tarosec --list
npx skills@1.9.0 add /path/to/tarosec --skill tarosec-purple --agent codex claude-code --copy -y
npx skills@1.9.0 list --agent codex claude-code
npx skills@1.9.0 remove tarosec-purple --agent codex claude-code -y
```

Select all skills with `--skill '*'`, or substitute `tarosec-audit`,
`tarosec-red`, or `tarosec-blue` for Purple. The CLI installs Codex skills under
`.agents/skills/`. With `--copy` and the Claude Code agent selected, it also
copies them into `.claude/skills/`. Restart the agent after installing.

## Report specialist

Install from a checkout containing Report.

```bash
npx skills add /path/to/tarosec --skill tarosec-report --agent codex --copy -y
```

The GitHub selector is `npx skills add refactorroom/tarosec --skill tarosec-report` once the remote branch includes the skill.

## GitHub installation and updates

The public `refactorroom/tarosec` repository contains all six skills.

```bash
npx skills@1.9.0 add refactorroom/tarosec --list
npx skills@1.9.0 add refactorroom/tarosec --skill tarosec-audit --agent codex -y
npx skills@1.9.0 update --project
```

Select either new skill with
`npx skills add refactorroom/tarosec --skill tarosec` or
`npx skills add refactorroom/tarosec --skill tarosec-simulate`. Both selectors
were verified against GitHub using Skills CLI 1.9.0.

For a local source, reinstall from the updated checkout. For an intentional
user-level installation, add `--global` to `add`, `list`, `update`, or `remove`.
The release checks used disposable project directories. They did not install a
global copy.

## npm package

Install the published package and sync its skills into your Codex project.

```bash
npm install tarosec@0.1.0
npx skills@1.9.0 experimental_sync --copy --agent codex
```

The first command downloads the six skill directories and Python helpers into
`node_modules/tarosec/skills/`. The second copies skills from your project's npm
dependencies into `.agents/skills/` for Codex. Run the sync again after updating
the package. For a direct GitHub install, use `npx skills add refactorroom/tarosec`.

## Other installation paths

For a local Claude Code session, start with `claude --plugin-dir /path/to/tarosec`.
The explicit plugin command for Purple is `/tarosec:tarosec-purple`. For Codex, an
explicit invocation names the skill, for example `$tarosec-purple`, in the message.
A plain task can also match the description where the host supports automatic routing.

For another Agent Skills-compatible host, copy a whole directory from `skills/`
into its configured project skills folder. Include its `SKILL.md`, references,
schemas, scripts and notices. Check the host's documentation for discovery paths.

## Troubleshooting

- If `add --list` finds zero skills, confirm the source revision contains `skills/*/SKILL.md`.
- If the CLI lists a skill but the agent cannot find it, confirm the selected
  agent and its project root. Start a new session in that project.
- For Claude Code, choose either the project copy or the local plugin when checking routing.
- If a Python helper reports a missing schema, check that the full skill
  directory was copied. Paths in skill instructions resolve from that directory.

[Agent Skills specification](https://agentskills.io/specification) · [Vercel Skills CLI](https://github.com/vercel-labs/skills)
