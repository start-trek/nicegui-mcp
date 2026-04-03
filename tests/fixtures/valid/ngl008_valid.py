from nicegui import ui


def on_click() -> None:
    ui.notify('done')


ui.button('Go', on_click=on_click)
