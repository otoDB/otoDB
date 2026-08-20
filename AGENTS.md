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

## Agent configuration

- `AGENTS.md` is the canonical shared instruction file. Keep `CLAUDE.md` as a relative symlink to the `AGENTS.md` in the same directory.
- Put personal or machine-specific instructions in the git-ignored `AGENTS.override.md`. Keep `CLAUDE.local.md` as a relative symlink to `AGENTS.override.md` so Codex and Claude Code read the same local instructions.
- Shared Claude Code settings live in `.claude/settings.json`; personal permissions and overrides belong in the git-ignored `.claude/settings.local.json`.
- Keep `.mcp.json` and `.codex/config.toml` aligned when adding or changing shared MCP servers. The former configures Claude Code and the latter configures Codex.

## Agent workflow

- For any task large enough to span more than one area of the codebase, plan first and implement second, with different models on each side:
  1. **Plan with Fable** — spawn an agent with `model: fable` to survey the codebase and produce the overall plan (work breakdown, file-level scope of each piece, and the order/dependencies between them).
  2. **Implement with Opus** — hand each piece of that plan to its own Opus agent. Give every agent the plan's scope for its piece so the pieces stay disjoint, and run independent pieces concurrently.

## MCP servers

`.mcp.json` and `.codex/config.toml` at the repository root define the MCP servers agents are expected to use. Claude Code enables the servers from `.mcp.json` via `enabledMcpjsonServers` in `.claude/settings.json`; Codex reads `.codex/config.toml`.

### `storybook` — writing and testing stories

Provided by the `@storybook/addon-mcp` addon registered in `frontend/.storybook/main.ts`, served over HTTP at `http://localhost:6006/mcp`.

- **The Storybook dev server must be running for this server to work.** Start it first with `bun run storybook:agent` from `frontend/` (see `frontend/AGENTS.md`). When Storybook is not running, the server is simply unreachable.
- Use `get-storybook-story-instructions` before writing or editing components and stories, `preview-stories` after any change that affects how the UI looks, and `run-story-tests` to validate.

### `playwright` — driving a browser and taking screenshots

- Runs headless Chrome for Testing (`--browser chromium`) in an isolated profile at a 1280x720 viewport.
- Screenshots and other artifacts are written to `.playwright-mcp/`, which is git-ignored. Note that `--output-dir` only applies when the tool call omits a filename; passing an explicit relative `filename` resolves it against the process working directory instead, which litters the repository. Prefer omitting `filename`.

### `chrome-devtools` — performance and network analysis

- Use this only when you need what Playwright cannot give you: Core Web Vitals, Lighthouse audits, performance traces, or detailed network/console inspection. For ordinary navigation and screenshots, use `playwright`.
- **Requires a real Google Chrome installation** (`/opt/google/chrome/chrome` on Linux). It does not download a browser for you. On Arch, install the AUR `google-chrome` package.

### Browser dependencies on Linux

The Chromium builds Playwright downloads are dynamically linked against system libraries that a minimal Linux install does not have. `playwright install-deps` only emits `apt-get` commands and is useless on non-Debian distributions. On Arch, install these instead:

```
paru -S --needed libxcomposite libxdamage libxfixes libxrandr libxkbcommon alsa-lib at-spi2-core mesa
```

Verify with `ldd ~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome | grep "not found"` — it should print nothing. When these are missing, the browser fails to launch with the unhelpful message `Target page, context or browser has been closed`.
