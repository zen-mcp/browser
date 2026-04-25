---
title: Features
description: Current browser-mcp capabilities for users and MCP clients.
---

`browser-mcp` focuses on practical browser automation: direct Playwright-style
tools for precise steps, plus an agent tool for tasks that need planning across
multiple page states.

## Core capabilities

| Capability | What it does | Typical use |
| --- | --- | --- |
| Page observation | Reads current URL, title, and visible body text. | Decide the next selector or summarize the page state. |
| Navigation | Opens URLs, scrolls pages, and waits for selectors, text, or timeouts. | Move through multi-page flows reliably. |
| Interaction | Clicks selectors, types text, and presses keyboard keys. | Fill forms, submit flows, open menus, or trigger UI actions. |
| Screenshots | Captures full-page or element screenshots as PNG artifacts. | Evidence, debugging, reports, before/after checks. |
| Artifact access | Lists and reads files from the runtime data directory. | Retrieve screenshots or generated downloads from the container. |
| Agent tasks | Runs a `browser-use` agent from a start URL and instruction. | Ask for a higher-level browser outcome when direct steps are too verbose. |

## Runtime model

The server starts a headless Chromium runtime and exposes MCP tools over SSE.
Direct tools use Playwright through `BrowserRuntime`; agent tasks use
`browser-use` with the configured OpenAI-compatible model.

Generated artifacts are written under `/data` in the container. Docker Compose
binds that to `${DATA_PATH}/browser-mcp` on the host, so useful files survive
container restarts without exposing the rest of the host filesystem.

## Safety boundaries

- Runtime browser sessions are headless.
- Artifact writes use safe generated filenames.
- Artifact and download reads validate the requested path stays inside `/data`.
- `type_text` returns only the number of typed characters, not the typed value.
- Credentials, cookies, auth headers, passwords, and TOTP secrets should not be
  logged, returned, or persisted.
