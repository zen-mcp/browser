# Architecture

`browser-mcp` follows a small AI-first model:

1. MCP tools expose browser capabilities.
2. Skills describe repeatable multi-tool procedures.
3. Rules define safety and repository boundaries.

## Runtime Components

- `src/server.py` creates the `FastMCP` server, loads `Settings`, creates the
  LLM, instantiates `BrowserRuntime`, and registers tools.
- `src/browser.py::BrowserRuntime` owns Playwright lifecycle, browser-use
  session creation, artifact naming, and path resolution.
- `src/tools/*.py` registers MCP tools by domain: observation, navigation,
  interaction, artifacts, and agent-driven flows.
- `src/llm.py` creates the OpenAI-compatible LLM used by `browser-use`.
- `main.py` is a thin entrypoint for local and container runs.

## Data Flow

1. MCP client calls a tool through the SSE transport.
2. Tool obtains a Playwright page through `BrowserRuntime.get_page()` or a
   browser-use session through `BrowserRuntime.get_agent_browser()`.
3. Browser actions run headless Chromium.
4. Artifacts are written under `/data` through `build_artifact_path()`.
5. File reads and `/artifacts/{file_name}` resolve paths through
   `resolve_file_path()`.

## Boundaries

- Only `server.py` composes settings, runtime, LLM, and tool registration.
- Tool modules should not import from each other. Shared boundary helpers belong
  in lightweight shared modules.
- Runtime lifecycle changes require focused tests because they affect all tools.
- Skills are instructions for agents, not executable application code.

## Deferred Candidates

These are intentionally out of scope for the foundation pass:

- Moving dependency management from `requirements.txt` to `pyproject.toml`/uv.
- Adding ruff, mypy strict mode, or broader CI quality gates.
- Adding OpenTelemetry or production tracing.
- Replacing SSE with Streamable HTTP.
