from __future__ import annotations

from collections.abc import Iterable

from .models import TopicInfo


TOPIC_ALIASES = {
    "layout": "layout_spacing_scrolling",
    "spacing": "layout_spacing_scrolling",
    "scrolling": "layout_spacing_scrolling",
    "async": "async_tasks_performance",
    "performance": "async_tasks_performance",
    "styling": "styling_theming",
    "theming": "styling_theming",
    "state": "state_management",
    "components": "component_architecture",
    "architecture": "component_architecture",
    "forms": "forms_validation",
    "data_views": "data_views_tables_charts",
    "tables": "data_views_tables_charts",
    "charts": "data_views_tables_charts",
    "deployment": "deployment_runtime",
    "runtime": "deployment_runtime",
}


TOPICS: list[TopicInfo] = [
    TopicInfo(
        name="layout_spacing_scrolling",
        summary="Rows, columns, gap control, scroll areas, min-height issues, and app shell layout patterns.",
        tags=["layout", "spacing", "scrolling", "row", "column", "overflow"],
    ),
    TopicInfo(
        name="async_tasks_performance",
        summary="Blocking work, async handler feedback, background tasks, timers, and reload caveats.",
        tags=["async", "performance", "background_tasks", "feedback", "reload"],
    ),
    TopicInfo(
        name="styling_theming",
        summary="How `.style`, `.classes`, `.props`, Quasar props, and Tailwind interact in NiceGUI.",
        tags=["styling", "tailwind", "quasar", "props", "classes"],
    ),
    TopicInfo(
        name="dialogs",
        summary="Persistent dialogs, confirmation flows, sticky actions, and destructive action UX.",
        tags=["dialog", "modal", "confirm", "persistent", "sticky-actions"],
    ),
    TopicInfo(
        name="state_management",
        summary="State containers, refreshable rendering, enums over booleans, and session/controller patterns.",
        tags=["state", "refreshable", "ui.state", "enum", "session"],
    ),
    TopicInfo(
        name="component_architecture",
        summary="Layout shells, thin page handlers, reusable components, and controller/service boundaries.",
        tags=["components", "architecture", "layout-shell", "controller", "service"],
    ),
    TopicInfo(
        name="forms_validation",
        summary="Per-input validation, aggregated forms, sticky form actions, and stepper workflows.",
        tags=["forms", "validation", "wizard", "sticky-actions"],
    ),
    TopicInfo(
        name="data_views_tables_charts",
        summary="Tables, AG Grid, charts, list/detail layouts, and filterable data views.",
        tags=["table", "aggrid", "chart", "dashboard", "data-view"],
    ),
    TopicInfo(
        name="testing",
        summary="Pytest plugin setup, async UI tests, and stable NiceGUI test fixtures.",
        tags=["testing", "pytest", "fixtures", "screen", "user"],
    ),
    TopicInfo(
        name="deployment_runtime",
        summary="ASGI deployment basics, websocket proxying, reload mode, and On Air caveats.",
        tags=["deployment", "runtime", "asgi", "websocket", "nginx"],
    ),
]

TOPIC_BY_NAME = {topic.name: topic for topic in TOPICS}

TOPIC_SOURCE_URLS = {
    "layout_spacing_scrolling": [
        "https://nicegui.io/documentation",
        "https://nicegui.io/static/search_index.json",
    ],
    "async_tasks_performance": [
        "https://nicegui.io/documentation",
    ],
    "styling_theming": [
        "https://nicegui.io/documentation",
    ],
    "dialogs": [
        "https://nicegui.io/documentation",
    ],
    "state_management": [
        "https://nicegui.io/documentation",
    ],
    "component_architecture": [
        "https://nicegui.io/documentation",
    ],
    "forms_validation": [
        "https://nicegui.io/documentation",
    ],
    "data_views_tables_charts": [
        "https://nicegui.io/documentation",
    ],
    "testing": [
        "https://nicegui.io/documentation",
    ],
    "deployment_runtime": [
        "https://nicegui.io/documentation",
    ],
}

