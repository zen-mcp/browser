---
title: Tools
description: MCP tool reference for the current browser-mcp runtime.
---

These tools are registered by the current source code under `src/tools`.

| Tool | Category | Use it for | Output shape |
| --- | --- | --- | --- |
| `browse_and_act` | Agent | Run a complex browser task from a start URL using a natural-language instruction. | Legacy plain text result or error text. |
| `browse_and_act_structured` | Agent | Run the same agent flow when the client expects structured data. | `{ ok, result, instruction, start_url }` or `{ ok: false, error, error_type }`. |
| `get_page_snapshot` | Observation | Get the active page URL, title, and visible body text. | `{ ok, url, title, text, text_length, text_truncated }`. |
| `navigate` | Navigation | Open a URL in the active Playwright page. | `{ ok, url, title }`. |
| `scroll` | Navigation | Scroll the current page up or down by pixels. | `{ ok, direction, pixels }`. |
| `wait_for` | Navigation | Wait for a selector, visible text, or timeout. | `{ ok, mode, selector/text/seconds }`. |
| `click` | Interaction | Click the first element matching a CSS selector. | `{ ok, selector, url }`. |
| `type_text` | Interaction | Type text into the first input-like element matching a CSS selector. | `{ ok, selector, chars }`. |
| `press_key` | Interaction | Press a keyboard key such as `Enter`, `Tab`, or `Escape`. | `{ ok, key, url }`. |
| `take_screenshot` | Artifacts | Capture a PNG screenshot of the full page or one selector. | `{ ok, file_name, path, url, title, size_bytes, full_page, selector }`. |
| `list_artifacts` | Artifacts | List top-level runtime artifact files in `/data`. | `{ ok, count, files }`. |
| `get_file` | Artifacts | Read an artifact or download by safe file name and return base64 content. | `{ ok, file_name, category, mime_type, size_bytes, content_base64 }`. |
| `get_downloaded_file` | Artifacts | Read a downloaded file by safe file name when it exists in the data directory. | `{ ok, file_name, category, mime_type, size_bytes, content_base64 }`. |

Most tools return a structured dictionary with `ok: true` on success. Expected
tool-boundary failures return `ok: false`, `error`, and `error_type`.

`browse_and_act` is intentionally kept as a string-output tool for older MCP
clients. Prefer `browse_and_act_structured` when your client can consume
structured results.
