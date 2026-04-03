from __future__ import annotations

from pathlib import Path

from nicegui_mcp.analyzers import analyze_code

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _fixture(group: str, name: str) -> str:
    return (FIXTURE_DIR / group / f"{name}.py").read_text(encoding="utf-8")


def _has_rule(code: str, rule_id: str) -> bool:
    return any(finding.rule_id == rule_id for finding in analyze_code(code).findings)


def test_tier1_invalid_fixtures_trigger_expected_rules() -> None:
    expected = {
        "ngl003_invalid": "NGL-003",
        "ngl013_invalid": "NGL-013",
        "ngl004_invalid": "NGL-004",
        "ngl005_invalid": "NGL-005",
        "ngl007_invalid": "NGL-007",
        "ngl009_invalid": "NGL-009",
        "ngl010_invalid": "NGL-010",
        "ngl008_invalid": "NGL-008",
        "ngl018_invalid": "NGL-018",
    }
    for fixture_name, rule_id in expected.items():
        assert _has_rule(_fixture("invalid", fixture_name), rule_id), fixture_name


def test_tier1_valid_fixtures_do_not_trigger_target_rule() -> None:
    expected = {
        "ngl003_valid": "NGL-003",
        "ngl013_valid": "NGL-013",
        "ngl004_valid": "NGL-004",
        "ngl005_valid": "NGL-005",
        "ngl007_valid": "NGL-007",
        "ngl009_valid": "NGL-009",
        "ngl010_valid": "NGL-010",
        "ngl008_valid": "NGL-008",
        "ngl018_valid": "NGL-018",
    }
    for fixture_name, rule_id in expected.items():
        assert not _has_rule(_fixture("valid", fixture_name), rule_id), fixture_name


def test_focus_filters_rules() -> None:
    code = "ui.button('Save').props('width=50%')\n"
    result = analyze_code(code, focus=["styling"])
    assert [finding.rule_id for finding in result.findings] == ["NGL-003"]


def test_tier2_rules() -> None:
    cases = {
        "NGL-001": """
with ui.column().classes('gap-8'):
    ui.label('One')
    ui.label('Two')
""",
        "NGL-002": """
with ui.row():
    ui.card().style('width: 50%')
    ui.card().style('width: 50%')
""",
        "NGL-014": """
show_list = True
show_detail = False
show_edit = False
""",
        "NGL-015": """
def render(mode: str) -> None:
    if mode == 'list':
        pass
    elif mode == 'detail':
        pass
    elif mode == 'edit':
        pass
""",
        "NGL-016": """
from nicegui import background_tasks, ui

def on_click() -> None:
    background_tasks.create(run_sync())

ui.button('Run', on_click=on_click)
""",
        "NGL-017": """
rows = [{'id': i} for i in range(2000)]
ui.table(columns=[{'name': 'id', 'label': 'ID', 'field': 'id'}], rows=rows)
""",
        "NGL-019": """
from nicegui import ui

ui.run(reload=True)
""",
        "NGL-020": """
count = 0

def fetch_orders():
    return [1, 2, 3]

def on_click() -> None:
    global count
    orders = fetch_orders()
    count = len(orders)
    label.text = str(count)

ui.button('Load', on_click=on_click)
""",
    }
    for rule_id, code in cases.items():
        assert _has_rule(code, rule_id), rule_id


def test_tier3_rules() -> None:
    cases = {
        "NGL-006": """
with ui.row():
    with ui.column():
        ui.echart({'series': []})
""",
        "NGL-011": """
def render() -> None:
    with ui.card():
        ui.label('A')
    with ui.card():
        ui.label('B')
""",
        "NGL-012": """
orders = []

for order in orders:
    ui.label(str(order))

ui.table(columns=[{'name': 'id', 'label': 'ID', 'field': 'id'}], rows=orders)
""",
    }
    for rule_id, code in cases.items():
        assert _has_rule(code, rule_id), rule_id
