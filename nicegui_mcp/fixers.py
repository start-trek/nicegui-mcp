from __future__ import annotations

import ast
import re

from .analyzers import analyze_code
from .models import AppliedFix, FixResult

STYLE_PROP_RE = re.compile(r"^(?P<key>(?:min|max)-?(?:width|height)|width|height|margin|padding|gap)=(?P<value>.+)$")
PROPS_CALL_RE = re.compile(r"\.props\((['\"])(?P<content>.*?)\1\)")


def fix_code(code: str, aggressive: bool = False) -> FixResult:
    analysis = analyze_code(code)
    updated_code = code
    applied_fixes: list[AppliedFix] = []
    notes: list[str] = []

    for line_no in _lines_for_rule(analysis.findings, "NGL-003"):
        new_code = _fix_css_props_on_line(updated_code, line_no)
        if new_code != updated_code:
            updated_code = new_code
            applied_fixes.append(AppliedFix(rule_id="NGL-003", description=f"Moved CSS-like props into `.style(...)` on line {line_no}."))

    for line_no in _lines_for_rule(analysis.findings, "NGL-004"):
        new_code = _fix_min_height_on_line(updated_code, line_no)
        if new_code != updated_code:
            updated_code = new_code
            applied_fixes.append(AppliedFix(rule_id="NGL-004", description=f"Added `min-h-0` support on line {line_no}."))

    for line_no in _lines_for_rule(analysis.findings, "NGL-007"):
        new_code = _fix_persistent_dialog_on_line(updated_code, line_no)
        if new_code != updated_code:
            updated_code = new_code
            applied_fixes.append(AppliedFix(rule_id="NGL-007", description=f"Added `persistent` dialog props on line {line_no}."))

    rewritten_sleep = _rewrite_async_time_sleep(updated_code, _lines_for_rule(analysis.findings, "NGL-009"))
    if rewritten_sleep != updated_code:
        updated_code = rewritten_sleep
        applied_fixes.append(AppliedFix(rule_id="NGL-009", description="Replaced `time.sleep(...)` with `await asyncio.sleep(...)` in async handlers."))
    elif _lines_for_rule(analysis.findings, "NGL-009"):
        notes.append("Blocking handler findings remain guidance-only where the code was not inside an `async def` body.")

    for line_no in _lines_for_rule(analysis.findings, "NGL-019"):
        new_code = _replace_line(updated_code, line_no, lambda line: line.replace("reload=True", "reload=False"))
        if new_code != updated_code:
            updated_code = new_code
            applied_fixes.append(AppliedFix(rule_id="NGL-019", description=f"Rewrote `reload=True` to `reload=False` on line {line_no}."))

    if aggressive:
        notes.append("`aggressive=True` currently enables the same safe deterministic fixer set as the default mode.")

    remaining = analyze_code(updated_code)
    return FixResult(
        updated_code=updated_code,
        applied_fixes=applied_fixes,
        notes=notes,
        recommend_reanalysis=bool(applied_fixes) or bool(remaining.findings),
    )


def _lines_for_rule(findings, rule_id: str) -> list[int]:
    line_numbers: list[int] = []
    for finding in findings:
        if finding.rule_id != rule_id or not finding.span_hint:
            continue
        match = re.search(r"line (\d+)", finding.span_hint)
        if match:
            line_number = int(match.group(1))
            if line_number not in line_numbers:
                line_numbers.append(line_number)
    return line_numbers


def _fix_css_props_on_line(code: str, line_no: int) -> str:
    def rewrite(line: str) -> str:
        def replace(match: re.Match[str]) -> str:
            content = match.group("content")
            quote = match.group(1)
            props_tokens: list[str] = []
            style_tokens: list[tuple[str, str]] = []
            for token in content.split():
                style_match = STYLE_PROP_RE.match(token)
                if style_match:
                    style_tokens.append((style_match.group("key"), style_match.group("value")))
                else:
                    props_tokens.append(token)
            if not style_tokens:
                return match.group(0)
            style_text = "; ".join(f"{key}: {value}" for key, value in style_tokens)
            props_fragment = f".props({quote}{' '.join(props_tokens)}{quote})" if props_tokens else ""
            return f"{props_fragment}.style({quote}{style_text}{quote})"

        return PROPS_CALL_RE.sub(replace, line)

    return _replace_line(code, line_no, rewrite)


def _fix_min_height_on_line(code: str, line_no: int) -> str:
    def rewrite(line: str) -> str:
        if "min-h-0" in line:
            return line
        if ".classes(" in line:
            return re.sub(r"\.classes\((['\"])(?P<content>.*?)\1\)", lambda match: f".classes({match.group(1)}{match.group('content')} min-h-0{match.group(1)})", line, count=1)
        if ":" in line:
            return line.replace(":", ".classes('min-h-0'):", 1)
        return f"{line}.classes('min-h-0')"

    return _replace_line(code, line_no, rewrite)


def _fix_persistent_dialog_on_line(code: str, line_no: int) -> str:
    def rewrite(line: str) -> str:
        if "persistent" in line:
            return line
        if ".props(" in line:
            return re.sub(r"\.props\((['\"])(?P<content>.*?)\1\)", lambda match: f".props({match.group(1)}{match.group('content')} persistent{match.group(1)})", line, count=1)
        if ":" in line:
            return line.replace(":", ".props('persistent'):", 1)
        return f"{line}.props('persistent')"

    return _replace_line(code, line_no, rewrite)


def _rewrite_async_time_sleep(code: str, lines_to_fix: list[int]) -> str:
    if not lines_to_fix:
        return code
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code
    async_line_numbers: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute) and isinstance(child.func.value, ast.Name):
                if child.func.value.id == "time" and child.func.attr == "sleep" and child.lineno in lines_to_fix:
                    async_line_numbers.add(child.lineno)

    updated = code
    for line_no in sorted(async_line_numbers):
        updated = _replace_line(updated, line_no, lambda line: line.replace("time.sleep(", "await asyncio.sleep("))
    if async_line_numbers and "import asyncio" not in updated:
        updated = f"import asyncio\n{updated}"
    return updated


def _replace_line(code: str, line_no: int, transform) -> str:
    lines = code.splitlines()
    index = line_no - 1
    if index < 0 or index >= len(lines):
        return code
    new_line = transform(lines[index])
    if new_line == lines[index]:
        return code
    lines[index] = new_line
    return "\n".join(lines) + ("\n" if code.endswith("\n") else "")
