# NiceGUI MCP Adoption-Driven Redesign — Execution Plan

## Architecture / Design

This plan implements the product redesign described in `NiceGUI-MCP-Design-Doc.md`. The core thesis: NiceGUI MCP should behave like a guided development copilot whose default action is "review what I just wrote, catch mistakes, suggest fixes, and give one meaningful improvement." Everything else supports that loop.

### Current state (v1.1)

- **Tools:** `list_topics`, `get_guidance`, `search_guidance`, `analyze_nicegui_code`, `fix_nicegui_code`, `generate_nicegui_component`
- **Resources:** `nicegui://topics/index`, `nicegui://guidance/{topic}`
- **Analyzers:** 20 rules (NGL-001 through NGL-020) across three tiers
- **Fixers:** 5 safe auto-fixers (NGL-003, NGL-004, NGL-007, NGL-009, NGL-019)
- **Generators:** 9 component kinds
- **Docs corpus:** 10 bundled markdown topics
- **Tests:** pytest green across `test_analyzers`, `test_fixers`, `test_generators`, `test_registry`, `test_server`

### Target state (v2.0)

**New flagship tools:**
- `review_nicegui_code` — composite analyze + fix + improvement in one call
- `get_pattern` — ready-to-use snippet + pitfalls for common NiceGUI tasks
- `list_component_kinds` — discovery tool for generator kinds

**New resource:**
- `nicegui-mcp://preflight` — startup-readable priming resource

**Upgraded surfaces:**
- Tool descriptions mention concrete anti-patterns and usage triggers
- Opaque parameters (`context`, `focus`, `mode`) are documented with valid values
- Server `INSTRUCTIONS` prime the review workflow

**Preserved advanced tools:**
- `analyze_nicegui_code`, `fix_nicegui_code`, `search_guidance`, `get_guidance`, `list_topics`, `generate_nicegui_component`

### Key files

| File | Role |
|---|---|
| `nicegui_mcp/models.py` | Pydantic models for all tool inputs/outputs |
| `nicegui_mcp/reviewer.py` | **New.** Composite review logic |
| `nicegui_mcp/patterns.py` | **New.** Pattern registry and retrieval |
| `nicegui_mcp/analyzers.py` | AST-based static analysis (20 rules) |
| `nicegui_mcp/fixers.py` | Deterministic safe fixers |
| `nicegui_mcp/generators.py` | Starter code generators (9 kinds) |
| `nicegui_mcp/registry.py` | Topic loading and search |
| `nicegui_mcp/profile.py` | Topics, rule metadata, focus maps |
| `nicegui_mcp/server.py` | FastMCP server, tools, resources |
| `tests/test_reviewer.py` | **New.** Tests for composite review |
| `tests/test_patterns.py` | **New.** Tests for pattern retrieval |

---

## Phased Acceptance Criteria

### Phase 1: Fix invocation and friction

| ID | Criterion |
|---|---|
| P1-1 | `review_nicegui_code` accepts a code string and optional `auto_fix` flag, returns issues + fixes + one improvement in a single call |
| P1-2 | `nicegui-mcp://preflight` resource exists and returns priming content including when to invoke, preferred tool, and common mistakes |
| P1-3 | `list_component_kinds` returns all 9 generator kinds with descriptions |
| P1-4 | `generate_nicegui_component` tool description lists valid `kind` values |
| P1-5 | All tool descriptions mention concrete anti-patterns or usage triggers |
| P1-6 | Server `INSTRUCTIONS` prime the review-first workflow |
| P1-7 | `focus` parameter documents valid values in tool description |
| P1-8 | `context` parameter documents its purpose in tool description |
| P1-9 | `mode` values are documented per-kind in `generate_nicegui_component` description |
| P1-10 | All existing tests remain green |

### Phase 2: Increase value per call

| ID | Criterion |
|---|---|
| P2-1 | `get_pattern` returns a ready-to-use snippet, explanation, pitfalls, and optional version notes for at least 8 common NiceGUI tasks |
| P2-2 | Review output includes one recommended improvement beyond correctness when findings exist |
| P2-3 | All new tools have tests covering happy path and at least one negative path |

---

## Operator Instructions

- Execute steps in order unless the plan explicitly marks steps as parallelizable.
- Respect each step's allowed-file list.
- Do not widen scope unless the step explicitly authorizes it.
- After each step, run the listed verification commands before moving on.
- If verification fails in untouched files, stop and report that failure instead of repairing it opportunistically.
- If a step fails tests, fix issues in that same thread before opening the next.
- Commit after each step to create rollback points.
- If a required MCP or tool cannot be used and the step says to stop, stop and report instead of silently skipping the requirement.

