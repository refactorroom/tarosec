# Contributing

- Edit shared guidance only in `references/`, `schemas/` or `scripts/validate_record.py`,
  then run `python3 scripts/sync_shared.py`.
- Keep each SKILL.md under ~100 lines; move conditional detail to the skill's `references/`.
- Every description states when to use the skill and what it is **not** for.
- A behavior change needs an evaluation case (`evaluations/fixtures/` + a
  `evaluations/reviewer/cases.json` entry) that fails without it. Keep the answer key
  out of the fixtures.
- Run `python3 -B -m unittest discover -s tests` before opening a PR.
- New skills (intel, incident, threat, posture) need a case showing that the
  separate trigger helps, compared with a section in an existing skill.
