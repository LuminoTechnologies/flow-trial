# Importing Requirements from Excel

The `flow import` command reads an `.xlsx` file and creates requirements in Flow.
Each worksheet maps to a set of requirements. Column headers are matched to Flow fields automatically.

## Quick start

```bash
# Preview what would be imported (no API calls)
python scripts/flow_cli.py import flow-test.xlsx --preview

# Quality check the data (no API calls)
python scripts/flow_cli.py import flow-test.xlsx --dry-run

# Import for real (creates a backup first)
python scripts/flow_cli.py import flow-test.xlsx
```

## Column mapping

By default the importer looks for common column header names:

| Flow field | Recognised column names (first match wins) |
|------------|-------------------------------------------|
| name | Req ID, ID, Name, Requirement ID |
| description | Statement, Description, Requirement, Text |
| owner | Owner, Responsible, Assignee |
| type | Type, Req Type, Requirement Type |
| rationale | Rationale, Justification |
| notes | Notes, Comments |

To customise column mapping, copy `config/import_config.yaml.example` to `config/import_config.yaml` and edit it.

## Idempotency

Each row is tagged with an `import_id` based on sheet name and row number.
Re-running the import skips rows that already exist in Flow. Safe to run multiple times.

## What gets backed up

Before importing, a snapshot of all current requirements is saved to `backups/`.
Use `flow backup list` to see available backups and `flow restore <backup-id>` to undo.

## Output report

After a successful import, a JSON report is written to `outputs/import_YYYYMMDD_HHMMSS.json`
listing created requirement IDs, skipped rows, and any failures.
