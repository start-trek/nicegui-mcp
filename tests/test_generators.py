from __future__ import annotations

import ast

from nicegui_mcp.generators import generate_component


def test_all_generators_return_code() -> None:
    kinds = [
        "layout_shell",
        "confirmation_dialog",
        "async_action_flow",
        "controller_service_page",
        "reusable_component",
        "list_detail",
        "filterable_table",
        "form_sticky_actions",
        "chart_sidebar_table",
    ]
    for kind in kinds:
        result = generate_component(kind)
        assert result.kind == kind
        assert result.code
        ast.parse(result.code)


def test_confirmation_dialog_destructive_mode() -> None:
    result = generate_component("confirmation_dialog", mode="destructive")
    assert "color=negative" in result.code


def test_controller_service_refreshable_mode() -> None:
    result = generate_component("controller_service_page", mode="refreshable")
    assert "@ui.refreshable" in result.code


def test_filterable_table_server_paginated_mode() -> None:
    result = generate_component("filterable_table", mode="server_paginated")
    assert "rowsNumber" in result.code
