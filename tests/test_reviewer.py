import pytest

from nicegui_mcp.reviewer import review_code


def test_review_returns_issues_for_bad_code():
    """Test that code with props misuse returns NGL-003 issue."""
    code = "ui.button('Save').props('width=50%')"
    result = review_code(code)
    
    assert len(result.issues) > 0
    ngl_003_issues = [issue for issue in result.issues if issue.rule_id == "NGL-003"]
    assert len(ngl_003_issues) == 1
    assert ngl_003_issues[0].title == "Inline styles vs Tailwind misuse"


def test_review_auto_fix_applies_safe_fixes():
    """Test that auto_fix=True applies safe fixes and updates code."""
    code = "ui.button('Save').props('width=50%')"
    result = review_code(code, auto_fix=True)
    
    assert result.fixed_code is not None
    assert ".style('width: 50%')" in result.fixed_code
    
    ngl_003_issues = [issue for issue in result.issues if issue.rule_id == "NGL-003"]
    assert len(ngl_003_issues) == 1
    assert ngl_003_issues[0].fixed is True


def test_review_no_fix_when_auto_fix_false():
    """Test that auto_fix=False doesn't apply fixes."""
    code = "ui.button('Save').props('width=50%')"
    result = review_code(code, auto_fix=False)
    
    assert result.fixed_code is None
    assert len(result.applied_fixes) == 0
    
    ngl_003_issues = [issue for issue in result.issues if issue.rule_id == "NGL-003"]
    assert len(ngl_003_issues) == 1
    assert ngl_003_issues[0].fixed is False


def test_review_clean_code_returns_no_issues():
    """Test that clean code returns no issues."""
    code = "ui.label('Hello')"
    result = review_code(code)
    
    assert len(result.issues) == 0
    assert "No issues detected" in result.summary


def test_review_multiple_issues():
    """Test that code with multiple issues returns both rule IDs."""
    code = """
async def on_click():
    time.sleep(1)  # NGL-009
    ui.button('Save').props('width=50%')  # NGL-003
"""
    result = review_code(code)
    
    rule_ids = [issue.rule_id for issue in result.issues]
    assert "NGL-003" in rule_ids
    assert "NGL-009" in rule_ids
