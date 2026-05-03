# AGENTS.md

## Commit conventions

- This project does **not** follow Conventional Commits.
- Write commit messages in plain, descriptive English that clearly explains what changed and why.

## Pull request conventions

- When creating a PR that is clearly related to a specific issue — either from the branch name (e.g. `SnO2WMaN/issue693`) or other context — always include a closing keyword like `close #693` in the PR body so that the issue is automatically closed when the PR is merged.

## Tooling preferences

- Use `jq` (not `python3 -c`) when querying or inspecting JSON files.
- 