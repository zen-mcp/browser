# Dev Command

Use this when an agent needs to run the MCP server locally.

## Steps

1. Create and activate a virtualenv if needed.
2. Install dependencies with `pip install -r requirements.txt`.
3. Ensure `.env` contains `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `MODEL_NAME`,
   and `BROWSER_MCP_PORT`.
4. Run `python3 main.py`.

## Docker Alternative

Run `docker compose up --build` for container parity. Runtime files are written
to `./data` on the host through the `/data` bind mount.
