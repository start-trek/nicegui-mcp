from __future__ import annotations

import ast
import re
from collections import Counter, defaultdict
from dataclasses import dataclass

from .models import AnalysisResult, Finding
from .profile import RULE_DETAILS, requested_rule_ids

STYLE_PROP_RE = re.compile(r"^(?P<key>(?:min|max)-?(?:width|height)|width|height|margin|padding|gap)=(?P<value>.+)$")
DESTRUCTIVE_WORDS = ("delete", "remove", "destroy", "destructive", "permanently", "danger")
FEEDBACK_TOKENS = ("notify", "loading", "spinner", "progress", "disable", "disabled", "busy")
COLOR_CLASS_PREFIXES = ("text-", "bg-", "border-")
BLOCKING_CALLS = {
    "time.sleep",
    "requests.get",
    "requests.post",
    "requests.put",
    "requests.delete",
    "subprocess.run",
}
UI_DATA_COMPONENTS = {"table", "aggrid", "echart", "highchart"}
UI_LAYOUT_COMPONENTS = {"row", "column"}


@dataclass
class UIChain:
    node: ast.Call
    root: str
    source: str
    classes: list[str]
    styles: list[str]
    props: list[str]
    keywords: dict[str, ast.AST]


@dataclass
class ContainerContext:
    node: ast.With | ast.AsyncWith
    chain: UIChain
    body_source: str


class _FindingCollector:
    def __init__(self) -> None:
        self._items: list[tuple[int, str, Finding]] = []

    def add(
        self,
        rule_id: str,
        node: ast.AST | None,
        message: str,
        suggestion: str | None = None,
        severity: str | None = None,
        confidence: str | None = None,
        auto_fixability: str | None = None,
    ) -> None:
        defaults = RULE_DETAILS.get(rule_id, {})
        line = getattr(node, "lineno", 1) if node is not None else 1
        self._items.append(
            (
                line,
                rule_id,
                Finding(
                    rule_id=rule_id,
                    severity=severity or defaults.get("severity", "warning"),
                    title=defaults.get("title", rule_id),
                    message=message,
                    suggestion=suggestion,
                    span_hint=f"line {line}" if node is not None else None,
                    confidence=confidence or defaults.get("confidence", "medium"),
                    auto_fixability=auto_fixability or defaults.get("auto_fixability", "guidance_only"),
                ),
            )
        )

    def sorted_findings(self) -> list[Finding]:
        return [finding for _, _, finding in sorted(self._items, key=lambda item: (item[0], item[1], item[2].message))]


