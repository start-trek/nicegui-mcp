from __future__ import annotations

from .analyzers import analyze_code
from .fixers import fix_code
from .models import AppliedFix, Finding, ReviewIssue, ReviewResult


def review_code(code: str, auto_fix: bool = True) -> ReviewResult:
    """Review NiceGUI code for issues and optionally apply safe fixes."""
    # Get analysis findings
    analysis = analyze_code(code)
    
    # Apply fixes if requested
    fix_result = None
    if auto_fix:
        fix_result = fix_code(code)
    
    # Map findings to review issues
    issues = []
    applied_fix_rule_ids = {fix.rule_id for fix in fix_result.applied_fixes} if fix_result else set()
    
    for finding in analysis.findings:
        issue = ReviewIssue(
            rule_id=finding.rule_id,
            severity=finding.severity,
            title=finding.title,
            message=finding.message,
            suggestion=finding.suggestion,
            confidence=finding.confidence,
            auto_fixable=(finding.auto_fixability == "safe"),
            fixed=(finding.rule_id in applied_fix_rule_ids),
        )
        issues.append(issue)
    
    # Set fixed code if fixes were applied
    fixed_code = None
    applied_fixes = []
    if fix_result and fix_result.applied_fixes:
        fixed_code = fix_result.updated_code
        applied_fixes = fix_result.applied_fixes
    
    # Build summary
    if not issues:
        summary = "No issues detected."
    else:
        fix_count = len([fix for fix in applied_fixes])
        issue_count = len(issues)
        if fix_count > 0:
            summary = f"Found {issue_count} issue(s), applied {fix_count} fix(es)."
        else:
            summary = f"Found {issue_count} issue(s)."
    
    return ReviewResult(
        issues=issues,
        fixed_code=fixed_code,
        applied_fixes=applied_fixes,
        improvement=None,  # Step 7 will add this logic
        summary=summary,
    )
