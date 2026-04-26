# Phase 01 — Auth, Policy, and Configuration Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Add a secure access-control foundation for the Browser MCP server before expanding browser capabilities.

**Architecture:** Replace ad-hoc environment loading with typed settings, add optional bearer-token protection for HTTP/SSE routes, and introduce a reusable browser navigation policy that can block risky targets before Playwright navigates. Keep backward compatibility by allowing auth to be disabled explicitly for local development.

**Tech Stack:** Python 3.11+, FastMCP, Starlette middleware/hooks where available, Playwright, `pydantic-settings`, standard-library `ipaddress`, `urllib.parse`, `socket`, `unittest`.

---

## Current baseline

Relevant files:

- `src/server.py` creates `FastMCP("browser-use-node", host="0.0.0.0")` and runs SSE only.
- `src/config.py` currently uses a frozen dataclass and `python-dotenv`.
- `src/tools/navigation.py` calls `page.goto(url, wait_until="domcontentloaded")` without URL policy checks.
- `.env.example` documents provider and Docker variables only.
- No server-level auth middleware or policy validation exists yet.

## Acceptance criteria

- Server can require `Authorization: Bearer <token>` for MCP HTTP/SSE traffic and artifact downloads.
- Auth can be disabled for local development via `BROWSER_MCP_AUTH_ENABLED=false`.
- Navigation rejects unsupported schemes, private-network targets, and explicitly blocked domains before calling Playwright.
- Allowlist/blocklist configuration is documented and tested.
- Existing unit tests still pass.
- New tests cover config defaults, auth decisions, and URL policy behavior.

---

## Task 1: Add typed settings with pydantic-settings

**Objective:** Centralize server, auth, provider, browser, and policy configuration in one validated settings object.

**Files:**

- Modify: `requirements.txt`
- Replace: `src/config.py`
- Test: `tests/test_config.py`
- Modify: `.env.example`
- Modify: `docs/src/content/docs/configuration.md`

**Implementation notes:**

Add dependency:

```text
pydantic-settings
```

Create settings groups in `src/config.py`:

```python
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_base_url: str = Field(alias="OPENAI_BASE_URL")
    model_name: str = Field(default="gpt-4o-mini", alias="MODEL_NAME")

    mcp_host: str = Field(default="0.0.0.0", alias="MCP_HOST")
    mcp_port: int = Field(default=8000, alias="MCP_PORT")
    mcp_transport: str = Field(default="sse", alias="MCP_TRANSPORT")

    auth_enabled: bool = Field(default=True, alias="BROWSER_MCP_AUTH_ENABLED")
    auth_token: str | None = Field(default=None, alias="BROWSER_MCP_AUTH_TOKEN")

    allow_domains: list[str] = Field(default_factory=list, alias="BROWSER_MCP_ALLOW_DOMAINS")
    block_domains: list[str] = Field(default_factory=list, alias="BROWSER_MCP_BLOCK_DOMAINS")
    block_private_networks: bool = Field(default=True, alias="BROWSER_MCP_BLOCK_PRIVATE_NETWORKS")
    allow_file_urls: bool = Field(default=False, alias="BROWSER_MCP_ALLOW_FILE_URLS")

    @field_validator("mcp_transport")
    @classmethod
    def validate_transport(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in {"sse", "streamable-http", "stdio"}:
            raise ValueError("MCP_TRANSPORT must be sse, streamable-http, or stdio")
        return normalized

    @field_validator("auth_token")
    @classmethod
    def validate_auth_token(cls, value: str | None, info):
        return value.strip() if isinstance(value, str) and value.strip() else None


def load_settings() -> Settings:
    settings = Settings()
    if settings.auth_enabled and not settings.auth_token:
        raise RuntimeError("BROWSER_MCP_AUTH_TOKEN is required when auth is enabled.")
    return settings
```

For comma-separated lists, either add validators or use JSON list syntax. Prefer comma-separated env for operator friendliness.

**Test cases:**

- `BROWSER_MCP_AUTH_ENABLED=false` allows missing token.
- `BROWSER_MCP_AUTH_ENABLED=true` requires token.
- Invalid `MCP_TRANSPORT` fails.
- Domain lists parse and strip whitespace.

**Verification command:**

```bash
python3 -m unittest tests/test_config.py -v
```

Expected: new config tests pass.

---

## Task 2: Add bearer-token auth boundary

**Objective:** Protect HTTP/SSE MCP traffic and artifact downloads with a shared auth check.

**Files:**

- Create: `src/auth.py`
- Modify: `src/server.py`
- Modify: `src/tools/artifacts.py`
- Test: `tests/test_auth.py`
- Docs: `docs/src/content/docs/configuration.md`

**Implementation approach:**

Create pure auth helpers first so they are easy to test without launching FastMCP:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AuthDecision:
    ok: bool
    status_code: int = 200
    reason: str = "ok"