### Step-specific notes

- **Steps 1–7** are sequential.
- **No steps** require MCP servers, browser tooling, or manual operator actions.
- All steps use only `python -m pytest` for verification.

---

## Agent Execution Prompts

### Step 1: ReviewResult model and review_code function

**Todos:** P1-1, P1-10

```text
Read the implementation plan at `.windsurf/plans/adoption-redesign.md`. This is Step 1: ReviewResult model and review_code function.

No prior steps are complete. This is the first step.

Allowed files:
- `nicegui_mcp/models.py`
- `nicegui_mcp/reviewer.py` (new file)
- `tests/test_reviewer.py` (new file)

Do not modify files outside this list unless this prompt explicitly says so.
If verification fails in untouched files, stop and report that failure as out-of-scope instead of repairing it opportunistically.

Read these files first:
- `nicegui_mcp/models.py` (understand existing models: `Finding`, `AnalysisResult`, `AppliedFix`, `FixResult`)
- `nicegui_mcp/analyzers.py` (understand `analyze_code` signature and return type)
- `nicegui_mcp/fixers.py` (understand `fix_code` signature and return type)
- `nicegui_mcp/profile.py` (understand `RULE_DETAILS`, `TIER_1_RULES`, `SAFE_FIX_RULES`)

Tasks:

1. In `nicegui_mcp/models.py`, add a `ReviewIssue` model:
   - `rule_id: str`
   - `severity: Literal["error", "warning", "info"]`
   - `title: str`
   - `message: str`
   - `suggestion: str | None = None`
   - `confidence: Literal["high", "medium", "low"] = "medium"`
   - `auto_fixable: bool = False`
   - `fixed: bool = False`

2. In `nicegui_mcp/models.py`, add a `ReviewResult` model:
   - `issues: list[ReviewIssue] = Field(default_factory=list)`
   - `fixed_code: str | None = None`
   - `applied_fixes: list[AppliedFix] = Field(default_factory=list)`
   - `improvement: str | None = None`
   - `summary: str`

3. Create `nicegui_mcp/reviewer.py` with a function:
   ```python
   def review_code(code: str, auto_fix: bool = True) -> ReviewResult:
   ```
   Implementation:
   - Call `analyze_code(code)` to get findings.
   - If `auto_fix` is True, call `fix_code(code)` to get fix results.
   - Map each `Finding` to a `ReviewIssue`, setting `auto_fixable` based on whether `finding.auto_fixability == "safe"`, and `fixed` based on whether the corresponding rule_id appears in the fix result's `applied_fixes`.
   - Set `fixed_code` to the fixer's `updated_code` if `auto_fix` is True and at least one fix was applied; otherwise `None`.
   - Set `applied_fixes` from the fix result.
   - Set `improvement` to `None` for now (Step 7 will add this logic).
   - Build a `summary` string: e.g., "Found N issue(s), applied M fix(es)." or "No issues detected."
   - Import from `.analyzers`, `.fixers`, `.models`.

4. Create `tests/test_reviewer.py` with these test cases:
   - `test_review_returns_issues_for_bad_code`: pass code with `ui.button('Save').props('width=50%')`, assert at least one issue with `rule_id == "NGL-003"`.
   - `test_review_auto_fix_applies_safe_fixes`: same code, assert `fixed_code` is not None and contains `.style('width: 50%')`, assert the NGL-003 issue has `fixed=True`.
   - `test_review_no_fix_when_auto_fix_false`: same code with `auto_fix=False`, assert `fixed_code is None`, assert `applied_fixes` is empty.
   - `test_review_clean_code_returns_no_issues`: pass `ui.label('Hello')`, assert no issues and summary says no issues.
   - `test_review_multiple_issues`: pass code that triggers NGL-003 and NGL-009 (e.g., a handler with `time.sleep` plus props misuse), assert both rule_ids appear in issues.

After implementation, verify:
- `python -m pytest tests/test_reviewer.py -v` (proves the new reviewer module works correctly)
- `python -m pytest tests/ -v` (repo-wide verification; stop and report unrelated baseline failures)

After verification passes, commit:
`git add nicegui_mcp/models.py nicegui_mcp/reviewer.py tests/test_reviewer.py`
`git commit -m "feat: add ReviewResult model and review_code composite function"`
```

---

### Step 2: Wire review tool and preflight resource into server

**Todos:** P1-1, P1-2, P1-10

