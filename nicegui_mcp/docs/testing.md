# Testing

Sources
- https://nicegui.io/documentation

## Pytest Setup

NiceGUI testing is easiest when the project standardizes its pytest setup early.

- keep the NiceGUI pytest plugin configured consistently
- centralize reusable test fixtures
- avoid ad hoc UI bootstrapping in every test module

## Stable Test Patterns

- test controllers and services directly outside the UI layer
- keep widget-level tests focused on behavior, not implementation trivia
- use async tests when the page logic depends on awaited work

## What to Test Here

For this MCP, core tests should cover:

- guidance loading and search
- analyzer findings
- fixer idempotence
- generator determinism
