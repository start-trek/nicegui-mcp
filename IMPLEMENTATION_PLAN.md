# NiceGUI MCP v1.1 Implementation Plan

## Running Checklist
- [x] Rename package, script, README, and examples from Obsidian to NiceGUI.
- [x] Remove Obsidian domain docs, fixtures, overlays, and integration baggage.
- [x] Add expanded NiceGUI guidance corpus based on real-world problem areas.
- [x] Ship topic listing, retrieval, and search.
- [x] Ship analyzer models plus the first high-confidence rule set.
- [x] Ship safe fixers for deterministic rewrites only.
- [x] Ship generators for layout shell, async flows, dialogs, forms, tables, and controller/service structure.
- [x] Rewrite tests around docs, analyzers, fixers, and generators.
- [x] Update README around a docs -> analyze -> fix -> reanalyze workflow.
- [x] Reach local pytest green for all core features.

## Sources
- Official docs: https://nicegui.io/documentation
- Search index: https://nicegui.io/static/search_index.json
- Research report: [/Users/derekdosterschill/Downloads/md.md](/Users/derekdosterschill/Downloads/md.md)

## Repo Map
- Keep and adapt: `pyproject.toml`, `README.md`, `examples/claude_desktop_config.json`, the FastMCP server pattern, package-resource loading, and the unit-test layout.
- Delete: Obsidian profiles, runtime overlays, Obsidian docs, runtime examples, integration baggage, vault fixtures, and committed egg-info artifacts.
- Add: `nicegui_mcp/profile.py`, `nicegui_mcp/analyzers.py`, `nicegui_mcp/fixers.py`, `nicegui_mcp/generators.py`, the 10-topic docs corpus, and NiceGUI-specific fixtures/tests.

## v1.1 Scope
- Tools: `list_topics`, `get_guidance`, `search_guidance`, `analyze_nicegui_code`, `fix_nicegui_code`, `generate_nicegui_component`
- Resources: `nicegui://topics/index`, `nicegui://guidance/{topic}`
- Topics: `layout_spacing_scrolling`, `async_tasks_performance`, `styling_theming`, `dialogs`, `state_management`, `component_architecture`, `forms_validation`, `data_views_tables_charts`, `testing`, `deployment_runtime`
- Tier 1 analyzers: `NGL-003`, `NGL-013`, `NGL-004`, `NGL-005`, `NGL-007`, `NGL-009`, `NGL-010`, `NGL-008`, `NGL-018`
- Tier 2 analyzers: `NGL-001`, `NGL-002`, `NGL-014`, `NGL-015`, `NGL-016`, `NGL-017`, `NGL-019`, `NGL-020`
- Tier 3 analyzers: `NGL-006`, `NGL-011`, `NGL-012`
- Safe fixers: `NGL-003`, `NGL-004`, `NGL-007`, `NGL-009`, `NGL-019`
- Generators: `layout_shell`, `confirmation_dialog`, `async_action_flow`, `controller_service_page`, `reusable_component`, `list_detail`, `filterable_table`, `form_sticky_actions`, `chart_sidebar_table`

## Execution Notes
- The server remains local-first and deterministic.
- Guidance is a curated offline subset, not a full NiceGUI docs mirror.
- Heuristic rules remain low-confidence and guidance-only.