RULE_DETAILS = {
    "NGL-001": {
        "title": "Excessive row or column gap",
        "severity": "warning",
        "confidence": "medium",
        "auto_fixability": "partial",
    },
    "NGL-002": {
        "title": "Row width overflow risk",
        "severity": "warning",
        "confidence": "medium",
        "auto_fixability": "guidance_only",
    },
    "NGL-003": {
        "title": "Inline styles vs Tailwind misuse",
        "severity": "warning",
        "confidence": "high",
        "auto_fixability": "safe",
    },
    "NGL-004": {
        "title": "Scroll area missing min-height fix",
        "severity": "warning",
        "confidence": "high",
        "auto_fixability": "safe",
    },
    "NGL-005": {
        "title": "Scroll area with unconstrained height",
        "severity": "warning",
        "confidence": "medium",
        "auto_fixability": "guidance_only",
    },
    "NGL-006": {
        "title": "Flex child may require min-width: 0",
        "severity": "info",
        "confidence": "low",
        "auto_fixability": "guidance_only",
    },
    "NGL-007": {
        "title": "Non-persistent destructive dialog",
        "severity": "warning",
        "confidence": "high",
        "auto_fixability": "safe",
    },
    "NGL-008": {
        "title": "Logic-heavy event handler",
        "severity": "warning",
        "confidence": "high",
        "auto_fixability": "guidance_only",
    },
    "NGL-009": {
        "title": "Blocking call in handler",
        "severity": "error",
        "confidence": "high",
        "auto_fixability": "partial",
    },
    "NGL-010": {
        "title": "Async action without feedback",
        "severity": "warning",
        "confidence": "medium",
        "auto_fixability": "guidance_only",
    },
    "NGL-011": {
        "title": "Repeated component extraction candidate",
        "severity": "info",
        "confidence": "low",
        "auto_fixability": "guidance_only",
    },
    "NGL-012": {
        "title": "Inconsistent data-display pattern",
        "severity": "info",
        "confidence": "low",
        "auto_fixability": "guidance_only",
    },
    "NGL-013": {
        "title": "Conflicting color props and classes",
        "severity": "warning",
        "confidence": "high",
        "auto_fixability": "partial",
    },
    "NGL-014": {
        "title": "Many booleans representing state",
        "severity": "warning",
        "confidence": "medium",
        "auto_fixability": "guidance_only",
    },
    "NGL-015": {
        "title": "Prefer explicit enums for state",
        "severity": "info",
        "confidence": "medium",
        "auto_fixability": "guidance_only",
    },
    "NGL-016": {
        "title": "Missing feedback for deferred actions",
        "severity": "warning",
        "confidence": "medium",
        "auto_fixability": "guidance_only",
    },
    "NGL-017": {
        "title": "Table with large in-memory rows",
        "severity": "warning",
        "confidence": "medium",
        "auto_fixability": "guidance_only",
    },
    "NGL-018": {
        "title": "Monolithic page function",
        "severity": "warning",
        "confidence": "high",
        "auto_fixability": "guidance_only",
    },
    "NGL-019": {
        "title": "Reload enabled in production entrypoint",
        "severity": "warning",
        "confidence": "high",
        "auto_fixability": "safe",
    },
    "NGL-020": {
        "title": "Missing controller boundary",
        "severity": "warning",
        "confidence": "medium",
        "auto_fixability": "guidance_only",
    },
}

RULE_IDS_IN_ORDER = list(RULE_DETAILS.keys())

TIER_1_RULES = [
    "NGL-003",
    "NGL-013",
    "NGL-004",
    "NGL-005",
    "NGL-007",
    "NGL-009",
    "NGL-010",
    "NGL-008",
    "NGL-018",
]

TIER_2_RULES = [
    "NGL-001",
    "NGL-002",
    "NGL-014",
    "NGL-015",
    "NGL-016",
    "NGL-017",
    "NGL-019",
    "NGL-020",
]

TIER_3_RULES = [
    "NGL-006",
    "NGL-011",
    "NGL-012",
]

FOCUS_RULES = {
    "layout_spacing_scrolling": {"NGL-001", "NGL-002", "NGL-004", "NGL-005", "NGL-006"},
    "async_tasks_performance": {"NGL-009", "NGL-010", "NGL-016", "NGL-019"},
    "styling_theming": {"NGL-003", "NGL-013"},
    "dialogs": {"NGL-007"},
    "state_management": {"NGL-014", "NGL-015"},
    "component_architecture": {"NGL-008", "NGL-011", "NGL-012", "NGL-018", "NGL-020"},
    "forms_validation": {"NGL-007", "NGL-010", "NGL-014"},
    "data_views_tables_charts": {"NGL-006", "NGL-012", "NGL-017"},
    "testing": set(),
    "deployment_runtime": {"NGL-019"},
}

SAFE_FIX_RULES = {"NGL-003", "NGL-004", "NGL-007", "NGL-009", "NGL-019"}


def normalize_topic_name(name: str) -> str:
    token = name.strip().lower().replace("-", "_").replace(" ", "_")
    return TOPIC_ALIASES.get(token, token)


def normalize_focus_list(focus: Iterable[str] | None) -> list[str] | None:
    if focus is None:
        return None
    normalized: list[str] = []
    for item in focus:
        token = normalize_topic_name(item)
        if token in TOPIC_BY_NAME and token not in normalized:
            normalized.append(token)
    return normalized


def requested_rule_ids(focus: Iterable[str] | None) -> tuple[list[str] | None, set[str]]:
    normalized_focus = normalize_focus_list(focus)
    if normalized_focus is None or not normalized_focus:
        return normalized_focus, set(RULE_IDS_IN_ORDER)
    rule_ids: set[str] = set()
    for topic in normalized_focus:
        rule_ids.update(FOCUS_RULES.get(topic, set()))
    return normalized_focus, rule_ids
