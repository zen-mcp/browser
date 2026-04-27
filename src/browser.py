import asyncio
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from browser_use import BrowserSession
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from config import Settings

DATA_DIR = Path("/data")

class BrowserRuntime:
    def __init__(self, settings: Settings):
        self.settings = settings
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._agent_browser: BrowserSession | None = None
        self._page_lock = asyncio.Lock()

    def get_agent_browser(self) -> BrowserSession:
        if self._agent_browser is None:
            self._agent_browser = BrowserSession(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ],
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
            )
        return self._agent_browser

    async def get_page(self) -> Page:
        if self._page is not None:
            return self._page

        async with self._page_lock:
            if self._page is not None:
                return self._page

            if self._playwright is None:
                self._playwright = await async_playwright().start()

            if self._browser is None:
                self._browser = await self._playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled",
                    ],
                )

            if self._context is None:
                self._context = await self._browser.new_context(
                    accept_downloads=True,
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/122.0.0.0 Safari/537.36"
                    ),
                )

            pages = self._context.pages
            if pages:
                self._page = pages[-1]
            else:
                self._page = await self._context.new_page()
            return self._page

    async def prewarm(self) -> None:
        await self.get_page()

    async def close(self) -> None:
        agent_browser = self._agent_browser
        self._agent_browser = None
        if agent_browser is not None:
            close = getattr(agent_browser, "close", None)
            if close is not None:
                result = close()
                if hasattr(result, "__await__"):
                    await result

        page = self._page
        self._page = None
        if page is not None:
            await page.close()

        context = self._context
        self._context = None
        if context is not None:
            await context.close()

        browser = self._browser
        self._browser = None
        if browser is not None:
            await browser.close()

        playwright = self._playwright
        self._playwright = None
        if playwright is not None:
            await playwright.stop()

    async def list_artifacts(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for path in sorted(DATA_DIR.glob("*")):
            if not path.is_file():
                continue
            stats = path.stat()
            results.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "size_bytes": stats.st_size,
                    "modified_at": datetime.fromtimestamp(
                        stats.st_mtime, tz=UTC
                    ).isoformat(),
                }
            )
        return results

    def build_artifact_path(self, prefix: str, extension: str) -> Path:
        safe_prefix = re.sub(r"[^A-Za-z0-9_.-]+", "_", prefix).strip("._-")
        if not safe_prefix:
            safe_prefix = "artifact"

        safe_extension = extension.lstrip(".") or "dat"
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S_%f")
        return DATA_DIR / f"{safe_prefix}_{timestamp}.{safe_extension}"

    def resolve_file_path(self, requested_name: str) -> Path:
        root = DATA_DIR.resolve()
        target = (root / requested_name).resolve()
        if target == root or root not in target.parents:
            raise ValueError("Requested file is outside data directory.")
        return target
