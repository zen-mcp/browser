---
name: scrape-with-pagination
description: Extract repeated content from paginated lists, result tables, or infinite-scroll pages using browser-mcp observation and navigation tools. Use when the user asks to collect items across multiple pages.
license: MIT
compatibility: browser-mcp direct Playwright MCP tools
allowed-tools: navigate get_page_snapshot click scroll wait_for take_screenshot
metadata:
  version: "1.0.0"
  tags: scraping,pagination,browser
---
# Scrape With Pagination

## When To Use

Use this skill for paginated search results, tables, product lists, article
lists, or infinite-scroll pages where an API is not available.

## Inputs

- `start_url`
- `item_selector` or text pattern that identifies each item.
- `next_selector` or a description of the next-page control.
- `max_pages` to prevent unbounded browsing.

## Procedure

1. `navigate(start_url)` and wait for the list area to load.
2. Capture `get_page_snapshot` and identify repeated item fields.
3. Extract only the requested fields. Avoid collecting unrelated page text.
4. Move to the next page with `click(next_selector)` or `scroll` for
   infinite-scroll pages.
5. After each page, call `wait_for` for the list area or a short timeout, then
   capture another snapshot.
6. Stop at `max_pages`, no next control, duplicate page content, or a user
   requested stopping condition.
7. Take a final screenshot when evidence is useful.

## Failure Modes

- If a CAPTCHA, login wall, or consent wall blocks scraping, stop and report it.
- If selectors are unstable, return the current URL/title and a screenshot so
  the flow can be adjusted.

## Never

- Never bypass site controls outside browser automation.
- Never scrape credentials, cookies, hidden auth tokens, or private profile data
  unless the user explicitly owns the session and requested those fields.