class _ContextVisitor(ast.NodeVisitor):
    def __init__(self, code: str, collector: _FindingCollector, requested_rules: set[str]) -> None:
        self.code = code
        self.lines = code.splitlines()
        self.collector = collector
        self.requested_rules = requested_rules
        self.stack: list[ContainerContext] = []

    def visit_With(self, node: ast.With) -> None:
        self._visit_context_block(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        self._visit_context_block(node)

    def visit_Call(self, node: ast.Call) -> None:
        if _is_outermost_ui_call(node):
            chain = _describe_ui_chain(node, self.code)
            if chain is not None:
                self._inspect_call_chain(chain)
        self.generic_visit(node)

    def _visit_context_block(self, node: ast.With | ast.AsyncWith) -> None:
        chain = _describe_ui_chain(node.items[0].context_expr, self.code) if node.items else None
        pushed = False
        if chain is not None:
            body_source = _source_for_node(self.code, node)
            context = ContainerContext(node=node, chain=chain, body_source=body_source)
            self._inspect_container(context)
            self.stack.append(context)
            pushed = True
        for statement in node.body:
            self.visit(statement)
        if pushed:
            self.stack.pop()

    def _inspect_container(self, context: ContainerContext) -> None:
        chain = context.chain
        body_source = context.body_source.casefold()
        if chain.root in UI_LAYOUT_COMPONENTS:
            if "NGL-001" in self.requested_rules:
                gap_levels = [
                    int(token.split("-", 1)[1])
                    for token in chain.classes
                    if token.startswith("gap-") and token.split("-", 1)[1].isdigit()
                ]
                if gap_levels and max(gap_levels) >= 6:
                    self.collector.add(
                        "NGL-001",
                        context.node,
                        "This container uses a large explicit gap. NiceGUI layout defaults already add spacing, so large Tailwind gap classes often over-space real UIs.",
                        "Prefer a smaller explicit gap or set a single container-level gap strategy.",
                    )
                elif not gap_levels and not _styles_contain_gap(chain.styles):
                    direct_children = sum(1 for stmt in context.node.body if isinstance(stmt, (ast.Expr, ast.With, ast.AsyncWith)))
                    if direct_children >= 4:
                        self.collector.add(
                            "NGL-001",
                            context.node,
                            "This container relies on default spacing across many children. Explicit gap control makes NiceGUI layouts more predictable.",
                            "Consider `.style('gap: 0.5rem')` or a small `gap-*` class on the container.",
                            confidence="medium",
                        )
            if "NGL-002" in self.requested_rules and chain.root == "row":
                percentage_widths = re.findall(r"width:\s*(\d+)%", context.body_source)
                half_width_classes = re.findall(r"\bw-1/2\b", context.body_source)
                total = sum(int(width) for width in percentage_widths) + (50 * len(half_width_classes))
                if total >= 100 and ("gap-" in context.body_source or "width:" in context.body_source or len(half_width_classes) >= 2):
                    self.collector.add(
                        "NGL-002",
                        context.node,
                        "This row likely overflows once gap spacing is included. Percentage widths plus NiceGUI row spacing often trigger wrapping.",
                        "Reduce the child widths or add a no-wrap strategy after checking the available width budget.",
                    )
            if "NGL-006" in self.requested_rules and chain.root == "row":
                if any(component in context.body_source for component in ("ui.table", "ui.aggrid", "ui.echart")) and "min-w-0" not in context.body_source:
                    self.collector.add(
                        "NGL-006",
                        context.node,
                        "This horizontal layout contains a likely wide data or chart component without an explicit `min-w-0` escape hatch.",
                        "If the main content clips or overflows, add `min-w-0` to the flex child that should shrink.",
                    )
        if "NGL-007" in self.requested_rules and chain.root == "dialog":
            props_text = " ".join(chain.props)
            if "persistent" not in props_text and any(word in body_source for word in DESTRUCTIVE_WORDS):
                self.collector.add(
                    "NGL-007",
                    context.node,
                    "This dialog appears to confirm a destructive action but is not marked persistent.",
                    "Add `.props('persistent')` so users do not dismiss destructive dialogs accidentally.",
                )

    def _inspect_call_chain(self, chain: UIChain) -> None:
        if "NGL-003" in self.requested_rules:
            style_like_props = [token for token in chain.props if STYLE_PROP_RE.match(token)]
            invalid_utilities = [token for token in chain.classes if token in {"w-50", "h-50", "min-w-50", "max-w-50"}]
            if style_like_props or invalid_utilities:
                detail_parts = []
                if style_like_props:
                    detail_parts.append(f"style-like props: {', '.join(style_like_props)}")
                if invalid_utilities:
                    detail_parts.append(f"questionable utility classes: {', '.join(invalid_utilities)}")
                self.collector.add(
                    "NGL-003",
                    chain.node,
                    f"This element mixes styling concerns in places NiceGUI does not handle well ({'; '.join(detail_parts)}).",
                    "Move raw CSS to `.style(...)` and keep `.props(...)` for Quasar props only.",
                )
        if "NGL-013" in self.requested_rules:
            has_color_prop = "color" in chain.keywords or any(token.startswith("color=") for token in chain.props)
            has_color_classes = any(token.startswith(COLOR_CLASS_PREFIXES) for token in chain.classes)
            if has_color_prop and has_color_classes:
                self.collector.add(
                    "NGL-013",
                    chain.node,
                    "This element mixes Quasar color props with Tailwind color classes, which often leads to confusing styling precedence.",
                    "Pick one color system for the element or keep Tailwind limited to layout-only classes.",
                )
        if chain.root == "scroll_area":
            has_full_height = "h-full" in chain.classes or _styles_contain_height(chain.styles)
            if has_full_height:
                nearest_layout = next((context for context in reversed(self.stack) if context.chain.root in UI_LAYOUT_COMPONENTS), None)
                if "NGL-004" in self.requested_rules and nearest_layout and not _has_min_height_zero(nearest_layout.chain):
                    self.collector.add(
                        "NGL-004",
                        nearest_layout.node,
                        "A scroll area sits inside a flex layout without `min-h-0`, which is a common cause of broken scrolling in NiceGUI.",
                        "Add `min-h-0` to the flex child that owns the scroll area.",
                    )
                if "NGL-005" in self.requested_rules and not any(_has_constrained_height(context.chain) for context in self.stack):
                    self.collector.add(
                        "NGL-005",
                        chain.node,
                        "This scroll area uses full height without any visible constrained parent height in the snippet.",
                        "Wrap it in a layout shell or parent container with explicit height, `h-full`, or `h-screen` semantics.",
                    )


def analyze_code(
    code: str,
    focus: list[str] | None = None,
    filename: str | None = None,
    context: str | None = None,
) -> AnalysisResult:
    normalized_focus, requested_rules = requested_rule_ids(focus)
    collector = _FindingCollector()
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        collector.add(
            "NGL-000",
            None,
            f"Python syntax error: {exc.msg}.",
            "Fix the syntax error before running NiceGUI analysis.",
            severity="error",
            confidence="high",
        )
        findings = collector.sorted_findings()
        return AnalysisResult(findings=findings, summary=_build_summary(findings), focus_applied=normalized_focus)

    _attach_parents(tree)
    assignments = _collect_assignments(tree)
    callback_names, lambda_handlers = _collect_callback_targets(tree)
    collector = _run_ast_detectors(
        tree=tree,
        code=code,
        filename=filename,
        context=context,
        assignments=assignments,
        callback_names=callback_names,
        lambda_handlers=lambda_handlers,
        requested_rules=requested_rules,
        collector=collector,
    )
    findings = collector.sorted_findings()
    return AnalysisResult(findings=findings, summary=_build_summary(findings), focus_applied=normalized_focus)


def _run_ast_detectors(
    tree: ast.Module,
    code: str,
    filename: str | None,
    context: str | None,
    assignments: dict[str, list[ast.AST]],
    callback_names: set[str],
    lambda_handlers: list[ast.Lambda],
    requested_rules: set[str],
    collector: _FindingCollector,
) -> _FindingCollector:
    visitor = _ContextVisitor(code=code, collector=collector, requested_rules=requested_rules)
    visitor.visit(tree)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _inspect_handler(node, callback_names, requested_rules, collector, assignments)
            _inspect_page_function(node, requested_rules, collector, code, filename)
            _inspect_boolean_state(node, requested_rules, collector)
            _inspect_enum_candidates(node, requested_rules, collector)
            _inspect_repeated_components(node, requested_rules, collector, code)
            _inspect_inconsistent_display(node, requested_rules, collector)
        elif isinstance(node, ast.Module):
            _inspect_boolean_state(node, requested_rules, collector)
            _inspect_enum_candidates(node, requested_rules, collector)
            _inspect_repeated_components(node, requested_rules, collector, code)
            _inspect_inconsistent_display(node, requested_rules, collector)
        elif isinstance(node, ast.Call):
            _inspect_large_tables(node, requested_rules, collector, assignments)

    for lambda_node in lambda_handlers:
        if "NGL-009" in requested_rules and any(_call_name(call) in BLOCKING_CALLS for call in ast.walk(lambda_node) if isinstance(call, ast.Call)):
            collector.add(
                "NGL-009",
                lambda_node,
                "A UI event lambda performs blocking synchronous work.",
                "Move the work into an async or background helper instead of blocking inline.",
            )

    if "NGL-019" in requested_rules:
        entrypoint_hint = (filename or context or "").casefold()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _call_name(node) == "ui.run":
                for keyword in node.keywords:
                    if keyword.arg == "reload" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                        severity = "warning" if any(token in entrypoint_hint for token in ("main", "app", "server", "prod")) or not entrypoint_hint else "info"
                        collector.add(
                            "NGL-019",
                            node,
                            "This snippet enables `reload=True`. That is useful in development but easy to leave behind in entrypoints that should behave like production.",
                            "Keep reload in a dev-only launcher or set `reload=False` in the main entrypoint.",
                            severity=severity,
                        )
    return collector


def _inspect_handler(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    callback_names: set[str],
    requested_rules: set[str],
    collector: _FindingCollector,
    assignments: dict[str, list[ast.AST]],
) -> None:
    if not _is_handler(node, callback_names):
        return

    blocking_calls = [call for call in ast.walk(node) if isinstance(call, ast.Call) and _call_name(call) in BLOCKING_CALLS]
    if "NGL-009" in requested_rules:
        for call in blocking_calls:
            collector.add(
                "NGL-009",
                call,
                f"This handler performs blocking work via `{_call_name(call)}`.",
                "Use `ui.run.io_bound`, `ui.run.cpu_bound`, `background_tasks`, or an async-friendly library instead.",
            )

    if "NGL-010" in requested_rules and isinstance(node, ast.AsyncFunctionDef):
        has_await = any(isinstance(child, ast.Await) for child in ast.walk(node))
        if has_await and not _has_feedback(node):
            collector.add(
                "NGL-010",
                node,
                "This async handler awaits work without any visible loading, success, or error feedback.",
                "Disable the trigger, show progress or a spinner, and surface success or failure explicitly.",
            )

    if "NGL-008" in requested_rules:
        statement_count = sum(1 for child in ast.walk(node) if isinstance(child, ast.stmt))
        branch_count = sum(1 for child in ast.walk(node) if isinstance(child, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.Match)))
        external_calls = sum(
            1
            for child in ast.walk(node)
            if isinstance(child, ast.Call) and _call_name(child) not in {"ui.notify", "ui.label", "ui.button", "print", "len", "range"}
        )
        if statement_count >= 12 or branch_count >= 3 or external_calls >= 6:
            collector.add(
                "NGL-008",
                node,
                "This event handler mixes several branches, calls, and UI-side effects. NiceGUI handlers are easier to maintain when they stay thin.",
                "Move business logic into a controller or service and keep the handler focused on orchestration.",
            )

    if "NGL-016" in requested_rules:
        deferred_calls = {
            _call_name(call)
            for call in ast.walk(node)
            if isinstance(call, ast.Call) and _call_name(call) in {"background_tasks.create", "asyncio.create_task"}
        }
        if deferred_calls and not _has_feedback(node, allow_logging=True):
            collector.add(
                "NGL-016",
                node,
                "This handler defers work in the background without any visible feedback or logging.",
                "Add at least a notification, progress state, or a log at the start of the deferred action.",
            )

    if "NGL-020" in requested_rules:
        global_writes = any(isinstance(child, ast.Global) for child in ast.walk(node))
        ui_mutations = any(
            isinstance(child, ast.Assign)
            and isinstance(child.targets[0], ast.Attribute)
            and child.targets[0].attr in {"text", "value", "rows", "options", "visible"}
            for child in ast.walk(node)
        )
        service_calls = any(
            _call_name(child).split(".")[-1].startswith(("fetch", "load", "save", "delete", "sync", "calculate"))
            for child in ast.walk(node)
            if isinstance(child, ast.Call)
        )
        if (global_writes or _writes_assigned_names(node, assignments)) and ui_mutations and service_calls:
            collector.add(
                "NGL-020",
                node,
                "This handler mutates shared state, performs service-like work, and updates UI directly in one place.",
                "Introduce a controller boundary so state mutation and business logic are testable outside the UI callback.",
            )


