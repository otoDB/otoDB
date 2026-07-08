# AGENTS.md

## Commit conventions

- This project does **not** follow Conventional Commits.
- Write commit messages in plain, descriptive English that clearly explains what changed and why.
- When an agent creates a git commit, it **must** include itself as a co-author in the commit message using a `Co-Authored-By:` trailer. For example:
  ```
  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  ```

## Pull request conventions

- When creating a PR that is clearly related to a specific issue — either from the branch name (e.g. `SnO2WMaN/issue693`) or other context — always include a closing keyword like `close #693` in the PR body so that the issue is automatically closed when the PR is merged.

## Tooling preferences

- Use `jq` (not `python3 -c`) when querying or inspecting JSON files.

## Editing CLAUDE.md

- `CLAUDE.md` files in this repo (root and per-directory, e.g. `frontend/CLAUDE.md`) are symlinks to `AGENTS.md`. Writing through the symlink fails, so check with `ls -la` first and edit the real `AGENTS.md` target directly.
