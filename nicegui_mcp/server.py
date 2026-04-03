from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from .analyzers import analyze_code
from .fixers import fix_code
from .generators import generate_component
from .registry import available_topics, get_topic, load_guidance_text, search_guidance_text

INSTRUCTIONS = (
    "NiceGUI MCP is a docs-first, static-analysis MCP server for local NiceGUI development. "
    "Use it to read bundled guidance, search topic docs, analyze code snippets for common NiceGUI issues, "
    "apply narrow deterministic fixes, and generate starter patterns for common app structures."
)

mcp = FastMCP(
    name="NiceGUI MCP",
    instructions=INSTRUCTIONS,
    stateless_http=True,
    json_response=True,
)


@mcp.resource("nicegui://topics/index")
def topic_index() -> str:
    payload = [topic.model_dump(mode="json") for topic in available_topics()]
    return json.dumps(payload, indent=2)


@mcp.resource("nicegui://guidance/{topic}")
def guidance_resource(topic: str) -> str:
    return load_guidance_text(topic)


@mcp.tool()
def list_topics() -> list[dict]:
    """List the bundled NiceGUI guidance topics with summaries and tags."""
    return [topic.model_dump(mode="json") for topic in available_topics()]


@mcp.tool()
def get_guidance(topic: str) -> str:
    """Return the full bundled markdown guidance for a NiceGUI topic."""
    return load_guidance_text(topic)


@mcp.tool()
def search_guidance(query: str, topics: list[str] | None = None) -> list[dict]:
    """Search bundled NiceGUI guidance docs and return heading-aware snippets sorted by relevance."""
    return [hit.model_dump(mode="json") for hit in search_guidance_text(query=query, topics=topics)]


@mcp.tool()
def analyze_nicegui_code(
    code: str,
    focus: list[str] | None = None,
    filename: str | None = None,
    context: str | None = None,
) -> dict:
    """Analyze NiceGUI code for known layout, async, dialog, styling, and architecture issues."""
    return analyze_code(code=code, focus=focus, filename=filename, context=context).model_dump(mode="json")


@mcp.tool()
def fix_nicegui_code(code: str, aggressive: bool = False) -> dict:
    """Apply narrow deterministic NiceGUI code fixes and return updated code plus applied fix metadata."""
    return fix_code(code=code, aggressive=aggressive).model_dump(mode="json")


@mcp.tool()
def generate_nicegui_component(kind: str, mode: str = "default", details_json: str | None = None) -> dict:
    """Generate deterministic NiceGUI starter code for common layout, dialog, async, and component patterns."""
    details = json.loads(details_json) if details_json else {}
    return generate_component(kind=kind, mode=mode, details=details).model_dump(mode="json")


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
