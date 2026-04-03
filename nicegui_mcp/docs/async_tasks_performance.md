# Async Tasks and Performance

Sources
- https://nicegui.io/documentation

## Event Loop Basics

NiceGUI lives on an async event loop. Blocking that loop freezes UI updates and websocket heartbeats.

- `time.sleep(...)` blocks.
- synchronous `requests.get(...)` blocks.
- large CPU work in handlers blocks unless you offload it.

## Safe Patterns

- Use `ui.run.io_bound(...)` for blocking I/O.
- Use `ui.run.cpu_bound(...)` for CPU-heavy work.
- Use `background_tasks.create(...)` when work should continue after the current interaction returns.
- Use `ui.timer(...)` for periodic refreshes instead of manual polling loops.

## Long-Running Action UX

Async work needs visible feedback.

- disable the triggering button
- show a spinner or progress indicator
- notify on success
- notify on failure

Example

```python
async def on_sync() -> None:
    button.disable()
    ui.notify('Starting sync...', color='info')
    try:
        await ui.run.io_bound(sync_service)
        ui.notify('Sync finished', color='positive')
    except Exception as exc:
        ui.notify(f'Sync failed: {exc}', color='negative')
    finally:
        button.enable()
```

## Reload Caveats

`ui.run(reload=True)` is a development convenience, not a production default.

- keep it in a dev-only launcher
- avoid conflating reload behavior with runtime behavior
- investigate background task behavior if reload makes development noisy
