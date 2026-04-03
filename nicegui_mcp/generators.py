from __future__ import annotations

from textwrap import dedent

from .models import GenerationResult


def generate_component(kind: str, mode: str = "default", details: dict | None = None) -> GenerationResult:
    details = details or {}
    normalized = kind.strip().lower().replace("-", "_").replace(" ", "_")
    generators = {
        "layout_shell": _layout_shell,
        "confirmation_dialog": _confirmation_dialog,
        "async_action_flow": _async_action_flow,
        "controller_service_page": _controller_service_page,
        "reusable_component": _reusable_component,
        "list_detail": _list_detail,
        "filterable_table": _filterable_table,
        "form_sticky_actions": _form_sticky_actions,
        "chart_sidebar_table": _chart_sidebar_table,
    }
    try:
        return generators[normalized](mode=mode, details=details)
    except KeyError as exc:
        raise ValueError(f"Unknown generator kind: {kind}") from exc


def _layout_shell(mode: str, details: dict) -> GenerationResult:
    title = details.get("title", "NiceGUI App")
    code = dedent(
        f"""
        from nicegui import ui


        @ui.page('/')
        def home() -> None:
            with ui.header(elevated=True).classes('items-center justify-between'):
                ui.label('{title}').classes('text-lg font-semibold')
                ui.button(icon='menu', on_click=lambda: drawer.toggle()).props('flat round dense')

            with ui.left_drawer(value=False).classes('bg-slate-50') as drawer:
                ui.label('Navigation').classes('text-sm font-medium')
                ui.separator()
                ui.button('Dashboard').props('flat align=left')

            with ui.column().classes('w-full h-screen min-h-0 gap-0'):
                with ui.row().classes('w-full items-center justify-between px-4 py-3 border-b'):
                    ui.label('Page heading').classes('text-xl font-semibold')
                    ui.button('Refresh', icon='refresh')
                with ui.column().classes('w-full min-h-0 flex-1'):
                    with ui.scroll_area().classes('w-full h-full'):
                        with ui.column().classes('w-full gap-4 p-4'):
                            ui.card().classes('w-full')
        """
    ).strip()
    notes = [
        "The shell includes `min-h-0` and a scrollable content region so nested pages can grow without breaking scroll behavior.",
        "Move drawer items and route registration into dedicated modules once the app gains more than a few pages.",
    ]
    return GenerationResult(kind="layout_shell", mode=mode, code=code, notes=notes)


def _confirmation_dialog(mode: str, details: dict) -> GenerationResult:
    destructive = mode == "destructive"
    action_label = details.get("action_label", "Delete" if destructive else "Confirm")
    title = details.get("title", "Confirm action")
    message = details.get("message", "This action cannot be undone." if destructive else "Please confirm this action.")
    confirm_props = "unelevated color=negative" if destructive else "unelevated color=primary"
    code = dedent(
        f"""
        from __future__ import annotations

        import asyncio

        from nicegui import ui


        class ConfirmDialog:
            def __init__(self) -> None:
                self._result: asyncio.Future[bool] | None = None
                with ui.dialog().props('persistent') as self.dialog:
                    with ui.card().classes('w-[30rem] max-w-full gap-0'):
                        with ui.column().classes('w-full gap-3 p-5'):
                            self.title = ui.label('{title}').classes('text-lg font-semibold')
                            self.message = ui.label('{message}').classes('text-sm text-slate-600')
                        ui.separator()
                        with ui.row().classes('w-full items-center justify-end gap-2 sticky bottom-0 bg-white p-4'):
                            ui.button('Cancel', on_click=self._cancel).props('flat')
                            ui.button('{action_label}', on_click=self._confirm).props('{confirm_props}')

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
        """
    ).strip()
    notes = [
        "Keep the dialog instance in stable scope and reuse it instead of re-creating confirmation flows in each handler.",
        "The sticky bottom action row keeps the primary action visible even when dialog content grows.",
    ]
    return GenerationResult(kind="confirmation_dialog", mode=mode, code=code, notes=notes)


