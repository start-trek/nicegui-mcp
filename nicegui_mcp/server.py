from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from .analyzers import analyze_code
from .fixers import fix_code
from .generators import generate_component, list_kinds
from .registry import available_topics, get_topic, load_guidance_text, search_guidance_text
from .reviewer import review_code

INSTRUCTIONS = (
    "NiceGUI MCP is a guided development copilot for NiceGUI applications.\n\n"
    "After writing or generating NiceGUI code, use `review_nicegui_code` to catch common\n"
    "mistakes and receive auto-fixes. This is the recommended default action before\n"
    "finalizing any NiceGUI code.\n\n"
    "The MCP catches: blocking calls in event handlers, missing min-h-0 on scroll area\n"
    "parents, CSS properties in .props() instead of .style(), non-persistent destructive\n"
    "dialogs, async handlers without feedback, logic-heavy handlers, monolithic page\n"
    "functions, and styling/props conflicts.\n\n"
    "Additional tools: retrieve proven implementation patterns with `get_pattern`,\n"
    "generate starter components with `generate_nicegui_component`, explore bundled\n"
    "guidance with `search_guidance` or `get_guidance`, and run targeted analysis\n"
    "with `analyze_nicegui_code`."
)

PREFLIGHT_CONTENT = (
    "# NiceGUI MCP Preflight\n\n"
    "**When to invoke:** After writing or generating NiceGUI code, before finalizing.\n\n"
    "**Preferred tool:** Use `review_nicegui_code` as the default entry point.\n\n"
    "**Common NiceGUI mistakes the MCP catches:**\n\n"
    "1. Blocking calls (`time.sleep`, `requests.get`) in UI event handlers\n"
    "2. Missing `min-h-0` on flex parents of scroll areas\n"
    "3. CSS properties passed via `.props()` instead of `.style()`\n"
    "4. Non-persistent dialogs for destructive actions\n"
    "5. Async handlers without loading/error feedback\n\n"
    "**Convention:** Before shipping NiceGUI code, run `review_nicegui_code`."
)

mcp = FastMCP(
    name="NiceGUI MCP",
    instructions=INSTRUCTIONS,
    stateless_http=True,
    json_response=True,
)


@mcp.resource("nicegui-mcp://preflight")
def preflight() -> str:
    return PREFLIGHT_CONTENT


@mcp.resource("nicegui://topics/index")
def topic_index() -> str:
    payload = [topic.model_dump(mode="json") for topic in available_topics()]
    return json.dumps(payload, indent=2)


@mcp.resource("nicegui://guidance/{topic}")
def guidance_resource(topic: str) -> str:
    return load_guidance_text(topic)


@mcp.tool()
def review_nicegui_code(code: str, auto_fix: bool = True) -> dict:
    """Review NiceGUI code for correctness issues, apply safe fixes, and suggest improvements.

    This is the recommended entry point after writing or generating NiceGUI code.
    Submit your code and receive: issues found, severity and confidence ratings,
    auto-applied fixes for safe corrections, and one recommended improvement.

    Common issues detected: missing await in async callbacks, stale closure bugs,
    incorrect binding usage, misuse of layout context managers, blocking calls in
    handlers, non-persistent destructive dialogs, and styling/props conflicts."""
    return review_code(code=code, auto_fix=auto_fix).model_dump(mode="json")


@mcp.tool()
def list_component_kinds() -> list[dict]:
    """List all available NiceGUI component generator kinds with descriptions.

    Use this to discover valid `kind` values for `generate_nicegui_component`.
    Each entry includes the kind name, a short description, and supported modes."""
    return list_kinds()


@mcp.tool()
def list_topics() -> list[dict]:
    """List the bundled NiceGUI guidance topics with summaries and tags.
    Topics cover layout, async patterns, styling, dialogs, state management,
    component architecture, forms, data views, testing, and deployment."""
    return [topic.model_dump(mode="json") for topic in available_topics()]


@mcp.tool()
def get_guidance(topic: str) -> str:
    """Return the full bundled markdown guidance for a NiceGUI topic.
    Use `list_topics` to discover available topic names."""
    return load_guidance_text(topic)


@mcp.tool()
def search_guidance(query: str, topics: list[str] | None = None) -> list[dict]:
    """Search bundled NiceGUI guidance docs and return heading-aware snippets sorted by relevance.
    Use for broad exploration when you are unsure which topic to read.
    For ready-to-use code patterns, prefer `get_pattern` instead."""
    return [hit.model_dump(mode="json") for hit in search_guidance_text(query=query, topics=topics)]


@mcp.tool()
def analyze_nicegui_code(
    code: str,
    focus: list[str] | None = None,
    filename: str | None = None,
    context: str | None = None,
) -> dict:
    """Analyze NiceGUI code for known issues without applying fixes.
    Detects: layout/spacing problems, blocking calls in handlers, async handlers without
    feedback, scroll area height bugs, styling/props conflicts, non-persistent destructive
    dialogs, monolithic page functions, logic-heavy handlers, and state management smells.
    For most workflows, prefer `review_nicegui_code` which combines analysis with auto-fix."""
    return analyze_code(code=code, focus=focus, filename=filename, context=context).model_dump(mode="json")


@mcp.tool()
def fix_nicegui_code(code: str, aggressive: bool = False) -> dict:
    """Apply narrow deterministic NiceGUI code fixes and return updated code plus applied fix metadata.
    Safe fixes: CSS-in-props to .style(), missing min-h-0 insertion, persistent dialog props,
    time.sleep to asyncio.sleep in async handlers, and reload=True to reload=False.
    For most workflows, prefer `review_nicegui_code` which combines analysis with auto-fix."""
    return fix_code(code=code, aggressive=aggressive).model_dump(mode="json")


@mcp.tool()
def generate_nicegui_component(kind: str, mode: str = "default", details_json: str | None = None) -> dict:
    """Generate deterministic NiceGUI starter code for common layout, dialog, async, and component patterns.

    Valid kinds: layout_shell, confirmation_dialog, async_action_flow, controller_service_page,
    reusable_component, list_detail, filterable_table, form_sticky_actions, chart_sidebar_table.

    Use `list_component_kinds` to discover kinds and their supported modes."""
    details = json.loads(details_json) if details_json else {}
    return generate_component(kind=kind, mode=mode, details=details).model_dump(mode="json")


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
