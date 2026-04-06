from __future__ import annotations

import ast

from nicegui_mcp.patterns import get_pattern_by_name, list_pattern_names


def test_all_patterns_return_valid_results() -> None:
    pattern_names = list_pattern_names()
    for pattern_entry in pattern_names:
        name = pattern_entry["name"]
        result = get_pattern_by_name(name)
        assert result.snippet, f"Pattern {name} should have non-empty snippet"
        assert result.explanation, f"Pattern {name} should have non-empty explanation"
        assert result.pitfalls, f"Pattern {name} should have non-empty pitfalls list"


def test_all_pattern_snippets_are_valid_python() -> None:
    pattern_names = list_pattern_names()
    for pattern_entry in pattern_names:
        name = pattern_entry["name"]
        result = get_pattern_by_name(name)
        try:
            ast.parse(result.snippet)
        except SyntaxError as exc:
            raise AssertionError(f"Pattern {name} has invalid Python syntax: {exc}")


def test_unknown_pattern_raises() -> None:
    try:
        get_pattern_by_name("nonexistent")
        assert False, "Expected ValueError for unknown pattern"
    except ValueError:
        pass  # Expected


def test_list_pattern_names_returns_all() -> None:
    pattern_names = list_pattern_names()
    assert len(pattern_names) == 8
    assert all(entry["name"] and entry["title"] for entry in pattern_names)