def _async_action_flow(mode: str, details: dict) -> GenerationResult:
    button_label = details.get("button_label", "Run sync")
    code = dedent(
        f"""
        from nicegui import background_tasks, ui


        async def sync_service() -> None:
            await ui.run.io_bound(lambda: None)


        @ui.page('/')
        def page() -> None:
            state = ui.state(False)

            async def on_sync() -> None:
                state.set(True)
                action_button.disable()
                ui.notify('Starting sync...', color='info')
                try:
                    await sync_service()
                    ui.notify('Sync finished', color='positive')
                except Exception as exc:  # pragma: no cover - example code
                    ui.notify(f'Sync failed: {{exc}}', color='negative')
                finally:
                    state.set(False)
                    action_button.enable()

            with ui.row().classes('items-center gap-3'):
                action_button = ui.button('{button_label}', on_click=on_sync)
                ui.spinner(size='sm').bind_visibility_from(state, 'value')
        """
    ).strip()
    notes = [
        "Disable the trigger before awaiting the long-running work so users cannot queue duplicate actions.",
        "Replace the inline service stub with `ui.run.io_bound`, `ui.run.cpu_bound`, or a dedicated controller call.",
    ]
    return GenerationResult(kind="async_action_flow", mode=mode, code=code, notes=notes)


def _controller_service_page(mode: str, details: dict) -> GenerationResult:
    page_name = details.get("page_name", "orders")
    refreshable = mode == "refreshable"
    if refreshable:
        code = dedent(
            f"""
            from dataclasses import dataclass, field

            from nicegui import ui


            class OrdersService:
                async def fetch_rows(self) -> list[dict]:
                    return [{{'id': 1, 'status': 'new'}}]


            @dataclass
            class OrdersController:
                service: OrdersService
                rows: list[dict] = field(default_factory=list)
                columns: list[dict] = field(default_factory=lambda: [{{'name': 'id', 'label': 'ID', 'field': 'id'}}])

                async def load(self) -> None:
                    self.rows = await self.service.fetch_rows()


            @ui.refreshable
            def render_table(controller: OrdersController) -> None:
                ui.table(columns=controller.columns, rows=controller.rows)


            @ui.page('/{page_name}')
            async def {page_name}_page() -> None:
                controller = OrdersController(service=OrdersService())
                await controller.load()
                render_table(controller)
            """
        ).strip()
    else:
        code = dedent(
            f"""
            from dataclasses import dataclass, field

            from nicegui import ui


            class OrdersService:
                async def fetch_rows(self) -> list[dict]:
                    return [{{'id': 1, 'status': 'new'}}]


            @dataclass
            class OrdersController:
                service: OrdersService
                rows: list[dict] = field(default_factory=list)
                columns: list[dict] = field(default_factory=lambda: [{{'name': 'id', 'label': 'ID', 'field': 'id'}}])

                async def load(self) -> None:
                    self.rows = await self.service.fetch_rows()


            @ui.page('/{page_name}')
            async def {page_name}_page() -> None:
                controller = OrdersController(service=OrdersService())
                await controller.load()
                ui.table(columns=controller.columns, rows=controller.rows)
            """
        ).strip()
    notes = [
        "Keep the page handler thin: instantiate the controller, call a controller method, then render from controller state.",
        "Split service, controller, and page modules once the app grows beyond a single page example.",
    ]
    return GenerationResult(kind="controller_service_page", mode=mode, code=code, notes=notes)


def _reusable_component(mode: str, details: dict) -> GenerationResult:
    component_name = details.get("component_name", "ReferenceCard")
    code = dedent(
        f"""
        from nicegui import ui


        def {component_name.lower()}(item: dict, mode: str = 'summary') -> None:
            with ui.card().classes('w-full gap-3'):
                with ui.row().classes('w-full items-start justify-between'):
                    ui.label(item['title']).classes('text-base font-semibold')
                    ui.badge(item.get('status', 'draft'))
                ui.label(item.get('summary', '')).classes('text-sm text-slate-600')
                if mode == 'detail':
                    ui.separator()
                    ui.markdown(item.get('details', 'No additional details yet.'))
        """
    ).strip()
    notes = [
        "Use a mode-driven component when the same data needs summary and detail presentations without copy-pasting the markup.",
    ]
    return GenerationResult(kind="reusable_component", mode=mode, code=code, notes=notes)