```text
Read the implementation plan at `.windsurf/plans/adoption-redesign.md`. This is Step 2: Wire review tool and preflight resource into server.

Step 1 is complete:
- `ReviewIssue` and `ReviewResult` models exist in `nicegui_mcp/models.py`
- `review_code()` function exists in `nicegui_mcp/reviewer.py`
- Tests pass in `tests/test_reviewer.py`

Allowed files:
- `nicegui_mcp/server.py`
- `tests/test_server.py`

Do not modify files outside this list unless this prompt explicitly says so.
If verification fails in untouched files, stop and report that failure as out-of-scope instead of repairing it opportunistically.

Read these files first:
- `nicegui_mcp/server.py` (understand existing tool/resource registration pattern)
- `nicegui_mcp/reviewer.py` (understand `review_code` signature and return type)
- `tests/test_server.py` (understand existing test patterns)

Tasks:

1. In `nicegui_mcp/server.py`, add an import:
   ```python
   from .reviewer import review_code
   ```

2. Add the `review_nicegui_code` tool. Register it as the FIRST tool (before `list_topics`) so it appears prominently:
   ```python
   @mcp.tool()
   def review_nicegui_code(code: str, auto_fix: bool = True) -> dict:
       """Review NiceGUI code for correctness issues, apply safe fixes, and suggest improvements.

       This is the recommended entry point after writing or generating NiceGUI code.
       Submit your code and receive: issues found, severity and confidence ratings,
       auto-applied fixes for safe corrections, and one recommended improvement.

       Common issues detected: missing await in async callbacks, stale closure bugs,
       incorrect binding usage, misuse of layout context managers, blocking calls in
       handlers, non-persistent destructive dialogs, and styling/props conflicts."""
       return review_code(code=code, auto_fix=auto_fix).model_dump(mode="json")
   ```

3. Add the `nicegui-mcp://preflight` resource. Place it before the existing resources:
   ```python
   @mcp.resource("nicegui-mcp://preflight")
   def preflight() -> str:
       return PREFLIGHT_CONTENT
   ```

4. Define `PREFLIGHT_CONTENT` as a module-level constant string (after `INSTRUCTIONS`). Content must include:
   - **When to invoke:** "After writing or generating NiceGUI code, before finalizing."
   - **Preferred tool:** "Use `review_nicegui_code` as the default entry point."
   - **Common NiceGUI mistakes the MCP catches:**
     1. Blocking calls (`time.sleep`, `requests.get`) in UI event handlers
     2. Missing `min-h-0` on flex parents of scroll areas
     3. CSS properties passed via `.props()` instead of `.style()`
     4. Non-persistent dialogs for destructive actions
     5. Async handlers without loading/error feedback
   - **Convention:** "Before shipping NiceGUI code, run `review_nicegui_code`."
   - Format as clean markdown.

5. In `tests/test_server.py`, add:
   - `test_review_tool`: call `review_nicegui_code("ui.button('Save').props('width=50%')")`, assert result has `"issues"` key with at least one entry.
   - `test_review_tool_auto_fix_false`: call with `auto_fix=False`, assert `result["fixed_code"]` is None.
   - `test_preflight_resource`: call `preflight()`, assert it contains `"review_nicegui_code"` and `"min-h-0"`.
   - Add imports for `review_nicegui_code` and `preflight` from `nicegui_mcp.server`.

After implementation, verify:
- `python -m pytest tests/test_server.py -v` (proves server wiring works)
- `python -m pytest tests/ -v` (repo-wide verification; stop and report unrelated baseline failures)

After verification passes, commit:
`git add nicegui_mcp/server.py tests/test_server.py`
`git commit -m "feat: wire review_nicegui_code tool and preflight resource into server"`
```

---

### Step 3: Component kind discoverability

**Todos:** P1-3, P1-4, P1-10

```text
Read the implementation plan at `.windsurf/plans/adoption-redesign.md`. This is Step 3: Component kind discoverability.

Steps 1–2 are complete:
- `review_nicegui_code` tool and `nicegui-mcp://preflight` resource are wired into the server
- All tests pass

Allowed files:
- `nicegui_mcp/generators.py`
- `nicegui_mcp/server.py`
- `tests/test_generators.py`
- `tests/test_server.py`

Do not modify files outside this list unless this prompt explicitly says so.
If verification fails in untouched files, stop and report that failure as out-of-scope instead of repairing it opportunistically.

Read these files first:
- `nicegui_mcp/generators.py` (understand the `generators` dict inside `generate_component` and each generator function)
- `nicegui_mcp/server.py` (understand how `generate_nicegui_component` is registered)
- `tests/test_generators.py` (understand existing test coverage)
- `tests/test_server.py` (understand existing test coverage)

Tasks:

