# Forms and Validation

Sources
- https://nicegui.io/documentation

## Per-Input Validation

Use built-in validation where it keeps the form readable.

```python
name = ui.input('Name', validation={'Required': lambda value: bool(value)})
```

## Aggregated Validation

Complex forms benefit from a small form helper or explicit `validate_all()` step.

- do not scatter validation across unrelated callbacks
- keep submit enablement rules readable
- show clear error states before destructive or expensive actions

## Sticky Form Actions

Long forms should keep actions visible.

- scroll the body
- dock the action bar
- separate cancel from primary save clearly

## Dynamic Validation

Validation often depends on other fields.

- revalidate dependent fields when driving values change
- keep those rules close to the form model or controller