def _inspect_page_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    requested_rules: set[str],
    collector: _FindingCollector,
    code: str,
    filename: str | None,
) -> None:
    if "NGL-018" not in requested_rules:
        return
    if not any(_is_ui_page_decorator(decorator) for decorator in node.decorator_list):
        return
    line_count = max((node.end_lineno or node.lineno) - node.lineno + 1, 1)
    ui_calls = sum(1 for child in ast.walk(node) if isinstance(child, ast.Call) and _call_name(child).startswith("ui."))
    if line_count >= 45 or ui_calls >= 18:
        filename_note = f" in {filename}" if filename else ""
        collector.add(
            "NGL-018",
            node,
            f"This `@ui.page` function is large enough to become a maintenance hotspot{filename_note}.",
            "Split the page into a layout shell plus reusable page sections or components.",
        )


def _inspect_boolean_state(node: ast.Module | ast.FunctionDef | ast.AsyncFunctionDef, requested_rules: set[str], collector: _FindingCollector) -> None:
    if "NGL-014" not in requested_rules:
        return
    bool_names: list[str] = []
    anchor: ast.AST | None = None
    for child in getattr(node, "body", []):
        if isinstance(child, ast.Assign) and isinstance(child.value, ast.Constant) and isinstance(child.value.value, bool):
            for target in child.targets:
                if isinstance(target, ast.Name):
                    bool_names.append(target.id)
                    anchor = anchor or child
    prefixed = [name for name in bool_names if name.startswith(("is_", "show_", "has_", "can_"))]
    if len(prefixed) >= 3:
        collector.add(
            "NGL-014",
            anchor,
            "This scope uses several booleans that likely model mutually exclusive UI states.",
            "Prefer a single explicit state enum or mode variable instead of boolean sprawl.",
        )