1. In `nicegui_mcp/generators.py`, add a module-level `COMPONENT_KINDS` dict that maps kind name to a description string. Place it before `generate_component`:
   ```python
   COMPONENT_KINDS: dict[str, str] = {
       "layout_shell": "App shell with header, sidebar drawer, and scrollable content region.",
       "confirmation_dialog": "Persistent confirmation dialog with async result. Modes: default, destructive.",
       "async_action_flow": "Button-triggered async action with loading spinner and error feedback.",
       "controller_service_page": "Page using controller/service separation. Modes: default, refreshable.",
       "reusable_component": "Mode-driven reusable card component with summary and detail views.",
       "list_detail": "List/detail layout with sidebar navigation and scrollable detail panel.",
       "filterable_table": "Searchable, paginated data table. Modes: default, server_paginated.",
       "form_sticky_actions": "Long-form page with sticky save/cancel action bar.",
       "chart_sidebar_table": "Dashboard layout with sidebar filters, chart, and data table.",
   }
   ```

2. In `nicegui_mcp/generators.py`, add a public function:
   ```python
   def list_kinds() -> list[dict[str, str]]:
       return [{"kind": kind, "description": desc} for kind, desc in COMPONENT_KINDS.items()]
   ```

3. In `nicegui_mcp/generators.py`, update `generate_component` to use `COMPONENT_KINDS` for validation instead of the inline `generators` dict. Keep the inline `generators` dict for dispatch but validate against `COMPONENT_KINDS.keys()` and raise the same `ValueError` for unknown kinds.

4. In `nicegui_mcp/server.py`, add an import:
   ```python
   from .generators import generate_component, list_kinds
   ```
   (Replace the existing `from .generators import generate_component`.)

5. In `nicegui_mcp/server.py`, add a `list_component_kinds` tool:
   ```python
   @mcp.tool()
   def list_component_kinds() -> list[dict]:
       """List all available NiceGUI component generator kinds with descriptions.

       Use this to discover valid `kind` values for `generate_nicegui_component`.
       Each entry includes the kind name, a short description, and supported modes."""
       return list_kinds()
   ```

6. In `nicegui_mcp/server.py`, update the `generate_nicegui_component` docstring to list valid kinds:
   ```python
   """Generate deterministic NiceGUI starter code for common layout, dialog, async, and component patterns.

   Valid kinds: layout_shell, confirmation_dialog, async_action_flow, controller_service_page,
   reusable_component, list_detail, filterable_table, form_sticky_actions, chart_sidebar_table.

   Use `list_component_kinds` to discover kinds and their supported modes."""
   ```

7. In `tests/test_generators.py`, add:
   - `test_list_kinds_returns_all`: call `list_kinds()`, assert length is 9, assert each entry has "kind" and "description" keys.
   - `test_component_kinds_match_generators`: assert the set of kinds from `list_kinds()` matches the set of kinds accepted by `generate_component`.

8. In `tests/test_server.py`, add:
   - `test_list_component_kinds_tool`: call `list_component_kinds()`, assert length is 9.
   - Add the import for `list_component_kinds`.

After implementation, verify:
- `python -m pytest tests/test_generators.py tests/test_server.py -v` (touched-file verification)
- `python -m pytest tests/ -v` (repo-wide verification; stop and report unrelated baseline failures)

After verification passes, commit:
`git add nicegui_mcp/generators.py nicegui_mcp/server.py tests/test_generators.py tests/test_server.py`
`git commit -m "feat: add list_component_kinds tool and document generator kinds"`
```

---

### Step 4: Rewrite tool descriptions and server instructions

**Todos:** P1-5, P1-6, P1-10

```text
Read the implementation plan at `.windsurf/plans/adoption-redesign.md`. This is Step 4: Rewrite tool descriptions and server instructions.

Steps 1–3 are complete:
- `review_nicegui_code`, `list_component_kinds`, and `nicegui-mcp://preflight` are wired in
- All tests pass

Allowed files:
- `nicegui_mcp/server.py`

Do not modify files outside this list unless this prompt explicitly says so.
If verification fails in untouched files, stop and report that failure as out-of-scope instead of repairing it opportunistically.

Read these files first:
- `nicegui_mcp/server.py` (understand all current tool descriptions and INSTRUCTIONS)
- `nicegui_mcp/profile.py` (understand rule IDs and what each rule detects, for reference when writing descriptions)

Tasks:

