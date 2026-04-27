<p align="center">
  <img src="https://raw.githubusercontent.com/zen-mcp/browser/refs/heads/main/logo.png" alt="Zen Browser MCP logo" width="300" />
</p>

<h1 align="center">Zen Browser MCP</h1>

<p align="center">
  MCP server for browser automation with Playwright and browser-use.
</p>

<p align="center">
  <a href="https://github.com/zen-mcp/browser/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/zen-mcp/browser/ci.yml?branch=main&label=ci&style=for-the-badge" /></a>
  <a href="https://github.com/zen-mcp/browser/actions/workflows/docs.yml"><img alt="Docs" src="https://img.shields.io/github/actions/workflow/status/zen-mcp/browser/docs.yml?branch=main&label=docs&style=for-the-badge" /></a>
  <a href="https://github.com/zen-mcp/browser/actions/workflows/release.yml"><img alt="Release" src="https://img.shields.io/github/actions/workflow/status/zen-mcp/browser/release.yml?label=release&style=for-the-badge" /></a>
  <a href="https://github.com/zen-mcp/browser/releases"><img alt="Latest release" src="https://img.shields.io/github/v/release/zen-mcp/browser?sort=semver&style=for-the-badge" /></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/zen-mcp/browser?style=for-the-badge" /></a>
  <a href="https://hub.docker.com/r/zenkiet/browser"><img alt="Docker pulls" src="https://img.shields.io/docker/pulls/zenkiet/browser?label=docker&logo=docker&style=for-the-badge" /></a>
  <a href="https://github.com/zen-mcp/browser/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/zen-mcp/browser?style=for-the-badge" /></a>
</p>

## What is it?

Zen Browser MCP is an MCP server that exposes a headless Chromium browser over
Streamable HTTP. It combines direct Playwright-style tools for deterministic
browser steps with a `browser-use` agent flow for higher-level multi-step tasks.

It is built to run from Docker first, with browser artifacts written through a
controlled `/data` volume.

## Why?

Browser automation is useful when a website does not expose a clean API, but
running an agent browser directly on your host machine increases the blast
radius. Zen Browser MCP keeps the browser runtime in a container and persists
only the files you explicitly bind through `${DATA_PATH}/browser-mcp:/data`.

Docker isolation reduces host exposure, but it is not a complete data-loss
prevention system. Treat credentials, downloads, screenshots, and visited pages
with the same care you would in any automation workflow.

## Quick Start

Copy the example environment file:

```bash
cp .env.example .env
```

Set your provider, model, port, and data path:

```text
OPENAI_API_KEY=your-provider-key
OPENAI_BASE_URL=https://your-provider.example/v1
MODEL_NAME=gpt-5.4-mini
BROWSER_MCP_TAG=latest
BROWSER_MCP_HOST=127.0.0.1
BROWSER_MCP_PORT=8000
BROWSER_PREWARM=true
DATA_PATH=./data
```

Start the MCP server:

```bash
docker compose up
```

The compose file runs `zen-mcp/browser:${BROWSER_MCP_TAG}`, maps
`127.0.0.1:${BROWSER_MCP_PORT}:8000`, and persists runtime files through
`${DATA_PATH}/browser-mcp:/data`. Streamable HTTP clients should connect to
`http://127.0.0.1:${BROWSER_MCP_PORT}/mcp`.

For OpenClaw:

```bash
openclaw mcp set zen-browser '{
  "url": "http://127.0.0.1:8000/mcp",
  "transport": "streamable-http",
  "connectionTimeoutMs": 10000
}'
```

If OpenClaw is running in another container on the same host, use
`http://host.docker.internal:8000/mcp` instead of `127.0.0.1`.

See the [configuration docs](https://zenkiet.github.io/browser-mcp/configuration/)
for the full environment reference.

## What can it do?

- Navigate pages, scroll, wait for selectors or text, and inspect visible text.
- Click elements, type into inputs, and press keyboard keys.
- Capture full-page or element screenshots as artifacts.
- List and retrieve files from the runtime data directory.
- Run complex browser tasks with a `browser-use` agent instruction.
- Use any OpenAI-compatible provider through `OPENAI_BASE_URL`.

## Docs

Full documentation is available at
[zenkiet.github.io/browser-mcp](https://zenkiet.github.io/browser-mcp/).

## Contribute

Clone the repo and install Python dependencies:

```bash
git clone https://github.com/zen-mcp/browser.git
cd browser
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the validation checks:

```bash
python3 -m compileall -q src tests main.py
python3 -m unittest discover -s tests -p "test_*.py"
docker build -t browser-mcp:ci .
```

For documentation changes:

```bash
cd docs
yarn install --frozen-lockfile
yarn build
```

Open a pull request with a focused change and the checks you ran.

## License

Licensed under the [Apache License 2.0](LICENSE).

<p align="center">
  <strong>Star me if Zen Browser MCP helps your agents browse with less risk.</strong>
</p>

<p align="center">
  <a href="https://github.com/zen-mcp/browser/stargazers"><img alt="Star this repo" src="https://img.shields.io/github/stars/zen-mcp/browser?label=Star%20this%20repo&style=social" /></a>
</p>
