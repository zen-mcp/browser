# Phase 02 — AI-Friendly Browser Snapshot and Element References Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Upgrade browser observation and interaction from CSS-selector-only primitives to stable, AI-friendly page snapshots with reusable element references.

**Architecture:** Add a snapshot service that scans accessible/interactive elements, assigns short-lived refs such as `@e1`, stores a ref registry in `BrowserRuntime`, and exposes new tools that click/type/select by ref. Preserve existing selector tools for backward compatibility.

**Tech Stack:** Python 3.11+, Playwright Python, FastMCP, dataclasses/Pydantic-style typed payloads, `unittest`, optional Pillow for annotated screenshots in a later task.

---

## Current baseline

Relevant files:

- `src/tools/observation.py` has `get_page_snapshot(max_text_chars=4000)` returning title, URL, and body text.
- `src/tools/interaction.py` has `click(selector)`, `type_text(selector, text)`, and `press_key(key)`.
- `src/browser.py` stores one active `Page`, but has no element ref registry.
- Tool docs live in `docs/src/content/docs/tools.md`.

## Acceptance criteria

- New snapshot tool returns structured page state with interactive elements and refs.
- Refs are stable within the current page state and expire after navigation or explicit refresh.
- New tools can click/type/select by ref.
- Existing selector tools continue to work.
- Snapshot output avoids leaking input values unless explicitly safe.
- Tests cover ref allocation, truncation, redaction, and interaction lookup errors.

---

## Task 1: Add element ref models and registry

**Objective:** Give the runtime a small in-memory registry mapping refs to safe locators.

**Files:**

- Modify: `src/browser.py`
- Create: `src/refs.py`
- Test: `tests/test_refs.py`

**Data model:**

```python
@dataclass(frozen=True)
class ElementRef:
    ref: str
    role: str | None
    name: str
    selector: str
    tag_name: str
    input_type: str | None = None
    visible: bool = True
    disabled: bool = False

class RefRegistry:
    def __init__(self) -> None:
        self._items: dict[str, ElementRef] = {}

    def reset(self) -> None:
        self._items.clear()

    def register(self, item: ElementRef) -> ElementRef:
        ref = f"@e{len(self._items) + 1}"
        stored = replace(item, ref=ref)
        self._items[ref] = stored
        return stored

    def get(self, ref: str) -> ElementRef:
        try:
            return self._items[ref]
        except KeyError:
            raise ValueError(f"Unknown or expired element ref: {ref}")
```

Add `self.refs = RefRegistry()` to `BrowserRuntime`.

Reset refs in `navigate()` after successful navigation and before generating a new snapshot.

**Tests:**

- First registered element gets `@e1`.
- Registry reset clears old refs.
- Missing ref raises stable `ValueError`.

---

## Task 2: Build structured snapshot extraction

**Objective:** Return a compact but useful structured view of the page for AI clients.

**Files:**

- Create: `src/snapshot.py`
- Modify: `src/tools/observation.py`
- Test: `tests/test_snapshot.py`

**Tool name:**

```text
get_structured_snapshot
```

**Output shape:**

```json
{
  "ok": true,
  "url": "https://example.com",
  "title": "Example",
  "text": "bounded visible text",
  "text_length": 1234,
  "text_truncated": false,
  "elements": [
    {
      "ref": "@e1",
      "role": "button",
      "name": "Submit",
      "tag_name": "button",
      "input_type": null,
      "visible": true,
      "disabled": false
    }
  ],
  "element_count": 1,
  "elements_truncated": false
}
```

**Extraction strategy:**

Start simple and deterministic:

```javascript
Array.from(document.querySelectorAll('a,button,input,select,textarea,[role],[tabindex]'))
  .filter(el => /* visible-ish */)
  .map((el, index) => ({ ... }))
```

Generate an internal selector with `data-browser-mcp-ref="e1"` or use Playwright locator nth fallback. Prefer a temporary data attribute because it is deterministic within the current DOM.

Do not return raw values for password fields or fields likely to contain secrets.

**Tests:**

Use pure sanitizer helpers for unit tests, and add Playwright integration tests later in Phase 05.

---

## Task 3: Add interaction tools by ref

**Objective:** Let clients act on snapshot refs instead of guessing CSS selectors.

**Files:**

- Modify: `src/tools/interaction.py`
- Test: `tests/test_ref_interactions.py`
- Docs: `docs/src/content/docs/tools.md`

**Tools:**

```text
click_ref(ref: str)
type_ref(ref: str, text: str, clear_first: bool = True)
select_ref(ref: str, value: str | None = None, label: str | None = None)
check_ref(ref: str, checked: bool = True)
hover_ref(ref: str)
```

**Implementation pattern:**

```python
element = runtime.refs.get(ref)
page = await runtime.get_page()
locator = page.locator(f'[data-browser-mcp-ref="{ref[2:]}"]').first
await locator.click()
```

Return only safe metadata. Never echo typed text.

**Error behavior:**

- Unknown ref returns `{ok: false, error_type: "ValueError"}` through `mcp_tool_guard`.
- Unsupported element type returns `{ok: false, error_type: "UnsupportedElementError"}`.

---

## Task 4: Add tab and page state helpers

**Objective:** Make snapshot refs reliable when pages open new tabs or reload.

**Files:**

- Modify: `src/browser.py`
- Create/modify: `src/tools/tabs.py`
- Modify: `src/tools/__init__.py`
- Test: `tests/test_tabs_contracts.py`
- Docs: `docs/src/content/docs/tools.md`

**Tools:**

```text
list_tabs()
switch_tab(index: int)
close_tab(index: int)
reload_page()
go_back()
go_forward()
```

Reset ref registry whenever the active page changes, reloads, or navigates.

---

## Task 5: Add optional annotated screenshot

**Objective:** Help clients visually map refs to page elements.

**Files:**

- Modify: `src/tools/artifacts.py`
- Optional create: `src/annotate.py`
- Test: `tests/test_annotate_contracts.py`
- Docs: `docs/src/content/docs/tools.md`

**Tool extension:**

Add `annotate: bool = False` to `take_screenshot` or create:

```text
take_annotated_screenshot(full_page: bool = False)
```

For the first version, use Playwright to inject temporary labels into the DOM before screenshot, then remove them in `finally`.

**Acceptance:**

- Labels correspond to current refs.
- DOM cleanup happens even if screenshot fails.
- Screenshot artifact path still uses `runtime.build_artifact_path()`.

---

## Final phase verification

Run:

```bash
python3 -m compileall -q src tests main.py
python3 -m unittest discover -s tests -p "test_*.py"
docker build -t browser-mcp:phase-02 .
```

Manual smoke test:

1. Navigate to a simple test page.
2. Call `get_structured_snapshot`.
3. Click a button using `click_ref("@e1")`.
4. Verify URL/page state changed as expected.
