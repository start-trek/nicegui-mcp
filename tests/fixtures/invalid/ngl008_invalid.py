from nicegui import ui


def fetch_data() -> list[int]:
    return [1, 2, 3]


def on_click() -> None:
    rows = fetch_data()
    if rows:
        for row in rows:
            if row > 1:
                ui.notify(str(row))
            else:
                ui.notify('small')
    if len(rows) > 2:
        ui.notify('many')
    ui.notify('done')


ui.button('Go', on_click=on_click)