def _list_detail(mode: str, details: dict) -> GenerationResult:
    code = dedent(
        """
        from nicegui import ui


        @ui.page('/items')
        def items_page() -> None:
            selected = ui.state(None)
            rows = [{'id': 1, 'name': 'First'}, {'id': 2, 'name': 'Second'}]

            with ui.row().classes('w-full min-h-0 gap-4'):
                with ui.column().classes('w-72 shrink-0 gap-2'):
                    for row in rows:
                        ui.button(row['name'], on_click=lambda item=row: selected.set(item)).props('flat align=left')
                with ui.column().classes('min-h-0 min-w-0 flex-1'):
                    with ui.scroll_area().classes('w-full h-full'):
                        with ui.card().classes('w-full'):
                            ui.label().bind_text_from(selected, 'value', backward=lambda item: item['name'] if item else 'Nothing selected')
        """
    ).strip()
    return GenerationResult(
        kind="list_detail",
        mode=mode,
        code=code,
        notes=["The list/detail shell keeps the detail panel scrollable without forcing the sidebar to grow."],
    )


def _filterable_table(mode: str, details: dict) -> GenerationResult:
    server_paginated = mode == "server_paginated"
    code = dedent(
        f"""
        from nicegui import ui


        async def fetch_rows(search: str, page: int, rows_per_page: int) -> tuple[list[dict], int]:
            rows = [{{'id': i, 'name': f'Row {{i}}'}} for i in range(1, 251)]
            filtered = [row for row in rows if search.lower() in row['name'].lower()]
            start = (page - 1) * rows_per_page
            return filtered[start:start + rows_per_page], len(filtered)


        @ui.page('/table')
        async def table_page() -> None:
            search = ui.state('')
            table = ui.table(
                columns=[{{'name': 'id', 'label': 'ID', 'field': 'id'}}, {{'name': 'name', 'label': 'Name', 'field': 'name'}}],
                rows=[],
                pagination={{'page': 1, 'rowsPerPage': 10, 'rowsNumber': 0}},
            )

            async def refresh() -> None:
                rows, total = await fetch_rows(search.value, table.pagination['page'], table.pagination['rowsPerPage'])
                table.rows = rows
                table.pagination['rowsNumber'] = total
                table.update()

            ui.input('Search', on_change=lambda e: search.set(e.value)).props('outlined dense clearable')
            table.on('request', lambda _: ui.run_javascript(''))
            {'await refresh()' if server_paginated else 'await refresh()'}
        """
    ).strip()
    notes = [
        "Keep filtering and pagination in one refresh function so it is easy to swap from local data to a real backend.",
        "Use the `request` event and `rowsNumber` for large datasets instead of materializing every row at once.",
    ]
    return GenerationResult(kind="filterable_table", mode=mode, code=code, notes=notes)


def _form_sticky_actions(mode: str, details: dict) -> GenerationResult:
    code = dedent(
        """
        from nicegui import ui


        @ui.page('/form')
        def form_page() -> None:
            with ui.column().classes('w-full h-screen min-h-0 gap-0'):
                with ui.scroll_area().classes('w-full h-full'):
                    with ui.column().classes('w-full gap-4 p-4'):
                        name = ui.input('Name', validation={'Required': lambda value: bool(value)})
                        email = ui.input('Email')
                        ui.textarea('Notes')
                ui.separator()
                with ui.row().classes('w-full items-center justify-end gap-2 sticky bottom-0 bg-white p-4'):
                    ui.button('Cancel').props('flat')
                    ui.button('Save', on_click=lambda: all(field.validate() for field in (name, email)))
        """
    ).strip()
    return GenerationResult(
        kind="form_sticky_actions",
        mode=mode,
        code=code,
        notes=["Keep primary form actions visible at the bottom of the screen when long forms scroll."],
    )


def _chart_sidebar_table(mode: str, details: dict) -> GenerationResult:
    code = dedent(
        """
        from nicegui import ui


        @ui.page('/dashboard')
        def dashboard_page() -> None:
            with ui.row().classes('w-full min-h-0 gap-4'):
                with ui.column().classes('w-72 shrink-0 gap-4'):
                    ui.input('Search').props('outlined dense')
                    ui.select(['Open', 'Closed'], label='Status')
                with ui.column().classes('min-h-0 min-w-0 flex-1 gap-4'):
                    with ui.card().classes('w-full'):
                        ui.echart({'xAxis': {'type': 'category', 'data': ['A', 'B']}, 'yAxis': {'type': 'value'}, 'series': [{'type': 'bar', 'data': [3, 7]}]})
                    with ui.card().classes('w-full'):
                        ui.table(columns=[{'name': 'name', 'label': 'Name', 'field': 'name'}], rows=[{'name': 'Alpha'}])
        """
    ).strip()
    return GenerationResult(
        kind="chart_sidebar_table",
        mode=mode,
        code=code,
        notes=["The main content column includes `min-w-0` so charts and tables can shrink next to the sidebar."],
    )
