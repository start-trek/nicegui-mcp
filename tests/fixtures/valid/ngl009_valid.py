import asyncio

from nicegui import ui


async def on_click() -> None:
    await asyncio.sleep(1)
    ui.notify('Done')


ui.button('Load', on_click=on_click)