def _inspect_enum_candidates(node: ast.Module | ast.FunctionDef | ast.AsyncFunctionDef, requested_rules: set[str], collector: _FindingCollector) -> None:
    if "NGL-015" not in requested_rules:
        return
    comparisons: dict[str, set[str]] = defaultdict(set)
    first_node: ast.AST | None = None
    for child in ast.walk(node):
        if isinstance(child, ast.Compare) and isinstance(child.left, ast.Name) and len(child.ops) == 1 and isinstance(child.ops[0], ast.Eq):
            comparator = child.comparators[0]
            if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                comparisons[child.left.id].add(comparator.value)
                first_node = first_node or child
    if any(len(values) >= 3 for values in comparisons.values()):
        collector.add(
            "NGL-015",
            first_node,
            "The same variable is compared against several string literals. That usually reads better as an explicit enum.",
            "Define an `Enum` or named state constants and use that type consistently.",
        )


def _inspect_large_tables(node: ast.Call, requested_rules: set[str], collector: _FindingCollector, assignments: dict[str, list[ast.AST]]) -> None:
    if "NGL-017" not in requested_rules:
        return
    call_name = _call_name(node)
    if call_name not in {"ui.table", "ui.aggrid"}:
        return
    for keyword in node.keywords:
        if keyword.arg not in {"rows", "rowData"}:
            continue
        if _is_large_rows_value(keyword.value, assignments):
            collector.add(
                "NGL-017",
                node,
                "This data view appears to materialize a large in-memory row set directly into the UI component.",
                "Switch to server-side pagination, filtering, or incremental loading once the dataset grows.",
            )


