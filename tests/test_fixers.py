from __future__ import annotations

from nicegui_mcp.fixers import fix_code


def test_props_to_style_fix() -> None:
    result = fix_code("ui.button('Save').props('width=50% outlined')\n")
    assert ".props('outlined').style('width: 50%')" in result.updated_code


def test_min_height_fix() -> None:
    code = """
with ui.column():
    ui.scroll_area().classes('h-full')
"""
    result = fix_code(code)
    assert "min-h-0" in result.updated_code


def test_persistent_dialog_fix() -> None:
    code = """
with ui.dialog():
    ui.label('Delete this record?')
"""
    result = fix_code(code)
    assert "persistent" in result.updated_code


def test_reload_fix() -> None:
    result = fix_code("from nicegui import ui\nui.run(reload=True)\n")
    assert "reload=False" in result.updated_code


def test_async_time_sleep_fix() -> None:
    code = """
import time

async def on_click() -> None:
    time.sleep(1)
"""
    result = fix_code(code)
    assert "await asyncio.sleep(1)" in result.updated_code
    assert "import asyncio" in result.updated_code


def test_idempotent_second_pass() -> None:
    code = "ui.button('Save').props('width=50%')\n"
    once = fix_code(code)
    twice = fix_code(once.updated_code)
    assert once.updated_code == twice.updated_code
