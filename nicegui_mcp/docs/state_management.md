# State Management

Sources
- https://nicegui.io/documentation

## Local UI State

NiceGUI gives you enough primitives to build state, but it does not impose a single architecture.

- `ui.state(...)` is useful for local reactive values
- `@ui.refreshable` lets you rebuild a section from tracked state
- small apps can start simple, but large apps need boundaries early

## Controller and Session Patterns

Good NiceGUI apps keep domain state out of the page body.

- controllers own use-case logic
- services talk to APIs or databases
- pages orchestrate and render

## Prefer Explicit Modes

Boolean sprawl is hard to read.

- avoid `show_list`, `show_detail`, `show_edit`, `show_modal` when only one mode is valid at a time
- prefer a single explicit enum or mode string

## Refreshable Rendering

Use refreshable sections for data views that re-render from state rather than mutating many widgets one by one.
