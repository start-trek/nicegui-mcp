import time

from nicegui import ui


def on_click() -> None:
    time.sleep(1)


ui.button('Load', on_click=on_click)
