# Phase 03 — Personal Session Profiles and Website Auth Workflows Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Support personal browser profiles so users can authenticate to websites once, persist session state safely, and reuse that state in future MCP sessions without exposing raw credentials.

**Architecture:** Introduce named browser profiles backed by controlled directories under `/data/profiles`, use Playwright persistent contexts or encrypted storage-state files, and add profile management tools. Website-specific auth docs describe safe manual login and reuse flows without storing passwords in the repository.

**Tech Stack:** Playwright persistent contexts/storage state, Python `pathlib`, `cryptography` for optional encryption, FastMCP tools, Docker volume `/data`, `unittest`.

---

## Current baseline

- `BrowserRuntime` owns one in-memory browser context.
- Runtime data uses top-level `/data` only.
- There is no concept of named profiles, persistent login, storage state, or session lifecycle.
- Existing docs warn not to leak credentials but do not provide website auth workflows.

## Acceptance criteria

- Users can create/list/switch/delete named profiles.
- Browser state can be saved and loaded per profile.
- Session files remain under `/data/profiles/<profile_name>`.
- Tools never return raw cookies, localStorage, auth headers, or passwords.
- Optional encryption can protect storage-state files at rest.
- Docs include safe auth workflows for GitHub, Figma, Google, and generic websites.

---

## Task 1: Define profile directory layout and validation

**Objective:** Create a safe profile filesystem boundary under `/data/profiles`.

**Files:**

- Modify: `src/browser.py`
- Create: `src/profiles.py`
- Test: `tests/test_profiles.py`
- Docs: `docs/src/content/docs/configuration.md`

**Directory layout:**

```text
/data/
  profiles/
    default/
      storage-state.json
      downloads/
      artifacts/
      traces/
    github/
      storage-state.json
```

**Profile name rules:**

- Lowercase letters, numbers, hyphen, underscore only.
- Max length 64.
- Reject `.`, `..`, slashes, absolute paths, and empty names.

**Core functions:**

```python
def validate_profile_name(name: str) -> str: ...
def profile_root(name: str) -> Path: ...
def list_profiles() -> list[dict]: ...
```

**Tests:**

- Valid profile names pass.
- Traversal attempts fail.
- Paths always resolve under `/data/profiles`.

---

## Task 2: Add profile-aware runtime lifecycle

**Objective:** Allow `BrowserRuntime` to switch browser contexts safely.

**Files:**

- Modify: `src/browser.py`
- Test: `tests/test_browser_runtime_profiles.py`

**Runtime additions:**

```python
self.active_profile_name = settings.default_profile
self._profile_contexts: dict[str, BrowserContext] = {}
```

Add methods:

```python
async def switch_profile(self, name: str) -> dict: ...
async def close_active_context(self) -> None: ...
async def save_storage_state(self) -> Path: ...
async def load_storage_state(self, name: str) -> dict: ...
```

Implementation can start with `browser.new_context(storage_state=...)` rather than full persistent context. Move to `launch_persistent_context` only if needed for Chrome extension or advanced profile behavior.

Reset element refs when switching profile.

---

## Task 3: Add profile management MCP tools

**Objective:** Expose profile operations to MCP clients with safe payloads.

**Files:**

- Create: `src/tools/profiles.py`
- Modify: `src/tools/__init__.py`
- Test: `tests/test_profile_tool_contracts.py`
- Docs: `docs/src/content/docs/tools.md`

**Tools:**

```text
list_profiles()
create_profile(name: str)
switch_profile(name: str)
save_session_state()
clear_profile_state(name: str)
get_active_profile()
```

**Safe output example:**

```json
{
  "ok": true,
  "active_profile": "github",
  "has_storage_state": true,
  "storage_state_size_bytes": 2048
}
```

Never return cookies, localStorage, or raw storage-state content.

---

## Task 4: Add optional storage-state encryption

**Objective:** Protect persisted website sessions at rest for personal deployments.

**Files:**

- Modify: `requirements.txt`
- Create: `src/crypto.py`
- Modify: `src/profiles.py`
- Modify: `src/config.py`
- Test: `tests/test_crypto.py`
- Docs: `docs/src/content/docs/configuration.md`

**Config:**

```text
BROWSER_MCP_SESSION_ENCRYPTION_ENABLED=true
BROWSER_MCP_SESSION_ENCRYPTION_KEY=<base64-fernet-key>
```

**Behavior:**

- If encryption enabled, write `storage-state.enc.json`.
- If encryption disabled, write `storage-state.json` and warn in docs.
- If encrypted file exists, load it only when key is configured.

**Tech:**

- `cryptography.fernet.Fernet`

---

## Task 5: Add human-in-the-loop login flow

**Objective:** Support sites that require manual login, MFA, passkeys, or CAPTCHA without trying to bypass protections.

**Files:**

- Modify: `src/tools/profiles.py`
- Modify: `src/tools/navigation.py`
- Docs: `docs/src/content/docs/use-cases.md`
- Create docs:
  - `docs/src/content/docs/auth/github.md`
  - `docs/src/content/docs/auth/figma.md`
  - `docs/src/content/docs/auth/google.md`
  - `docs/src/content/docs/auth/generic.md`

**Flow:**

1. `switch_profile("github")`
2. `navigate("https://github.com/login")`
3. User completes login manually through exposed browser workflow or remote browser access if supported.
4. `save_session_state()`
5. Future tasks reuse `switch_profile("github")`.

**Security rule:**

Do not implement CAPTCHA bypass. Do not store passwords. Do not return cookies.

---

## Task 6: Add profile backup and cleanup docs

**Objective:** Make long-running personal usage maintainable.

**Files:**

- Docs: `docs/src/content/docs/configuration.md`
- Docs: `README.md`

Document:

- Where session state is stored.
- How to revoke a compromised profile.
- How to rotate encryption keys.
- How to clear sessions.
- How to back up `/data/profiles` securely.

---

## Final phase verification

Run:

```bash
python3 -m compileall -q src tests main.py
python3 -m unittest discover -s tests -p "test_*.py"
docker build -t browser-mcp:phase-03 .
```

Manual smoke test:

1. Create profile `github`.
2. Switch to it.
3. Navigate to GitHub.
4. Save session state.
5. Restart server.
6. Switch to `github` and verify state file is detected without raw cookie output.