def authorize_header(auth_enabled: bool, expected_token: str | None, header_value: str | None) -> AuthDecision:
    if not auth_enabled:
        return AuthDecision(ok=True)
    if not expected_token:
        return AuthDecision(ok=False, status_code=500, reason="auth token is not configured")
    prefix = "Bearer "
    if not header_value or not header_value.startswith(prefix):
        return AuthDecision(ok=False, status_code=401, reason="missing bearer token")
    provided = header_value[len(prefix):].strip()
    if provided != expected_token:
        return AuthDecision(ok=False, status_code=403, reason="invalid bearer token")
    return AuthDecision(ok=True)
```

Integrate with Starlette custom routes where possible. If FastMCP does not expose a clean global middleware hook, document the limitation and protect all custom HTTP routes now, then add an explicit transport auth integration in a follow-up task after validating FastMCP internals.

**Test cases:**

- Disabled auth returns OK.
- Missing header returns 401.
- Wrong token returns 403.
- Correct bearer token returns OK.

**Verification command:**

```bash
python3 -m unittest tests/test_auth.py -v
```

Expected: all auth helper tests pass.

---

## Task 3: Add navigation policy checks

**Objective:** Prevent browser navigation to unsupported schemes, private networks, metadata IPs, and blocked domains.

**Files:**

- Create: `src/policy.py`
- Modify: `src/tools/navigation.py`
- Test: `tests/test_policy.py`
- Docs: `docs/src/content/docs/configuration.md`

**Policy rules:**

- Allow `http` and `https` by default.
- Block `file://` unless `allow_file_urls=true`.
- Block loopback, link-local, private, multicast, and reserved IPs when `block_private_networks=true`.
- Always block cloud metadata targets such as `169.254.169.254`.
- If `allow_domains` is non-empty, only allow matching domains.
- `block_domains` always wins over `allow_domains`.
- Support wildcard suffix patterns such as `*.github.com`.

**Implementation shape:**

```python
@dataclass(frozen=True)
class PolicyDecision:
    ok: bool
    reason: str = "ok"


def evaluate_navigation_url(url: str, settings: Settings) -> PolicyDecision:
    ...
```

Modify `navigate()`:

```python
decision = evaluate_navigation_url(url, runtime.settings)
if not decision.ok:
    return {"ok": False, "error": decision.reason, "error_type": "NavigationPolicyError"}
```

**Test cases:**

- `https://github.com` allowed by default.
- `file:///etc/passwd` blocked by default.
- `http://127.0.0.1:8080` blocked when private network blocking is enabled.
- `http://169.254.169.254/latest/meta-data` always blocked.
- `https://evil.example` blocked when allowlist is `github.com`.
- `https://sub.github.com` allowed when allowlist is `*.github.com`.
- Blocklist overrides allowlist.

**Verification command:**

```bash
python3 -m unittest tests/test_policy.py -v
```

Expected: all policy tests pass.

---

## Task 4: Add health and readiness routes

**Objective:** Make container and reverse-proxy deployments easier to monitor.

**Files:**

- Modify: `src/server.py`
- Test: `tests/test_server_routes.py`
- Docs: `docs/src/content/docs/configuration.md`
- Modify: `Dockerfile` if adding Docker healthcheck

**Routes:**

- `GET /healthz` returns process liveness.
- `GET /readyz` returns config/runtime readiness without exposing secrets.

Example response:

```json
{
  "ok": true,
  "service": "browser-mcp",
  "transport": "sse",
  "auth_enabled": true
}
```

**Verification command:**

```bash
python3 -m unittest tests/test_server_routes.py -v
```

Expected: route handlers return stable JSON shapes.

---

## Task 5: Update Docker and documentation

**Objective:** Document secure deployment defaults and operational examples.

**Files:**

- Modify: `.env.example`
- Modify: `docker-compose.yml`
- Modify: `README.md`
- Modify: `docs/src/content/docs/configuration.md`
- Modify: `docs/src/content/docs/features.md`

**Documentation must include:**

- How to set `BROWSER_MCP_AUTH_TOKEN`.
- How to disable auth only for local trusted development.
- Example Caddy/Nginx reverse proxy note.
- Domain allowlist/blocklist examples.
- Warning that browser automation can expose credentials through screenshots/downloads.

**Verification command:**

```bash
python3 -m compileall -q src tests main.py
python3 -m unittest discover -s tests -p "test_*.py"
```

Expected: all tests pass.

---

## Final phase verification

Run:

```bash
python3 -m compileall -q src tests main.py
python3 -m unittest discover -s tests -p "test_*.py"
docker build -t browser-mcp:phase-01 .
```

Expected:

- Syntax check passes.
- Unit tests pass.
- Docker image builds.
- Auth and policy settings are documented.
