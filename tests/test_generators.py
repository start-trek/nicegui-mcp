from __future__ import annotations

import ast

from nicegui_mcp.generators import generate_component, list_kinds


def test_list_kinds_returns_all() -> None:
    kinds = list_kinds()
    assert len(kinds) == 9
    for entry in kinds:
        assert "kind" in entry
        assert "description" in entry


def test_component_kinds_match_generators() -> None:
    list_kinds_set = {entry["kind"] for entry in list_kinds()}
    generator_kinds = [
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
    assert list_kinds_set == set(generator_kinds)


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
