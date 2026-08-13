# Working conventions

- Never commit or push directly to `main`. Always create a feature branch for any change and push that branch instead. Open a PR if the user wants the change merged.
- Always show proposed code changes to the user before applying them. This applies to edits to the codebase itself (source files, config, docs). It does not apply to generated output files that a skill is instructed to write as part of its normal operation (e.g. `issues/<KEY>/summary.md` written by the `/support` skill) — write those directly, no confirmation needed.