def _inspect_repeated_components(node: ast.Module | ast.FunctionDef | ast.AsyncFunctionDef, requested_rules: set[str], collector: _FindingCollector, code: str) -> None:
    if "NGL-011" not in requested_rules:
        return
    if not getattr(node, "body", None):
        return
    card_blocks = [child for child in getattr(node, "body", []) if isinstance(child, (ast.With, ast.AsyncWith)) and "ui.card" in _source_for_node(code, child)]
    if len(card_blocks) >= 2:
        collector.add(
            "NGL-011",
            card_blocks[1],
            "This scope repeats card-style UI blocks that may be strong candidates for a reusable component.",
            "Extract the repeated structure into a small render helper or dedicated component module.",
        )


def _inspect_inconsistent_display(node: ast.Module | ast.FunctionDef | ast.AsyncFunctionDef, requested_rules: set[str], collector: _FindingCollector) -> None:
    if "NGL-012" not in requested_rules:
        return
    rendered_as_cards: set[str] = set()
    rendered_as_tables: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.For) and isinstance(child.target, ast.Name) and isinstance(child.iter, ast.Name):
            rendered_as_cards.add(child.iter.id)
        elif isinstance(child, ast.Call) and _call_name(child) == "ui.table":
            for keyword in child.keywords:
                if keyword.arg == "rows" and isinstance(keyword.value, ast.Name):
                    rendered_as_tables.add(keyword.value.id)
    overlap = rendered_as_cards & rendered_as_tables
    if overlap:
        collector.add(
            "NGL-012",
            node,
            f"The same data set is rendered through multiple patterns ({', '.join(sorted(overlap))}), which can drift into inconsistent UX.",
            "Choose a shared component or explicit display modes when the same data appears in different contexts.",
        )


