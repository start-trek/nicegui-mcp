async def fetch_records() -> list[dict]:
    return []


async def on_click() -> None:
    ui.notify('Loading...', color='info')
    await fetch_records()
    ui.notify('Done', color='positive')
