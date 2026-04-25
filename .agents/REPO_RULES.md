# Repo Rules

## Local Layout

- `main.py` injects `src` into `sys.path`; tests that import runtime modules may
  need to do the same.
- Runtime data is under `/data` in Docker and `./data` on the host.
- `data/`, docs build output, Python caches, and docs `node_modules/` are
  ignored.
- The docs site is Astro + Starlight under `docs/`; do not mix old MkDocs paths
  back in.

## Browser Gotchas

- Use `headless=True` and Chromium flags `--no-sandbox` and
  `--disable-dev-shm-usage` for container parity.
- Direct Playwright tools and the browser-use agent use separate sessions. Do
  not assume cookies or page state are shared between them.
- Use selectors that are resilient enough for agent-driven tasks, and return
  evidence with screenshots when a flow is ambiguous.
- Timeouts should be explicit at the tool boundary. Avoid unbounded waits.

## Artifact Gotchas

- `build_artifact_path(prefix, extension)` sanitizes names and adds a timestamp.
- `resolve_file_path(requested_name, category)` blocks traversal and absolute
  paths. Keep this behavior covered by tests.
- Do not add artifacts or downloads to git.

## Testing Gotchas

- The local command is `python3 -m unittest discover -s tests -p "test_*.py"`.
- Existing tests stub heavy browser dependencies; keep unit tests lightweight.
- Add integration/e2e browser tests only when the change really needs a live
  browser.
