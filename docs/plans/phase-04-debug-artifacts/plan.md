# Phase 04 — Debug Artifacts, Network Visibility, and Run Bundles Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Make browser automation debuggable and auditable by collecting screenshots, console logs, page errors, network summaries, traces, and downloads into safe run bundles.

**Architecture:** Introduce a `RunContext` per browser task/session, store artifacts under `/data/runs/<run_id>`, attach Playwright event listeners for console/network/downloads, and expose tools to list/export run artifacts. Sensitive values must be redacted before logs are persisted or returned.

**Tech Stack:** Playwright tracing/events, Python `json`, `zipfile`, `datetime`, optional `structlog`, FastMCP tools, `unittest`.

---

## Current baseline

- `take_screenshot` writes PNG files directly under `/data`.
- `list_artifacts` lists only top-level files under `/data`.
- Downloads can be read if the caller knows the file name, but download event tracking is not explicit.
- No console logs, network logs, HAR, trace, failure screenshot, or run grouping exists.

## Acceptance criteria

- Every browser session can have a `run_id` and run directory.
- Screenshots, downloads, traces, console logs, and network summaries are grouped by run.
- Tool failures can capture a failure screenshot when enabled.
- Sensitive headers and likely secrets are redacted.
- Users can list runs and export a run bundle.
- Existing top-level artifact tools remain backward compatible or are clearly deprecated.

---

## Task 1: Add run directory model

**Objective:** Centralize artifact paths around a run context.

**Files:**

- Create: `src/runs.py`
- Modify: `src/browser.py`
- Test: `tests/test_runs.py`
- Docs: `docs/src/content/docs/features.md`

**Directory layout:**

```text
/data/runs/<run_id>/
  metadata.json
  screenshots/
  downloads/
  traces/
  logs/
    console.jsonl
    page-errors.jsonl
    network.jsonl
```

**Run ID format:**

```text
YYYYMMDD_HHMMSS_<short-random>
```

**Functions:**

```python
def create_run(name: str | None = None) -> RunContext: ...
def active_run() -> RunContext: ...
def resolve_run_file(run_id: str, relative_path: str) -> Path: ...
```

Path traversal protection is mandatory.

---

## Task 2: Attach console and page-error listeners

**Objective:** Capture JavaScript console output and uncaught page errors.

**Files:**

- Modify: `src/browser.py`
- Create: `src/events.py`
- Test: `tests/test_event_redaction.py`
- Docs: `docs/src/content/docs/tools.md`

**Captured fields:**

```json
{
  "timestamp": "...",
  "type": "error",
  "text": "redacted message",
  "location": {"url": "...", "line": 12, "column": 4}
}
```

**Redaction:**

Redact patterns:

- `Authorization: Bearer ...`
- `api_key=...`
- `token=...`
- strings matching common secret prefixes
- cookie header values

---

## Task 3: Add network summary logging

**Objective:** Help diagnose failed loads/API calls without dumping sensitive bodies.

**Files:**

- Modify: `src/browser.py`
- Modify: `src/events.py`
- Test: `tests/test_network_logging.py`
- Docs: `docs/src/content/docs/tools.md`

**Captured fields:**

```json
{
  "timestamp": "...",
  "method": "GET",
  "url": "https://example.com/api/items",
  "status": 200,
  "resource_type": "xhr",
  "duration_ms": 123
}
```

Do not capture request/response bodies in the first version.

Add config:

```text
BROWSER_MCP_NETWORK_LOGGING_ENABLED=true
BROWSER_MCP_NETWORK_LOG_MAX_ENTRIES=1000
```

---

## Task 4: Add Playwright trace support

**Objective:** Allow users to capture full trace bundles for difficult debugging sessions.

**Files:**

- Modify: `src/browser.py`
- Create: `src/tools/debug.py`
- Modify: `src/tools/__init__.py`
- Test: `tests/test_debug_tool_contracts.py`
- Docs: `docs/src/content/docs/tools.md`

**Tools:**

```text
start_trace(screenshots: bool = true, snapshots: bool = true)
stop_trace()
```

Trace output path:

```text
/data/runs/<run_id>/traces/trace.zip
```

Return metadata only:

```json
{"ok": true, "run_id": "...", "file_name": "trace.zip", "size_bytes": 12345}
```

---

## Task 5: Track downloads explicitly

**Objective:** Make downloaded files discoverable and safely retrievable.

**Files:**

- Modify: `src/browser.py`
- Modify: `src/tools/artifacts.py`
- Test: `tests/test_download_contracts.py`
- Docs: `docs/src/content/docs/tools.md`

**Tools:**

```text
list_downloads(run_id: str | None = None)
get_download(run_id: str, file_name: str)
```

Move or save downloads into:

```text
/data/runs/<run_id>/downloads/<safe-file-name>
```

Add size limit config:

```text
BROWSER_MCP_MAX_DOWNLOAD_MB=50
```

---

## Task 6: Capture failure screenshot in tool guard

**Objective:** Automatically collect debugging evidence when a browser tool fails.

**Files:**

- Modify: `src/tools/contracts.py`
- Modify: browser tool registrations as needed
- Test: `tests/test_failure_artifacts.py`

Because `mcp_tool_guard` currently has no access to runtime, add a runtime-aware guard factory:

```python
def mcp_browser_tool_guard(runtime: BrowserRuntime):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return ensure_ok(await func(*args, **kwargs))
            except Exception as error:
                screenshot = await runtime.capture_failure_screenshot_safe()
                return {**error_payload(error), "failure_screenshot": screenshot}
        return wrapper
    return decorator
```

Keep the existing `mcp_tool_guard` for pure tools.

---

## Task 7: Add run listing and export tools

**Objective:** Make evidence bundles easy to inspect and share.

**Files:**

- Create: `src/tools/runs.py`
- Modify: `src/tools/__init__.py`
- Test: `tests/test_run_tools.py`
- Docs: `docs/src/content/docs/tools.md`

**Tools:**

```text
list_runs(limit: int = 20)
get_run_file(run_id: str, relative_path: str)
export_run_bundle(run_id: str)
```

`export_run_bundle` creates:

```text
/data/runs/<run_id>/<run_id>.zip
```

---

## Final phase verification

Run:

```bash
python3 -m compileall -q src tests main.py
python3 -m unittest discover -s tests -p "test_*.py"
docker build -t browser-mcp:phase-04 .
```

Manual smoke test:

1. Start a run.
2. Navigate to a page.
3. Trigger console and network events.
4. Take screenshot.
5. Export run bundle.
6. Confirm bundle contains metadata, logs, and screenshots with no raw secrets.
