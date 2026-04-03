# NiceGUI MCP

NiceGUI MCP is a docs-first [Model Context Protocol](https://modelcontextprotocol.io/) server for local NiceGUI development. It bundles curated guidance, searches that guidance, analyzes pasted NiceGUI code for common problems, applies a narrow safe fixer set, and generates starter patterns for real app workflows.

## What It Does

- Guidance lookup for common NiceGUI problem areas
- Topic search across bundled docs
- Static analysis for layout, scrolling, async, dialog, styling, and architecture issues
- Deterministic safe fixes for a small allowlisted set of patterns
- Starter generation for layout shells, dialogs, async flows, forms, tables, and controller/service splits

## What It Does Not Do

- repo-wide indexing
- arbitrary code execution
- browser automation
- embeddings or vector search
- hosted multi-user deployment
- large-scale automated refactors

## Bundled Topics

- `layout_spacing_scrolling`
- `async_tasks_performance`
- `styling_theming`
- `dialogs`
- `state_management`
- `component_architecture`
- `forms_validation`
- `data_views_tables_charts`
- `testing`
- `deployment_runtime`

## Tools

- `list_topics()`
- `get_guidance(topic)`
- `search_guidance(query, topics=None)`
- `analyze_nicegui_code(code, focus=None, filename=None, context=None)`
- `fix_nicegui_code(code, aggressive=False)`
- `generate_nicegui_component(kind, mode='default', details_json=None)`

## Resources

- `nicegui://topics/index`
- `nicegui://guidance/{topic}`

## Recommended Workflow

1. Search or read guidance for the problem area.
2. Analyze the relevant NiceGUI snippet.
3. Apply safe fixes where the fixer set supports them.
4. Reanalyze the updated code.
5. Generate a better pattern when the issue is architectural rather than local.

## Installation

```bash
uv sync
```

## Run

```bash
uv run nicegui-mcp
```

## Test

```bash
uv run pytest -q
```

## Example MCP Client Config

```json
{
  "mcpServers": {
    "nicegui-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/nicegui-mcp", "nicegui-mcp"]
    }
  }
}
```

## Project Layout

```text
nicegui_mcp/
├── analyzers.py
├── docs/
├── fixers.py
├── generators.py
├── models.py
├── profile.py
├── registry.py
└── server.py
```