def _collect_assignments(tree: ast.Module) -> dict[str, list[ast.AST]]:
    assignments: dict[str, list[ast.AST]] = defaultdict(list)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments[target.id].append(node.value)
    return assignments


def _collect_callback_targets(tree: ast.Module) -> tuple[set[str], list[ast.Lambda]]:
    callback_names: set[str] = set()
    lambda_handlers: list[ast.Lambda] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg and keyword.arg.startswith("on_"):
                if isinstance(keyword.value, ast.Name):
                    callback_names.add(keyword.value.id)
                elif isinstance(keyword.value, ast.Lambda):
                    lambda_handlers.append(keyword.value)
    return callback_names, lambda_handlers


def _is_handler(node: ast.FunctionDef | ast.AsyncFunctionDef, callback_names: set[str]) -> bool:
    return node.name.startswith("on_") or node.name.endswith("_handler") or node.name in callback_names


def _has_feedback(node: ast.FunctionDef | ast.AsyncFunctionDef, allow_logging: bool = False) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            call_name = _call_name(child)
            if call_name == "ui.notify":
                return True
            if any(token in call_name for token in ("spinner", "progress", "disable")):
                return True
            if allow_logging and call_name.startswith(("logger.", "logging.")):
                return True
        elif isinstance(child, ast.Assign):
            targets = [target.id for target in child.targets if isinstance(target, ast.Name)]
            if any(any(token in name for token in ("loading", "progress", "busy")) for name in targets):
                return True
    return False


def _writes_assigned_names(node: ast.FunctionDef | ast.AsyncFunctionDef, assignments: dict[str, list[ast.AST]]) -> bool:
    assigned_names = set(assignments)
    return any(isinstance(child, ast.Assign) and any(isinstance(target, ast.Name) and target.id in assigned_names for target in child.targets) for child in ast.walk(node))


def _is_large_rows_value(node: ast.AST, assignments: dict[str, list[ast.AST]]) -> bool:
    if isinstance(node, ast.List):
        return len(node.elts) >= 50
    if isinstance(node, ast.Name):
        return any(_is_large_rows_value(value, assignments) for value in assignments.get(node.id, []))
    if isinstance(node, ast.ListComp):
        for generator in node.generators:
            if isinstance(generator.iter, ast.Call) and _call_name(generator.iter) == "range":
                first_arg = generator.iter.args[0] if generator.iter.args else None
                if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, int) and first_arg.value >= 500:
                    return True
    return False


