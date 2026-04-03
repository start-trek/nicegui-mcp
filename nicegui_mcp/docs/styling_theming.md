# Styling and Theming

Sources
- https://nicegui.io/documentation

## `.style` vs `.classes` vs `.props`

Use each API for one job.

- `.style(...)` for raw CSS like `width`, `height`, `padding`, or `gap`
- `.classes(...)` for Tailwind or class-based styling
- `.props(...)` for Quasar component props like `dense`, `flat`, or `outlined`

Avoid CSS-like props such as `width=50%` inside `.props(...)`.

## Tailwind and Quasar Interactions

NiceGUI wraps Quasar components. Some Quasar props create classes or styles that override Tailwind expectations.

- `color='primary'` and `text-red-500` on the same button create confusing precedence.
- Tailwind layout utilities are usually safe.
- Tailwind color utilities mixed with Quasar color props should be used deliberately, not accidentally.

## Practical Defaults

- keep layout classes in `.classes(...)`
- keep sizing tweaks in `.style(...)`
- pick one color system per component where possible

Example

```python
ui.button('Save', color='primary').classes('px-4')
```

```python
ui.card().style('width: 24rem').classes('rounded-xl shadow-sm')
```

## Design Tokens

As apps grow, centralize repeated spacing, color, and surface choices.

- use shared class strings or helper functions
- keep component-level theming consistent
- avoid duplicating hard-coded visual choices across pages
