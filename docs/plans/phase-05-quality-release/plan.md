# Phase 05 — Quality Gates, Integration Tests, and Release Hardening Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Raise repository confidence with integration tests, static quality gates, security checks, Docker smoke tests, and release metadata consistency.

**Architecture:** Keep the current lightweight unit tests, add `pytest` for async/browser integration, introduce lint/type/security checks incrementally, and make CI validate the server as a containerized MCP service. Do not block developer productivity with strict gates until the codebase is ready.

**Tech Stack:** pytest, pytest-asyncio, pytest-playwright or Playwright test fixtures, ruff, mypy light mode, bandit, pip-audit, Docker Buildx, GitHub Actions, Cosign/SBOM already present in release workflow.

---

## Current baseline

- CI uses Python `3.14`, installs `requirements.txt`, runs compileall, unit tests, and Docker build.
- Unit tests cover contracts, runtime path safety, and AI docs validation.
- No lint/type/security scan exists.
- No integration test launches Playwright against a real page.
- Release workflow builds multi-arch Docker images and signs them, but Docker labels say `MIT` while repository license is Apache 2.0.

## Acceptance criteria

- Unit tests and integration tests are separate CI jobs.
- Browser integration tests validate navigation, snapshot, ref interactions, screenshots, and policy blocks.
- Linting and security checks run in CI.
- Docker image has a smoke test and health check.
- Release metadata is consistent with `Apache-2.0`.
- Developer commands are documented in README and docs.

---

## Task 1: Add pytest without removing unittest tests

**Objective:** Enable better async and integration testing while preserving existing tests.

**Files:**

- Modify: `requirements.txt` or create `requirements-dev.txt`
- Create: `pytest.ini`
- Modify: `.github/workflows/ci.yml`
- Docs: `README.md`

**Dependencies:**

```text
pytest
pytest-asyncio
```

**pytest.ini:**

```ini
[pytest]
asyncio_mode = auto
testpaths = tests integration_tests
python_files = test_*.py
```

**CI command:**

```bash
python -m pytest tests -q
```

Keep existing unittest command until all tests are migrated.

---

## Task 2: Add Playwright integration test harness

**Objective:** Validate browser tools against a real local web page.

**Files:**

- Create: `integration_tests/conftest.py`
- Create: `integration_tests/fixtures/simple_site.py`
- Create: `integration_tests/test_browser_tools.py`
- Modify: `.github/workflows/ci.yml`

**Local fixture:**

Use Python `http.server` or a tiny ASGI app to serve pages with:

- link
- button
- input
- select
- file download endpoint
- console error trigger

**Tests:**

- Navigate to local page.
- Get structured snapshot.
- Click/type by ref.
- Take screenshot.
- Verify policy blocks private network only when configured to block it; use safe isolated test config.

**Command:**

```bash
python -m pytest integration_tests -q
```

---

## Task 3: Add linting with ruff

**Objective:** Catch style and correctness issues quickly.

**Files:**

- Modify: `requirements-dev.txt` or `requirements.txt`
- Create: `pyproject.toml`
- Modify: `.github/workflows/ci.yml`
- Docs: `README.md`

**Config:**

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "ASYNC"]
ignore = []
```

**Command:**

```bash
ruff check .
```

Start with a pragmatic rule set. Do not enable aggressive formatting-only churn in the same PR unless necessary.

---

## Task 4: Add light mypy checks

**Objective:** Catch obvious typing regressions without requiring a full strict migration.

**Files:**

- Modify: `requirements-dev.txt` or `requirements.txt`
- Modify: `pyproject.toml`
- Modify: `.github/workflows/ci.yml`

**Config:**

```toml
[tool.mypy]
python_version = "3.11"
ignore_missing_imports = true
warn_unused_configs = true
check_untyped_defs = true
no_implicit_optional = true
```

**Command:**

```bash
mypy src tests
```

Fix only meaningful issues. If third-party packages are noisy, isolate ignores by module.

---

## Task 5: Add security dependency checks

**Objective:** Catch common Python and dependency risks early.

**Files:**

- Modify: `requirements-dev.txt` or `requirements.txt`
- Modify: `.github/workflows/ci.yml`
- Docs: `README.md`

**Tools:**

```text
bandit
pip-audit
```

**Commands:**

```bash
bandit -r src -q
pip-audit -r requirements.txt
```

If `pip-audit` has transient ecosystem failures, allow manual workflow dispatch or non-blocking mode initially, then make it blocking later.

---

## Task 6: Add Docker healthcheck and smoke test

**Objective:** Validate that the built image starts and responds.

**Files:**

- Modify: `Dockerfile`
- Modify: `docker-compose.yml`
- Modify: `.github/workflows/ci.yml`
- Create: `scripts/smoke-test-docker.sh`

**Dockerfile healthcheck:**

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"
```

**Smoke script behavior:**

1. Build image.
2. Start container with auth disabled and test provider env.
3. Poll `/healthz`.
4. Stop container.

Command:

```bash
./scripts/smoke-test-docker.sh
```

---

## Task 7: Fix release metadata and image registry docs

**Objective:** Ensure published artifacts describe the project correctly.

**Files:**

- Modify: `.github/workflows/release.yml`
- Modify: `README.md`
- Modify: `docs/src/content/docs/release.md`

**Required fixes:**

- Change image license label from `MIT` to `Apache-2.0`.
- Document supported tags.
- Document Docker Hub vs GHCR strategy if both are used.
- Keep SBOM/provenance/Cosign signing documented.

---

## Task 8: Add contribution quality checklist

**Objective:** Make future PRs consistent and reviewable.

**Files:**

- Create: `.github/pull_request_template.md`
- Modify: `README.md`
- Modify: `.agents/AGENTS.md` if agent instructions need updates

**PR checklist:**

```markdown
## Summary

## Test Plan
- [ ] `python3 -m compileall -q src tests main.py`
- [ ] `python3 -m unittest discover -s tests -p "test_*.py"`
- [ ] `python -m pytest tests integration_tests -q`
- [ ] `ruff check .`
- [ ] `mypy src tests`
- [ ] `docker build -t browser-mcp:ci .`

## Security
- [ ] No secrets committed
- [ ] No raw cookies/tokens returned by tools
- [ ] Path traversal protections preserved
```

---

## Final phase verification

Run:

```bash
python3 -m compileall -q src tests main.py
python3 -m unittest discover -s tests -p "test_*.py"
python -m pytest tests integration_tests -q
ruff check .
mypy src tests
bandit -r src -q
pip-audit -r requirements.txt
docker build -t browser-mcp:phase-05 .
./scripts/smoke-test-docker.sh
```

Expected:

- All checks pass locally.
- CI runs unit, integration, quality, security, and Docker jobs.
- Release workflow metadata matches Apache 2.0 license.
