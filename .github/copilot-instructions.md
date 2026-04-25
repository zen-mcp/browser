# Copilot Instructions for browser-mcp

Use `AGENTS.md` as the primary project instructions. These notes mirror the
core rules for GitHub Copilot.

- For coding, review, and refactor tasks, follow `.agents/skills/karpathy-guidelines/SKILL.md`.
- This project is an MCP server for browser automation using Playwright and `browser-use`.
- Runtime code lives in `src`; `main.py` is a thin entrypoint.
- Keep browser I/O async-first and use Playwright async APIs.
- New or updated MCP tools should return `dict` payloads with `ok: bool`.
- Preserve the legacy string return contract of `browse_and_act`; use
  `browse_and_act_structured` for structured agent results.
- File reads for artifacts/downloads must go through
  `BrowserRuntime.resolve_file_path()`.
- Artifact writes must go through `BrowserRuntime.build_artifact_path()`.
- Never log or return API keys, cookies, auth headers, passwords, or TOTP
  secrets.
- Before changing multi-step browser workflows, check `.agents/SKILLS.md`.
- Run `python3 -m unittest discover -s tests -p "test_*.py"` for validation.
