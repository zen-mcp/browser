---
title: Configuration
description: Docker, provider, transport, model, port, and artifact settings.
---

The server reads configuration from environment variables. With Docker Compose,
copy `.env.example` to `.env` and edit the values there.

## Required

| Variable | Purpose |
| --- | --- |
| `OPENAI_API_KEY` | API key for your OpenAI-compatible provider. |
| `OPENAI_BASE_URL` | Base URL for the provider API. |
| `MODEL_NAME` | Model used by the `browser-use` agent flow. |

## Docker settings

| Variable | Default in example | Purpose |
| --- | --- | --- |
| `BROWSER_MCP_TAG` | `latest` | Container image tag for `zen-mcp/browser`. |
| `BROWSER_MCP_PORT` | `8000` | Host port mapped to container port `8000`. |
| `BROWSER_MCP_TRANSPORT` | `streamable-http` | MCP HTTP transport. Use `sse` only for legacy clients. |
| `BROWSER_PREWARM` | `true` | Start Playwright and Chromium during server startup to reduce first-tool latency. |
| `DATA_PATH` | `./data` | Host directory that receives runtime files. |

Docker Compose maps:

```text
127.0.0.1:${BROWSER_MCP_PORT}:8000
${DATA_PATH}/browser-mcp:/data
```

That means screenshots and runtime artifacts are written to `/data` inside the
container and persist on the host under `${DATA_PATH}/browser-mcp`. The host
port is bound to localhost by default so the MCP server is not exposed on every
network interface.

Streamable HTTP clients connect to:

```text
http://127.0.0.1:${BROWSER_MCP_PORT}/mcp
```

Legacy SSE clients can set `BROWSER_MCP_TRANSPORT=sse` and connect to `/sse`.

Files can be retrieved with `list_artifacts`, `get_file`, or the
`/artifacts/<file_name>` HTTP route. File reads are validated so requests cannot
escape the data directory. Prefer the `/artifacts/<file_name>` route for large
files instead of returning base64 content through MCP.

## Example

```text
DATA_PATH=./data
OPENAI_API_KEY=your-provider-key
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-5.4-mini
BROWSER_MCP_TAG=latest
BROWSER_MCP_PORT=8000
BROWSER_MCP_TRANSPORT=streamable-http
BROWSER_PREWARM=true
```

## OpenClaw

Configure OpenClaw with Streamable HTTP:

```bash
openclaw mcp set zen-browser '{
  "url": "http://127.0.0.1:8000/mcp",
  "transport": "streamable-http",
  "connectionTimeoutMs": 10000
}'
```

If OpenClaw runs in another container on the same host, use:

```json
{
  "url": "http://host.docker.internal:8000/mcp",
  "transport": "streamable-http",
  "connectionTimeoutMs": 10000
}
```

`openclaw mcp set` saves client configuration only. It does not start this
server and does not prove the endpoint is reachable.

## Local run

For local development outside Docker, create a virtual environment, install
dependencies, and run the entrypoint:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Docker remains the recommended path for normal usage because it keeps the
browser runtime and generated files in a predictable container boundary.
