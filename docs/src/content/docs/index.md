---
title: Home
description: Run browser automation through MCP in an isolated Docker runtime.
---

`browser-mcp` gives MCP clients a browser they can drive safely and repeatably.
It runs headless Chromium with Playwright inside Docker, exposes tools over MCP
Streamable HTTP, and adds a `browser-use` agent for complex multi-step web
tasks.

## Docker first

The recommended path is Docker. It keeps the browser runtime separate from your
host environment and writes runtime files only through the configured `/data`
volume.

```bash
cp .env.example .env
```

Set the values you need:

```text
OPENAI_API_KEY=your-provider-key
OPENAI_BASE_URL=https://your-provider.example/v1
MODEL_NAME=gpt-5.4-mini
BROWSER_MCP_HOST=127.0.0.1
BROWSER_MCP_PORT=8000
BROWSER_PREWARM=true
DATA_PATH=./data
```

Start the service:

```bash
docker compose up
```

The MCP server listens on port `8000` by default. Runtime files are stored in
`/data` inside the container and persisted on the host at
`${DATA_PATH}/browser-mcp`.

Streamable HTTP clients connect to `http://127.0.0.1:8000/mcp`.

## Why it exists

Browser automation is useful for pages that do not expose a clean API, but it is
risky to let an agent run directly in your main desktop or shell environment.
`browser-mcp` narrows that surface:

- browser actions run in a containerized headless Chromium runtime;
- generated files and screenshots go through the `/data` bind mount;
- artifact reads validate file paths before returning data;
- secrets should be passed through environment variables, not written to docs,
  logs, or artifacts.

Docker isolation reduces host exposure, but it is not a full data-loss
prevention system. Treat visited websites, credentials, downloads, and
screenshots with the same care you would in any browser automation workflow.

## What it can do

- Navigate, wait, scroll, click, type, and press keys.
- Read the current page URL, title, and visible text.
- Capture screenshots and retrieve artifact files.
- Run higher-level agent tasks with a natural-language instruction.
- Use OpenAI-compatible model providers through `OPENAI_BASE_URL`.

## Common jobs

- collect evidence from a page with text snapshot plus screenshot;
- scrape paginated lists when no API is available;
- fill standard login forms without echoing credentials back in results;
- run multi-step browser tasks through an agent;
- keep generated screenshots and files in a predictable host folder.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Use local development when changing the server itself. Use Docker for normal
usage and parity with the released image.
