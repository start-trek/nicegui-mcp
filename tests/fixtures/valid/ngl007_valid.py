from nicegui import ui

with ui.dialog().props('persistent'):
    ui.label('Delete this record?')
    ui.button('Delete')
