---
title: Use Cases
description: Practical workflows that browser-mcp supports today.
---

## Evidence capture

Use `get_page_snapshot` to record URL, title, and visible text, then
`take_screenshot` for a PNG artifact. Finish with `list_artifacts` or `get_file`
to retrieve the evidence bundle.

Best for QA checks, before/after captures, audit notes, and bug reports.

## Paginated scraping

Use `navigate`, `get_page_snapshot`, `click`, `scroll`, and `wait_for` to move
through search results, tables, product lists, or article lists when there is no
API available.

Keep a page limit and stop on login walls, CAPTCHA, consent walls, duplicate
content, or missing next controls.

## Standard login forms

Use `navigate`, `get_page_snapshot`, `type_text`, `click`, `press_key`, and
`wait_for` for ordinary email/password forms. Do not echo passwords, TOTP codes,
cookies, or auth headers in responses or artifacts.

This is not for SSO, OAuth, passkeys, CAPTCHA solving, or bypassing security
controls.

## Multi-step browser tasks

Use `browse_and_act_structured` when the task is easier to describe as an
outcome than as a list of selectors. The agent starts from the provided URL and
uses the configured OpenAI-compatible model to complete the instruction.

Use direct tools instead when the flow needs deterministic selector-by-selector
control.

## Screenshot reports

Use `take_screenshot` with `full_page: true` for long reports or `selector` for
a focused element. Retrieve files from the host at `${DATA_PATH}/browser-mcp` or
through `get_file`.
