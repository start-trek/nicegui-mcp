from nicegui import ui


@ui.page('/')
def home() -> None:
    ui.label('Hello')
    ui.button('Open')
