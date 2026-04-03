from __future__ import annotations

import pytest

from nicegui_mcp.registry import available_topics, get_topic, load_guidance_text, search_guidance_text


def test_all_topics_load() -> None:
    topics = available_topics()
    assert len(topics) == 10
    assert all(topic.summary for topic in topics)
    assert all(topic.tags for topic in topics)


def test_topic_normalization() -> None:
    assert get_topic("Layout Spacing Scrolling").name == "layout_spacing_scrolling"
    assert get_topic("styling-theming").name == "styling_theming"


def test_guidance_text_loads() -> None:
    text = load_guidance_text("dialogs")
    assert "persistent" in text


def test_unknown_topic_raises() -> None:
    with pytest.raises(ValueError, match="Unknown topic"):
        load_guidance_text("unknown-topic")


def test_search_returns_heading_aware_hits() -> None:
    hits = search_guidance_text("persistent dialog")
    assert hits
    assert any(hit.topic == "dialogs" for hit in hits)
    assert any(hit.heading for hit in hits)


def test_search_topic_filter() -> None:
    hits = search_guidance_text("spinner", topics=["async_tasks_performance"])
    assert hits
    assert all(hit.topic == "async_tasks_performance" for hit in hits)
