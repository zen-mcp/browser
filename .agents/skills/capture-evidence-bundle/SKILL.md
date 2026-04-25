---
name: capture-evidence-bundle
description: Capture browser task evidence by collecting page snapshot text, screenshots, current URL/title, and artifact metadata. Use when a task needs auditable proof of the page state before or after browser actions.
license: MIT
compatibility: browser-mcp direct Playwright MCP tools
allowed-tools: get_page_snapshot take_screenshot list_artifacts get_file
metadata:
  version: "1.0.0"
  tags: evidence,browser,artifacts
---
# Capture Evidence Bundle

## When To Use

Use this skill when a user asks for proof, screenshots, page evidence, a before
and after capture, or a reproducible record of a browser task.

## Inputs

- `label`: short evidence label used as a screenshot prefix.
- `full_page`: whether the screenshot should include the full page.
- `selector`: optional element selector for focused screenshots.

## Procedure

1. Call `get_page_snapshot` to capture URL, title, and visible text.
2. Call `take_screenshot` with a sanitized label. Use `full_page=True` for
   reports, audits, and long pages.
3. If a specific UI element matters, capture a second screenshot with
   `selector`.
4. Call `list_artifacts` and record the new screenshot file names.
5. Return a concise summary with URL, title, screenshot names, and any notable
   page text needed to explain the result.

## Never

- Never include passwords, auth tokens, cookies, or raw headers in summaries.
- Never persist credentials in artifacts.
- Never bypass `take_screenshot` or file tools with ad hoc filesystem paths.
