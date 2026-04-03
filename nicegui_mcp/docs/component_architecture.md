# Component Architecture

Sources
- https://nicegui.io/documentation

## Layout Shells

Centralize the app frame early.

- shared header
- shared drawer or navigation
- shared scrollable body pattern
- page-level content plugged into the shell

## Thin Page Handlers

Keep `@ui.page` functions small.

- instantiate controller/session objects
- call controller methods
- render from controller state
- extract repeated sections into reusable components

## Reusable Components

NiceGUI components can be simple functions.

- a reference card can accept `mode='summary'` or `mode='detail'`
- repeated list rows should become helpers
- shared visual patterns should not be copy-pasted across pages

## Services and Controllers

Split responsibilities clearly.

- services: API, database, file I/O
- controllers: state and orchestration
- UI: layout, events, and presentation
