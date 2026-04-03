# Data Views, Tables, and Charts

Sources
- https://nicegui.io/documentation

## Tables

`ui.table` is a good default for moderate data sets.

- keep column definitions explicit
- do not materialize huge row sets directly if pagination is expected
- refresh the table from one controller method rather than scattered mutations

## AG Grid

Use `ui.aggrid` when you need richer grid behavior, but remember that it exposes a more complex config surface.

- test grid options incrementally
- keep row data and server-side paging logic separated
- treat styling and theme choices as part of the component contract

## Charts Beside Filters

Dashboards commonly need a sidebar plus a flexible chart/table column.

- sidebar: `shrink-0`
- main content: `min-w-0`
- stacked chart and table cards inside the main content column

## Filterable List and Detail Views

Use one source of truth for search and filters, then feed both table and detail components from that state.