1. Rewrite the `INSTRUCTIONS` constant to prime the review workflow. New content:
   ```
   NiceGUI MCP is a guided development copilot for NiceGUI applications.

   After writing or generating NiceGUI code, use `review_nicegui_code` to catch common
   mistakes and receive auto-fixes. This is the recommended default action before
   finalizing any NiceGUI code.

   The MCP catches: blocking calls in event handlers, missing min-h-0 on scroll area
   parents, CSS properties in .props() instead of .style(), non-persistent destructive
   dialogs, async handlers without feedback, logic-heavy handlers, monolithic page
   functions, and styling/props conflicts.

   Additional tools: retrieve proven implementation patterns with `get_pattern`,
   generate starter components with `generate_nicegui_component`, explore bundled
   guidance with `search_guidance` or `get_guidance`, and run targeted analysis
   with `analyze_nicegui_code`.
   ```
   (Adjust formatting for a single string constant.)

2. Rewrite the `list_topics` docstring:
   ```
   List the bundled NiceGUI guidance topics with summaries and tags.
   Topics cover layout, async patterns, styling, dialogs, state management,
   component architecture, forms, data views, testing, and deployment.
   ```

3. Rewrite the `get_guidance` docstring:
   ```
   Return the full bundled markdown guidance for a NiceGUI topic.
   Use `list_topics` to discover available topic names.
   ```

4. Rewrite the `search_guidance` docstring:
   ```
   Search bundled NiceGUI guidance docs and return heading-aware snippets sorted by relevance.
   Use for broad exploration when you are unsure which topic to read.
   For ready-to-use code patterns, prefer `get_pattern` instead.
   ```

5. Rewrite the `analyze_nicegui_code` docstring:
   ```
   Analyze NiceGUI code for known issues without applying fixes.
   Detects: layout/spacing problems, blocking calls in handlers, async handlers without
   feedback, scroll area height bugs, styling/props conflicts, non-persistent destructive
   dialogs, monolithic page functions, logic-heavy handlers, and state management smells.
   For most workflows, prefer `review_nicegui_code` which combines analysis with auto-fix.
   ```

6. Rewrite the `fix_nicegui_code` docstring:
   ```
   Apply narrow deterministic NiceGUI code fixes and return updated code plus applied fix metadata.
   Safe fixes: CSS-in-props to .style(), missing min-h-0 insertion, persistent dialog props,
   time.sleep to asyncio.sleep in async handlers, and reload=True to reload=False.
   For most workflows, prefer `review_nicegui_code` which combines analysis with auto-fix.
   ```

7. Do NOT change any function signatures, logic, or imports. Only change string constants and docstrings.

After implementation, verify:
- `python -m pytest tests/ -v` (repo-wide verification; descriptions do not affect behavior, so all tests must still pass)

After verification passes, commit:
`git add nicegui_mcp/server.py`
`git commit -m "docs: rewrite tool descriptions and server instructions for review-first workflow"`
```

---

### Step 5: Simplify and document opaque parameters

**Todos:** P1-7, P1-8, P1-9, P1-10

```text
Read the implementation plan at `.windsurf/plans/adoption-redesign.md`. This is Step 5: Simplify and document opaque parameters.

Steps 1–4 are complete:
- All new tools and resources are wired in
- Tool descriptions and instructions have been rewritten
- All tests pass

Allowed files:
- `nicegui_mcp/server.py`
- `tests/test_server.py`

Do not modify files outside this list unless this prompt explicitly says so.
If verification fails in untouched files, stop and report that failure as out-of-scope instead of repairing it opportunistically.

Read these files first:
- `nicegui_mcp/server.py` (understand current parameter signatures for `analyze_nicegui_code` and `generate_nicegui_component`)
- `nicegui_mcp/analyzers.py` (understand what `focus` and `context` do: `focus` filters rules by topic, `context` provides an entrypoint filename hint for NGL-019)
- `nicegui_mcp/generators.py` (understand what `mode` does per generator kind)
- `tests/test_server.py` (understand existing test coverage for these tools)

Tasks:

1. In `nicegui_mcp/server.py`, update the `analyze_nicegui_code` tool docstring to document `focus` and `context` parameters inline:
   ```
   Analyze NiceGUI code for known issues without applying fixes.
   Detects: layout/spacing problems, blocking calls in handlers, async handlers without
   feedback, scroll area height bugs, styling/props conflicts, non-persistent destructive
   dialogs, monolithic page functions, logic-heavy handlers, and state management smells.

   Parameters:
   - code: the NiceGUI code to analyze.
   - focus: optional list of topic names to restrict which rules run. Valid values:
     layout, spacing, scrolling, async, performance, styling, theming, dialogs,
     state, components, architecture, forms, data_views, tables, charts,
     deployment, runtime, testing. Omit to run all rules.
   - filename: optional filename hint, used to assess production-entrypoint rules.
   - context: optional description of the file's role (e.g., 'main entrypoint',
     'reusable component'). Used alongside filename for entrypoint detection.

   For most workflows, prefer `review_nicegui_code` which combines analysis with auto-fix.
   ```

