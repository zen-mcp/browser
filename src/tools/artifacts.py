import base64
import mimetypes
from pathlib import Path

from starlette.responses import FileResponse, PlainTextResponse

from browser import BrowserRuntime
from .contracts import error_payload, mcp_tool_guard


def register_artifact_tools(mcp, runtime: BrowserRuntime) -> None:
    def file_response_payload(file_path: Path, category: str) -> dict:
        encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
        return {
            "ok": True,
            "file_name": file_path.name,
            "category": category,
            "mime_type": mimetypes.guess_type(file_path.name)[0]
            or "application/octet-stream",
            "size_bytes": file_path.stat().st_size,
            "content_base64": encoded,
        }

    def read_file_payload(file_name: str, category: str) -> dict:
        try:
            file_path = runtime.resolve_file_path(file_name, category)
        except ValueError as error:
            return error_payload(error)

        if not file_path.exists() or not file_path.is_file():
            return {
                "ok": False,
                "error": "File not found.",
                "error_type": "FileNotFoundError",
            }

        return file_response_payload(file_path, category.lower())

    @mcp.custom_route("/artifacts/{file_name:path}", methods=["GET"])
    async def download_artifact(request):
        try:
            file_path = runtime.resolve_file_path(
                request.path_params["file_name"], "artifacts"
            )
        except ValueError as error:
            return PlainTextResponse(str(error), status_code=400)

        if not file_path.exists() or not file_path.is_file():
            return PlainTextResponse("File not found.", status_code=404)

        return FileResponse(file_path)

    @mcp.tool(
        description=(
            "List top-level runtime artifact files in the data directory with "
            "size and modified time metadata."
        )
    )
    @mcp_tool_guard
    async def list_artifacts() -> dict:
        """List artifact files currently available for retrieval."""
        files = await runtime.list_artifacts()
        return {"ok": True, "count": len(files), "files": files}

    @mcp.tool(
        description=(
            "Read a runtime artifact or download by safe file name and return "
            "base64 content plus MIME and size metadata."
        )
    )
    @mcp_tool_guard
    async def get_file(file_name: str, category: str = "artifacts") -> dict:
        """Read a runtime file through BrowserRuntime path validation."""
        return read_file_payload(file_name, category)

    @mcp.tool(
        description=(
            "Read a downloaded file by safe file name and return base64 "
            "content plus MIME and size metadata."
        )
    )
    @mcp_tool_guard
    async def get_downloaded_file(file_name: str) -> dict:
        """Read a downloaded file through BrowserRuntime path validation."""
        return read_file_payload(file_name, "downloads")

    @mcp.tool(
        description=(
            "Capture a PNG screenshot of the current direct Playwright page. "
            "Use full_page for evidence bundles or selector for a focused element."
        )
    )
    @mcp_tool_guard
    async def take_screenshot(
        file_name_prefix: str = "screenshot",
        full_page: bool = False,
        selector: str | None = None,
    ) -> dict:
        """Capture a screenshot artifact using BrowserRuntime path helpers."""
        page = await runtime.get_page()
        file_path = runtime.build_artifact_path(file_name_prefix, "png")

        if selector:
            await page.locator(selector).first.screenshot(path=str(file_path))
        else:
            await page.screenshot(path=str(file_path), full_page=full_page)

        return {
            "ok": True,
            "file_name": file_path.name,
            "path": str(file_path),
            "url": page.url,
            "title": await page.title(),
            "size_bytes": file_path.stat().st_size,
            "full_page": full_page,
            "selector": selector,
        }
