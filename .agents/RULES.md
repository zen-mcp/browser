# Rules

These rules apply to AI agents and human contributors changing runtime behavior.

## Mandatory Coding Discipline

Agents must apply `.agents/skills/guidelines/SKILL.md` before writing,
reviewing, or refactoring code.

## Safety Gates

- File reads for artifacts/downloads must call
  `BrowserRuntime.resolve_file_path()`.
- Artifact writes must call `BrowserRuntime.build_artifact_path()`.
- Do not write outside the configured data directory.
- Do not log, return, or persist secrets: API keys, cookies, auth headers,
  passwords, TOTP secrets, or form credentials.
- Runtime browser sessions must remain headless in committed code.
- Tool code should not make arbitrary outbound HTTP calls outside browser
  automation flows.

## MCP Tool Contract

- New or updated MCP tools return a `dict` with `ok: bool`.
- Expected tool-boundary failures return `{ok: false, error, error_type}`.
- Preserve legacy output contracts unless the task explicitly allows a breaking
  change.
- Keep `browse_and_act` string-compatible; use `browse_and_act_structured` for
  structured agent results.
- Tool descriptions should state what the tool does, when to use it, and the
  most important output fields.

## Python Rules

- Use async Playwright APIs only.
- Prefer explicit types for public helpers and tool signatures.
- Catch broad exceptions only at the MCP boundary helper, not deep inside
  runtime logic.
- Keep comments sparse and useful.

## Approval Needed

- Renaming or removing an MCP tool.
- Changing `BrowserRuntime` lifecycle or session sharing behavior.
- Adding new environment variables.
- Bumping major versions of `browser-use`, Playwright, or MCP SDK.
- Changing package manager or CI quality gate policy.
