# Design Values and Model Awareness

The `flow models` command helps manage requirements whose values come from analysis models
(e.g. Python scripts, Excel calculations).

## Tagging model-derived requirements

Requirements derived from a model should have the custom field `value_source: model` set in Flow.
This makes them identifiable and enables the quality rule that flags untagged numeric requirements.

## Subcommands

### List requirements with numeric values

```bash
python scripts/flow_cli.py models list
```

Lists all requirements whose description contains a numeric value, grouped by `value_source` tag.
Requirements with numbers but no `value_source` tag are flagged as a warning.

### Sync values from a model CSV export

```bash
python scripts/flow_cli.py models sync --csv path/to/model_output.csv
```

Reads a CSV file exported from your analysis model and updates matched requirements in Flow.

**CSV format:**

| Column | Purpose |
|--------|---------|
| `import_id` | Match by import ID (e.g. `Sheet1::row5`) - preferred |
| `name` | Match by requirement name - fallback |
| `description` | New description/value to write to Flow |

Unmatched rows are skipped with a warning. A backup is created before any updates.

## Workflow

1. Run your analysis model and export results to CSV.
2. Run `flow models sync --csv model_output.csv` to push updated values.
3. Use `flow quality` to check that updated requirements still have valid `shall` statements.
4. Use `flow icd generate` to regenerate ICDs with the new values.
