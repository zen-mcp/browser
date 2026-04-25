---
name: safe-login
description: Authenticate through a standard email and password login form while protecting credentials. Use when a browser task requires a logged-in session and the site does not provide an API.
license: MIT
compatibility: browser-mcp direct Playwright MCP tools; not for SSO, OAuth, passkey, or CAPTCHA-heavy flows
allowed-tools: navigate get_page_snapshot click type_text press_key wait_for take_screenshot
metadata:
  version: "1.0.0"
  tags: auth,browser,safety
---
# Safe Login

## When To Use

Use this skill for ordinary email/password forms. Do not use it for SSO, OAuth,
passkeys, CAPTCHA solving, or flows that require bypassing security controls.

## Inputs

- `login_url`
- `email`
- `password`
- `success_selector` or visible text that confirms login succeeded.
- `totp_code` if the user provides a one-time code during the session.

## Procedure

1. `navigate(login_url)` and wait for the login form.
2. Use `get_page_snapshot` to identify email/username, password, remember-me,
   and submit controls.
3. Type credentials with `type_text`. Do not repeat credential values in any
   response or log.
4. Submit with `click` or `press_key("Enter")`.
5. If a TOTP field appears, ask the user for the current code unless one was
   already provided.
6. `wait_for` the success selector or success text.
7. Use `take_screenshot` after login only if evidence is needed and it will not
   expose private account data.

## Failure Modes

- CAPTCHA or bot challenge: stop and report `captcha`.
- Password field not found: capture a page snapshot and report `no-form`.
- Invalid credentials: report the site error text without echoing secrets.

## Never

- Never log or return passwords, TOTP codes, cookies, or auth headers.
- Never persist credentials in artifacts.
- Never attempt to bypass CAPTCHA, SSO, passkeys, or account recovery controls.
