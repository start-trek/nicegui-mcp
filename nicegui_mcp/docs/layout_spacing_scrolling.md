# Layout, Spacing, and Scrolling

Sources
- https://nicegui.io/documentation
- https://nicegui.io/static/search_index.json

## Default Containers

NiceGUI rows and columns are already flex containers. Treat them as opinionated layout primitives, not as empty HTML wrappers.

- `ui.row()` wraps by default.
- `ui.column()` stacks children vertically.
- NiceGUI adds its own spacing defaults, so copied Tailwind snippets often need adjustment.

## Gap Control

Prefer one spacing strategy per container.

- Use `.style('gap: 0.5rem')` when you want explicit CSS control.
- Use a small `gap-*` class when it is already part of your styling system.
- Avoid stacking a large `gap-*` utility on top of layout defaults without checking the result.

Examples

```python
with ui.column().style('gap: 0.5rem'):
    ui.input('Name')
    ui.input('Email')
```

```python
with ui.row().classes('items-center gap-2'):
    ui.button('Save')
    ui.button('Cancel').props('flat')
```

## Row Wrapping and Width Budgets

Rows frequently wrap because percentage widths plus gap spacing exceed the available width.

- Two `width: 50%` children inside a gapped row often overflow.
- `w-1/2` plus explicit gap has the same problem.
- If wrapping is undesirable, shrink the widths or adopt a no-wrap layout on purpose.

## Scroll Areas That Actually Work

`ui.scroll_area()` usually needs a constrained parent and a `min-h-0` flex child.

- A scroll area with `h-full` but no constrained parent height is usually broken.
- The flex child that owns the scroll area often needs `min-h-0`.
- App shells with header + body + sticky footer work best when the body column gets `min-h-0`.

Example

```python
with ui.column().classes('w-full h-screen min-h-0 gap-0'):
    with ui.row().classes('items-center justify-between p-4 border-b'):
        ui.label('Header')
    with ui.column().classes('w-full min-h-0 flex-1'):
        with ui.scroll_area().classes('w-full h-full'):
            with ui.column().classes('gap-4 p-4'):
                ui.card()
```

## Chart and Table Layouts

Wide data views need horizontal shrinking support.

- Use `min-w-0` on the flex child that should shrink.
- Keep sidebars `shrink-0` and let the main content column absorb pressure.
- Prefer a shared layout shell rather than per-page spacing hacks.
