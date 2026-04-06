from __future__ import annotations

from nicegui_mcp.server import (
    analyze_nicegui_code,
    fix_nicegui_code,
    generate_nicegui_component,
    get_guidance,
    list_component_kinds,
    list_topics,
    search_guidance,
    topic_index,
    review_nicegui_code,
    preflight,
)


def test_list_topics_tool() -> None:
    topics = list_topics()
    assert len(topics) == 10
    assert topics[0]["name"]


def test_guidance_tool() -> None:
    text = get_guidance("dialogs")
    assert "persistent" in text


def test_search_tool() -> None:
    hits = search_guidance("scroll area", topics=["layout_spacing_scrolling"])
    assert hits
    assert all(hit["topic"] == "layout_spacing_scrolling" for hit in hits)


def test_analyze_tool() -> None:
    result = analyze_nicegui_code("ui.button('Save').props('width=50%')")
    assert any(finding["rule_id"] == "NGL-003" for finding in result["findings"])


def test_analyze_with_context() -> None:
    result = analyze_nicegui_code("from nicegui import ui\nui.run(reload=True)\n", context="main entrypoint")
    assert any(finding["rule_id"] == "NGL-019" for finding in result["findings"])


def test_fix_tool() -> None:
    result = fix_nicegui_code("ui.button('Save').props('width=50%')\n")
    assert ".style('width: 50%')" in result["updated_code"]


def test_generate_tool() -> None:
    result = generate_nicegui_component("layout_shell")
    assert result["kind"] == "layout_shell"
    assert "ui.scroll_area" in result["code"]


def test_list_component_kinds_tool() -> None:
    kinds = list_component_kinds()
    assert len(kinds) == 9


def test_topic_resource() -> None:
    payload = topic_index()
    assert "layout_spacing_scrolling" in payload


def test_review_tool() -> None:
    result = review_nicegui_code("ui.button('Save').props('width=50%')")
    assert "issues" in result
    assert len(result["issues"]) >= 1


def test_review_tool_auto_fix_false() -> None:
    result = review_nicegui_code("ui.button('Save').props('width=50%')", auto_fix=False)
    assert result["fixed_code"] is None


def test_preflight_resource() -> None:
    content = preflight()
    assert "review_nicegui_code" in content
    assert "min-h-0" in content