2. In `nicegui_mcp/server.py`, update the `generate_nicegui_component` tool docstring to document `mode` and `details_json` per-kind:
   ```
   Generate deterministic NiceGUI starter code for common layout, dialog, async, and component patterns.

   Valid kinds: layout_shell, confirmation_dialog, async_action_flow, controller_service_page,
   reusable_component, list_detail, filterable_table, form_sticky_actions, chart_sidebar_table.

   Parameters:
   - kind: the component kind to generate (see list above).
   - mode: optional variant. Supported modes by kind:
     confirmation_dialog: 'default', 'destructive'.
     controller_service_page: 'default', 'refreshable'.
     filterable_table: 'default', 'server_paginated'.
     All other kinds: 'default' only.
   - details_json: optional JSON string with customization keys. Supported keys by kind:
     layout_shell: {"title": "App Name"}.
     confirmation_dialog: {"title": "...", "message": "...", "action_label": "..."}.
     async_action_flow: {"button_label": "..."}.
     controller_service_page: {"page_name": "..."}.
     reusable_component: {"component_name": "..."}.

   Use `list_component_kinds` to discover kinds and their descriptions.
   ```

3. Do NOT change any function signatures or logic. Only change docstrings.

4. In `tests/test_server.py`, add a test that exercises the `context` parameter:
   - `test_analyze_with_context`: call `analyze_nicegui_code("from nicegui import ui\nui.run(reload=True)\n", context="main entrypoint")`, assert any finding has `rule_id == "NGL-019"`.

After implementation, verify:
- `python -m pytest tests/test_server.py -v` (touched-file verification)
- `python -m pytest tests/ -v` (repo-wide verification; stop and report unrelated baseline failures)

After verification passes, commit:
`git add nicegui_mcp/server.py tests/test_server.py`
`git commit -m "docs: document focus, context, mode, and details_json parameters inline"`
```

---

### Step 6: Pattern retrieval tool

**Todos:** P2-1, P2-3

```text
Read the implementation plan at `.windsurf/plans/adoption-redesign.md`. This is Step 6: Pattern retrieval tool.

Steps 1–5 are complete:
- All Phase 1 tools, resources, descriptions, and parameter docs are in place
- All tests pass

Allowed files:
- `nicegui_mcp/models.py`
- `nicegui_mcp/patterns.py` (new file)
- `nicegui_mcp/server.py`
- `tests/test_patterns.py` (new file)
- `tests/test_server.py`

Do not modify files outside this list unless this prompt explicitly says so.
If verification fails in untouched files, stop and report that failure as out-of-scope instead of repairing it opportunistically.

Read these files first:
- `nicegui_mcp/models.py` (understand existing model patterns)
- `nicegui_mcp/generators.py` (reference for code snippet formatting and the `COMPONENT_KINDS` registry pattern)
- `nicegui_mcp/server.py` (understand tool registration pattern)
- `tests/test_server.py` (understand test patterns)

Tasks:

1. In `nicegui_mcp/models.py`, add:
   ```python
   class PatternResult(BaseModel):
       pattern_name: str
       title: str
       snippet: str
       explanation: str
       pitfalls: list[str] = Field(default_factory=list)
       version_notes: str | None = None
   ```

2. Create `nicegui_mcp/patterns.py` with a `PATTERNS` registry dict and a `get_pattern_by_name` function:
   ```python
   def get_pattern_by_name(name: str) -> PatternResult:
   ```
   Also add:
   ```python
   def list_pattern_names() -> list[dict[str, str]]:
       return [{"name": name, "title": pattern.title} for name, pattern in PATTERNS.items()]
   ```

