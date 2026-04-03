# Dialogs

Sources
- https://nicegui.io/documentation

## Persistent Confirmation Flows

Dialogs that confirm destructive actions should usually be persistent.

- clicking outside should not dismiss a delete confirmation
- users should always have visible cancel and confirm actions
- keep destructive copy explicit

Example

```python
with ui.dialog().props('persistent') as dialog:
    with ui.card().classes('w-[28rem] max-w-full gap-0'):
        with ui.column().classes('gap-3 p-5'):
            ui.label('Delete this record?').classes('text-lg font-semibold')
            ui.label('This action cannot be undone.')
        ui.separator()
        with ui.row().classes('items-center justify-end gap-2 sticky bottom-0 bg-white p-4'):
            ui.button('Cancel', on_click=dialog.close).props('flat')
            ui.button('Delete', on_click=delete_record).props('unelevated color=negative')
```

## Lifetime and Scope

Keep reusable dialogs in stable scope.

- avoid creating them inside narrow transient contexts
- reuse awaitable confirmation helpers
- open existing dialog instances from callbacks

## Sticky Actions

Long dialogs should keep primary actions visible.

- separate the scrollable body from the action row
- dock the action row at the bottom of the dialog card
- keep spacing and hierarchy consistent across dialogs
