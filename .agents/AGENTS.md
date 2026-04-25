# AGENTS.md - browser-mcp

This file is the source of truth for AI coding agents working in this repo.
Keep it concise, update it when project commands or safety rules change, and
prefer linking to `.agents/` for details.

## Project

`browser-mcp` is an MCP server that exposes browser automation over HTTP/SSE.
It combines direct Playwright tools with a `browser-use` agent flow for complex
multi-step browser tasks.

## Architecture

Read `.agents/ARCHITECTURE.md` before changing runtime lifecycle, tool
registration, or artifact handling.

Main runtime pieces:

- `main.py`: thin local/container entrypoint that adds `src` to `sys.path`.
- `src/server.py`: creates `FastMCP`, loads settings, wires runtime, LLM, tools.
- `src/browser.py`: owns Playwright/browser-use lifecycle and data path helpers.
- `src/tools/`: MCP tools split by domain.
- `tests/`: lightweight unit and validation tests.

## Before Work

1. For any code writing, review, or refactor, read and apply
   `.agents/skills/guidelines/SKILL.md`.
2. Read `.agents/RULES.md` for safety and MCP boundary rules.
3. Read `.agents/REPO_RULES.md` for project-specific gotchas.
4. For multi-step browser workflows, check `.agents/SKILLS.md` first.
5. If adding or changing a skill, update `.agents/SKILLS.md` and keep tests
   passing.

## Commands

| Action | Command |
| --- | --- |
| Install deps | `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` |
| Run server | `python3 main.py` |
| Docker run | `docker compose up --build` |
| Unit tests | `python3 -m unittest discover -s tests -p "test_*.py"` |
| Runtime tests only | `python3 -m unittest tests/test_browser_runtime.py` |
| Syntax check | `python3 -m compileall -q src tests main.py` |

Do not introduce `pyproject.toml`, `uv`, ruff, mypy, or OpenTelemetry in this
foundation pass unless a later task explicitly asks for it.

## Code Rules

- Python 3.11+ style, async-first for browser and MCP tool I/O.
- Keep direct Playwright access behind `BrowserRuntime`.
- MCP tools should return `dict` payloads with `ok: bool` unless preserving an
  existing legacy contract.
- Errors should be converted at the MCP tool boundary to `{ok: false, error,
  error_type}`. Helper/internal functions may raise normally.
- Keep `browse_and_act` string-compatible for existing clients. Add structured
  sibling tools rather than breaking that return type.
- Use clear tool descriptions/docstrings so MCP clients can choose tools well.
- Avoid cross-imports between `src/tools/*` modules except shared lightweight
  helpers.

## Safety Boundaries

- All artifact/download file reads must go through
  `BrowserRuntime.resolve_file_path()`.
- All artifact writes must use `BrowserRuntime.build_artifact_path()`.
- Never commit `headless=False` in runtime code.
- Never log or return raw cookies, auth headers, API keys, passwords, or TOTP
  secrets.
- Do not write runtime artifacts to paths outside `/data` in the container or
  `./data` on the host.
- Do not add outbound HTTP from tool code outside Playwright/browser-use flows.

## AI-First Assets

- `.agents/`: repo-local AI-first architecture, rules, skills, and commands.
- `.cursor/rules/`: Cursor project rules derived from this file.
- `.github/copilot-instructions.md`: Copilot mirror of the core instructions.
- `skills/`: deprecated compatibility placeholder; canonical skills live in
  `.agents/skills/`.

## Change Discipline

- The worktree may contain user changes. Do not revert unrelated edits.
- Keep AI-first docs and runtime contract changes scoped.
- Update tests with behavior changes, especially MCP output shape or path
  safety.
