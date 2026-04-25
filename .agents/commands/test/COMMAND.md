# Test Command

Use this before finishing runtime, tool, or AI-first documentation changes.

## Commands

```bash
python3 -m unittest discover -s tests -p "test_*.py"
python3 -m compileall -q src tests main.py
```

Run Docker build validation when Docker behavior or dependency installation
changes:

```bash
docker build -t browser-mcp:ci .
```