3. Populate `PATTERNS` with at least these 8 entries. Each entry is a `PatternResult`. Use `textwrap.dedent` for snippets. The patterns:

   a. `async_ui_update` — "Async UI Updates"
      - Snippet: async handler that disables button, shows spinner, awaits work, re-enables
      - Pitfalls: forgetting to disable trigger, missing error feedback, not re-enabling on failure
      - Explanation: NiceGUI async handlers should disable the trigger, show progress, and always re-enable in a finally block.

   b. `dialog_open_close` — "Dialog Open/Close Flow"
      - Snippet: reusable dialog class with async `ask()` method returning bool
      - Pitfalls: not using `persistent` for destructive confirms, creating new dialog instances per call, forgetting to resolve the future on cancel
      - Explanation: Create one dialog instance and reuse it. Use asyncio.Future for awaitable results.

   c. `timer_driven_refresh` — "Timer-Driven Refresh"
      - Snippet: `ui.timer` refreshing a `@ui.refreshable` section
      - Pitfalls: timer interval too short causing UI thrash, not gating refresh behind active-tab check, timer not stopped on page teardown
      - Explanation: Use ui.timer for periodic updates. Pair with @ui.refreshable for clean re-rendering.

   d. `table_crud` — "Table CRUD Pattern"
      - Snippet: table with add/edit/delete using dialog and controller
      - Pitfalls: mutating rows list in place without calling table.update(), large inline row sets, missing optimistic UI feedback
      - Explanation: Keep rows in a controller. Call table.update() after mutations.

   e. `value_binding` — "Value Binding"
      - Snippet: input bound to label via `bind_value_to`/`bind_text_from`
      - Pitfalls: binding to a property that does not exist, circular bindings, using lambda backward functions that raise on None
      - Explanation: Use bind_value_to for two-way and bind_text_from for one-way display.

   f. `background_task` — "Background Task Coordination"
      - Snippet: `background_tasks.create()` with notification on completion
      - Pitfalls: fire-and-forget without logging, no error handling in the background coroutine, assuming UI context is available inside the task
      - Explanation: Always handle exceptions inside background tasks. Use ui.notify only from the originating client context.

   g. `navigation_pages` — "Multi-Page Navigation"
      - Snippet: multiple `@ui.page` routes with shared layout shell
      - Pitfalls: duplicating header/drawer across pages, using ui.navigate.to inside async without await, not using ui.page decorator
      - Explanation: Share layout via a common function or component called at the top of each page handler.

   h. `scroll_area_setup` — "Scroll Area Setup"
      - Snippet: column with min-h-0 containing scroll_area with h-full
      - Pitfalls: missing min-h-0 on flex parent, no constrained height ancestor, nesting scroll areas accidentally
      - Explanation: Scroll areas need a height-constrained ancestor. Add min-h-0 to the flex parent.

4. In `nicegui_mcp/server.py`, add imports and wire the tool:
   ```python
   from .patterns import get_pattern_by_name, list_pattern_names
   ```

   ```python
   @mcp.tool()
   def get_pattern(pattern_name: str) -> dict:
       """Retrieve a ready-to-use NiceGUI implementation pattern with code snippet, explanation, and pitfalls.

       Available patterns: async_ui_update, dialog_open_close, timer_driven_refresh,
       table_crud, value_binding, background_task, navigation_pages, scroll_area_setup.

       Returns a complete snippet you can adapt directly, plus common pitfalls to avoid."""
       return get_pattern_by_name(pattern_name).model_dump(mode="json")
   ```

5. Create `tests/test_patterns.py` with:
   - `test_all_patterns_return_valid_results`: iterate all pattern names from `list_pattern_names()`, call `get_pattern_by_name(name)`, assert each has non-empty `snippet`, `explanation`, and `pitfalls`.
   - `test_all_pattern_snippets_are_valid_python`: for each pattern, `ast.parse(result.snippet)` must not raise.
   - `test_unknown_pattern_raises`: call `get_pattern_by_name("nonexistent")`, assert `ValueError` is raised.
   - `test_list_pattern_names_returns_all`: assert `list_pattern_names()` returns 8 entries.

6. In `tests/test_server.py`, add:
   - `test_get_pattern_tool`: call the server-level `get_pattern("async_ui_update")`, assert result has `"snippet"` key.
   - Add the import for `get_pattern`.

After implementation, verify:
- `python -m pytest tests/test_patterns.py tests/test_server.py -v` (touched-file verification)
- `python -m pytest tests/ -v` (repo-wide verification; stop and report unrelated baseline failures)

After verification passes, commit:
`git add nicegui_mcp/models.py nicegui_mcp/patterns.py nicegui_mcp/server.py tests/test_patterns.py tests/test_server.py`
`git commit -m "feat: add get_pattern tool with 8 ready-to-use NiceGUI patterns"`
```

---

### Step 7: Enrich review output with improvement suggestion

**Todos:** P2-2, P2-3

```text
Read the implementation plan at `.windsurf/plans/adoption-redesign.md`. This is Step 7: Enrich review output with improvement suggestion.

Steps 1–6 are complete:
- All tools (`review_nicegui_code`, `get_pattern`, `list_component_kinds`) are wired in
- All resources (`preflight`) are in place
- All descriptions are rewritten
- All tests pass

Allowed files:
- `nicegui_mcp/reviewer.py`
- `tests/test_reviewer.py`

Do not modify files outside this list unless this prompt explicitly says so.
If verification fails in untouched files, stop and report that failure as out-of-scope instead of repairing it opportunistically.