def _attach_parents(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            setattr(child, "_parent", node)


def _is_outermost_ui_call(node: ast.Call) -> bool:
    parent = getattr(node, "_parent", None)
    if isinstance(parent, ast.Attribute) and parent.value is node:
        grandparent = getattr(parent, "_parent", None)
        return not (isinstance(grandparent, ast.Call) and grandparent.func is parent)
    return True


def _describe_ui_chain(node: ast.AST, code: str) -> UIChain | None:
    if not isinstance(node, ast.Call):
        return None
    calls: list[ast.Call] = []
    current: ast.AST = node
    while isinstance(current, ast.Call) and isinstance(current.func, ast.Attribute):
        calls.append(current)
        if isinstance(current.func.value, ast.Name) and current.func.value.id == "ui":
            break
        current = current.func.value
    root_call = calls[-1] if calls else None
    if not (
        root_call
        and isinstance(root_call.func, ast.Attribute)
        and isinstance(root_call.func.value, ast.Name)
        and root_call.func.value.id == "ui"
    ):
        return None
    calls.reverse()
    root_call = calls[0]
    classes: list[str] = []
    styles: list[str] = []
    props: list[str] = []
    for call in calls[1:]:
        if call.func.attr == "classes":
            for value in _literal_string_args(call):
                classes.extend(token for token in value.split() if token)
        elif call.func.attr == "style":
            for value in _literal_string_args(call):
                styles.append(value)
        elif call.func.attr == "props":
            for value in _literal_string_args(call):
                props.extend(token for token in value.split() if token)
    keywords = {keyword.arg: keyword.value for keyword in root_call.keywords if keyword.arg}
    return UIChain(
        node=node,
        root=root_call.func.attr,
        source=_source_for_node(code, node),
        classes=classes,
        styles=styles,
        props=props,
        keywords=keywords,
    )


def _literal_string_args(node: ast.Call) -> list[str]:
    values: list[str] = []
    for arg in node.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            values.append(arg.value)
    return values


def _styles_contain_gap(styles: list[str]) -> bool:
    return any("gap:" in style or "gap :" in style for style in styles)


def _styles_contain_height(styles: list[str]) -> bool:
    lowered = " ".join(styles).casefold()
    return "height: 100%" in lowered or "height:100%" in lowered or "height: 100vh" in lowered


def _has_min_height_zero(chain: UIChain) -> bool:
    class_hit = "min-h-0" in chain.classes
    style_hit = any("min-height: 0" in style.casefold().replace("  ", " ") for style in chain.styles)
    return class_hit or style_hit


def _has_constrained_height(chain: UIChain) -> bool:
    lowered_styles = " ".join(chain.styles).casefold()
    return any(token in chain.classes for token in ("h-full", "h-screen")) or any(token.startswith(("max-h-", "min-h-")) for token in chain.classes) or any(
        marker in lowered_styles for marker in ("height:", "max-height:", "min-height:")
    )


def _is_ui_page_decorator(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and _call_name(node) == "ui.page"


def _call_name(node: ast.Call) -> str:
    target: ast.AST = node.func
    parts: list[str] = []
    while isinstance(target, ast.Attribute):
        parts.append(target.attr)
        target = target.value
    if isinstance(target, ast.Name):
        parts.append(target.id)
    return ".".join(reversed(parts))


def _source_for_node(code: str, node: ast.AST) -> str:
    return ast.get_source_segment(code, node) or ""


def _build_summary(findings: list[Finding]) -> str:
    if not findings:
        return "No known NiceGUI issues detected in the provided snippet."
    counts = Counter(finding.severity for finding in findings)
    parts = [f"{counts[severity]} {severity}" for severity in ("error", "warning", "info") if counts[severity]]
    return f"Found {len(findings)} issue(s): {', '.join(parts)}."
