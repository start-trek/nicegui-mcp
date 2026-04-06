from __future__ import annotations

from textwrap import dedent

from .models import PatternResult


PATTERNS: dict[str, PatternResult] = {
    "async_ui_update": PatternResult(
        pattern_name="async_ui_update",
        title="Async UI Updates",
        snippet=dedent("""
            from nicegui import ui

            async def on_action() -> None:
                button.disable()
                spinner.visible = True
                ui.notify('Starting action...', color='info')
                try:
                    await some_async_work()
                    ui.notify('Action completed', color='positive')
                except Exception as exc:
                    ui.notify(f'Action failed: {exc}', color='negative')
                finally:
                    button.enable()
                    spinner.visible = False

            with ui.row().classes('items-center gap-2'):
                button = ui.button('Run action', on_click=on_action)
                spinner = ui.spinner(size='sm').bind_visibility_from(button, 'disabled', backward=lambda x: not x)
        """).strip(),
        explanation="NiceGUI async handlers should disable the trigger, show progress, and always re-enable in a finally block.",
        pitfalls=[
            "forgetting to disable trigger",
            "missing error feedback", 
            "not re-enabling on failure"
        ]
    ),
    
    "dialog_open_close": PatternResult(
        pattern_name="dialog_open_close",
        title="Dialog Open/Close Flow",
        snippet=dedent("""
            from __future__ import annotations

            import asyncio

            from nicegui import ui


            class ConfirmDialog:
                def __init__(self) -> None:
                    self._result: asyncio.Future[bool] | None = None
                    with ui.dialog().props('persistent') as dialog:
                        with ui.card().classes('w-[30rem] max-w-full gap-0'):
                            with ui.column().classes('w-full gap-3 p-5'):
                                self.title = ui.label('Confirm action').classes('text-lg font-semibold')
                                self.message = ui.label('Are you sure?').classes('text-sm text-slate-600')
                            ui.separator()
                            with ui.row().classes('w-full items-center justify-end gap-2 sticky bottom-0 bg-white p-4'):
                                ui.button('Cancel', on_click=self._cancel).props('flat')
                                ui.button('Confirm', on_click=self._confirm).props('unelevated color=primary')

                async def ask(self, title: str, message: str) -> bool:
                    self.title.set_text(title)
                    self.message.set_text(message)
                    self._result = asyncio.get_running_loop().create_future()
                    self.dialog.open()
                    return await self._result

                def _confirm(self) -> None:
                    if self._result and not self._result.done():
                        self._result.set_result(True)
                    self.dialog.close()

                def _cancel(self) -> None:
                    if self._result and not self._result.done():
                        self._result.set_result(False)
                    self.dialog.close()


            # Usage
            dialog = ConfirmDialog()

            async def on_delete() -> None:
                if await dialog.ask('Delete item', 'This cannot be undone.'):
                    ui.notify('Item deleted', color='positive')
        """).strip(),
        explanation="Create one dialog instance and reuse it. Use asyncio.Future for awaitable results.",
        pitfalls=[
            "not using persistent for destructive confirms",
            "creating new dialog instances per call",
            "forgetting to resolve the future on cancel"
        ]
    ),
    
    "timer_driven_refresh": PatternResult(
        pattern_name="timer_driven_refresh",
        title="Timer-Driven Refresh",
        snippet=dedent("""
            from nicegui import ui

            @ui.refreshable
            def status_display() -> None:
                status = get_current_status()  # Your data fetching logic
                ui.label(f'Status: {status}')

            @ui.page('/')
            def page() -> None:
                status_display()
                ui.timer(5.0, status_display.refresh)  # Refresh every 5 seconds
        """).strip(),
        explanation="Use ui.timer for periodic updates. Pair with @ui.refreshable for clean re-rendering.",
        pitfalls=[
            "timer interval too short causing UI thrash",
            "not gating refresh behind active-tab check",
            "timer not stopped on page teardown"
        ]
    ),
    
    "table_crud": PatternResult(
        pattern_name="table_crud", 
        title="Table CRUD Pattern",
        snippet=dedent("""
            from dataclasses import dataclass, field

            from nicegui import ui


            @dataclass
            class TableController:
                rows: list[dict] = field(default_factory=list)

                def add_row(self, row: dict) -> None:
                    self.rows.append(row)

                def update_row(self, index: int, row: dict) -> None:
                    self.rows[index] = row

                def delete_row(self, index: int) -> None:
                    del self.rows[index]


            @ui.page('/')
            def page() -> None:
                controller = TableController()
                controller.rows = [{'id': 1, 'name': 'Item 1'}]

                table = ui.table(
                    columns=[{'name': 'id', 'label': 'ID', 'field': 'id'}, 
                           {'name': 'name', 'label': 'Name', 'field': 'name'}],
                    rows=controller.rows
                )

                def add_item() -> None:
                    new_id = max(row['id'] for row in controller.rows) + 1 if controller.rows else 1
                    controller.add_row({'id': new_id, 'name': f'Item {new_id}'})
                    table.update()

                ui.button('Add item', on_click=add_item)
        """).strip(),
        explanation="Keep rows in a controller. Call table.update() after mutations.",
        pitfalls=[
            "mutating rows list in place without calling table.update()",
            "large inline row sets",
            "missing optimistic UI feedback"
        ]
    ),
    
    "value_binding": PatternResult(
        pattern_name="value_binding",
        title="Value Binding",
        snippet=dedent("""
            from nicegui import ui

            @ui.page('/')
            def page() -> None:
                text_input = ui.input('Enter text')
                display_label = ui.label()

                # Two-way binding: input value controls label text
                text_input.bind_value_to(display_label, 'text')

                # One-way binding: display only
                # display_label.bind_text_from(text_input, 'value')
        """).strip(),
        explanation="Use bind_value_to for two-way and bind_text_from for one-way display.",
        pitfalls=[
            "binding to a property that does not exist",
            "circular bindings",
            "using lambda backward functions that raise on None"
        ]
    ),
    
    "background_task": PatternResult(
        pattern_name="background_task",
        title="Background Task Coordination",
        snippet=dedent("""
            from __future__ import annotations

            import logging

            from nicegui import background_tasks, ui

            logger = logging.getLogger(__name__)

            async def process_data(data: str) -> None:
                try:
                    # Simulate background work
                    await ui.run.io_bound(lambda: len(data))
                    ui.notify('Processing completed', color='positive')
                except Exception as exc:
                    logger.exception("Background task failed")
                    ui.notify(f'Processing failed: {exc}', color='negative')

            @ui.page('/')
            def page() -> None:
                def start_processing() -> None:
                    background_tasks.create(process_data('sample data'))
                    ui.notify('Processing started...', color='info')

                ui.button('Start processing', on_click=start_processing)
        """).strip(),
        explanation="Always handle exceptions inside background tasks. Use ui.notify only from the originating client context.",
        pitfalls=[
            "fire-and-forget without logging",
            "no error handling in the background coroutine",
            "assuming UI context is available inside the task"
        ]
    ),
    
    "navigation_pages": PatternResult(
        pattern_name="navigation_pages",
        title="Multi-Page Navigation",
        snippet=dedent("""
            from nicegui import ui

            def shared_layout(title: str) -> None:
                with ui.header(elevated=True).classes('items-center justify-between'):
                    ui.label(title).classes('text-lg font-semibold')
                    ui.button(icon='menu', on_click=lambda: drawer.toggle()).props('flat round dense')

                with ui.left_drawer(value=False).classes('bg-slate-50') as drawer:
                    ui.label('Navigation').classes('text-sm font-medium')
                    ui.separator()
                    ui.button('Home', on_click=lambda: ui.navigate.to('/')).props('flat align=left')
                    ui.button('About', on_click=lambda: ui.navigate.to('/about')).props('flat align=left')

            @ui.page('/')
            def home() -> None:
                shared_layout('Home')
                with ui.column().classes('w-full min-h-0 flex-1'):
                    ui.label('Home page content')

            @ui.page('/about')
            def about() -> None:
                shared_layout('About')
                with ui.column().classes('w-full min-h-0 flex-1'):
                    ui.label('About page content')
        """).strip(),
        explanation="Share layout via a common function or component called at the top of each page handler.",
        pitfalls=[
            "duplicating header/drawer across pages",
            "using ui.navigate.to inside async without await",
            "not using ui.page decorator"
        ]
    ),
    
    "scroll_area_setup": PatternResult(
        pattern_name="scroll_area_setup",
        title="Scroll Area Setup",
        snippet=dedent("""
            from nicegui import ui

            @ui.page('/')
            def page() -> None:
                with ui.column().classes('w-full h-screen min-h-0 gap-0'):
                    # Header or other fixed content
                    with ui.row().classes('w-full items-center justify-between p-4'):
                        ui.label('Page title').classes('text-xl font-semibold')
                    
                    # Scrollable content area
                    with ui.column().classes('w-full min-h-0 flex-1'):
                        with ui.scroll_area().classes('w-full h-full'):
                            with ui.column().classes('w-full gap-4 p-4'):
                                # Content that can overflow
                                for i in range(50):
                                    ui.card().classes('w-full').props('flat')
        """).strip(),
        explanation="Scroll areas need a height-constrained ancestor. Add min-h-0 to the flex parent.",
        pitfalls=[
            "missing min-h-0 on flex parent",
            "no constrained height ancestor",
            "nesting scroll areas accidentally"
        ]
    )
}


def get_pattern_by_name(name: str) -> PatternResult:
    if name not in PATTERNS:
        raise ValueError(f"Unknown pattern: {name}")
    return PATTERNS[name]


def list_pattern_names() -> list[dict[str, str]]:
    return [{"name": name, "title": pattern.title} for name, pattern in PATTERNS.items()]