Read these files first:
- `nicegui_mcp/reviewer.py` (understand current `review_code` logic and where `improvement` is set to None)
- `nicegui_mcp/profile.py` (understand `RULE_DETAILS` keys and the rule tier structure)
- `nicegui_mcp/analyzers.py` (understand what each rule detects, to write relevant improvement suggestions)
- `tests/test_reviewer.py` (understand existing test coverage)

Tasks:

1. In `nicegui_mcp/reviewer.py`, add a private function:
   ```python
   def _pick_improvement(findings: list[Finding], code: str) -> str | None:
   ```
   This function selects one high-value improvement suggestion based on the findings and code.

   Logic (evaluate in order, return the first match):

   a. If any finding has `rule_id == "NGL-008"` (logic-heavy handler):
      Return: "Consider extracting business logic from your event handlers into a controller or service layer. This makes handlers thin, testable, and easier to maintain. See the `controller_service_page` generator or the `background_task` pattern."

   b. If any finding has `rule_id == "NGL-018"` (monolithic page function):
      Return: "This page function is large enough to benefit from decomposition. Extract repeated UI sections into reusable component functions and keep the page handler focused on layout composition. See the `reusable_component` generator."

   c. If any finding has `rule_id == "NGL-014"` (many booleans) or `rule_id == "NGL-015"` (string enum candidate):
      Return: "Multiple boolean flags or string comparisons suggest implicit state modes. Replace them with an explicit enum or state variable. This eliminates impossible state combinations and makes UI branching clearer."

   d. If any finding has `rule_id == "NGL-010"` (async without feedback):
      Return: "Your async handlers would benefit from explicit loading, success, and error states. Disable the trigger before awaiting, show a spinner, and always surface the outcome. See the `async_ui_update` pattern."

   e. If any finding has `rule_id == "NGL-011"` (repeated components):
      Return: "Repeated card-style blocks are good candidates for a reusable component function. Extract the shared structure and parameterize the differences. See the `reusable_component` generator."

   f. If any finding has `rule_id in ("NGL-001", "NGL-002", "NGL-004", "NGL-005", "NGL-006")` (layout issues):
      Return: "Your layout would benefit from explicit height constraints and gap management. NiceGUI flex layouts work best with min-h-0 on scroll parents, constrained heights, and intentional gap classes. See the `scroll_area_setup` pattern."

   g. If no findings match any of the above, return None.

2. In `nicegui_mcp/reviewer.py`, update `review_code` to call `_pick_improvement(findings, code)` and assign the result to the `improvement` field of `ReviewResult`. Pass the original `analyze_code` findings (the `Finding` objects, not the mapped `ReviewIssue` objects) to `_pick_improvement`.

3. In `tests/test_reviewer.py`, add:

   - `test_review_suggests_controller_improvement`: pass code with a logic-heavy handler (12+ statements, multiple branches, external calls — reuse a pattern similar to the NGL-008 invalid fixture), assert `result.improvement` is not None and contains "controller" or "service".

   - `test_review_suggests_async_feedback_improvement`: pass code with an async handler that awaits without feedback (e.g., `async def on_click():\n    await slow_call()\n` registered as `ui.button('Go', on_click=on_click)`), assert `result.improvement` is not None and contains "loading" or "feedback" or "spinner".

   - `test_review_no_improvement_for_clean_code`: pass `ui.label('Hello')`, assert `result.improvement is None`.

   - `test_review_improvement_is_first_match_only`: pass code that triggers both NGL-008 and NGL-010, assert `result.improvement` mentions "controller" (NGL-008 takes priority).

After implementation, verify:
- `python -m pytest tests/test_reviewer.py -v` (touched-file verification)
- `python -m pytest tests/ -v` (repo-wide verification; stop and report unrelated baseline failures)

After verification passes, commit:
`git add nicegui_mcp/reviewer.py tests/test_reviewer.py`
`git commit -m "feat: add improvement suggestion to review_nicegui_code output"`
```

---

## Phase 3 Outline (Future Work)

Phase 3 covers broader product hardening. These steps are not prompted here because they depend on real usage feedback from the Phase 1+2 changes. When ready, create a separate plan file.

| Area | Work |
|---|---|
| Packaging | PyPI publishing, install verification, `pip install nicegui-mcp` flow |
| CLI | `--help`, `--version`, `--test`, `--health-check` flags |
| Configuration | Default config templates, config validation |
| Error handling | Standardized error messages across all tools |
| Testing | Coverage expansion, property-based tests for analyzers, integration tests |
| Security | Input sanitization, dependency auditing |
| Maintenance | Dependabot, CI/CD pipeline, changelog automation |
| Community | CONTRIBUTING.md, issue templates, PR templates |
