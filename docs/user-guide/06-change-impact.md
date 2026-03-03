# Change Impact Analysis

The `flow impact` command shows what is affected by a change before you make it.

## Subcommands

### Requirement impact

```bash
python scripts/flow_cli.py impact req <id>
```

Shows everything linked to a requirement: parent and child requirements, cross-links,
linked test cases, system allocation, owner, and stage.
Also prints a summary count of impacted items.

### System impact

```bash
python scripts/flow_cli.py impact system <id>
```

Lists all requirements allocated to a system and summarises the impact of changing it.

### Diff against a backup

```bash
python scripts/flow_cli.py impact diff <backup-id>
```

Compares the current project state against a backup snapshot and lists:

- Requirements added since the backup
- Requirements removed since the backup
- Requirements modified (with field-level diff)

A diff report is saved to `outputs/diff_<backup-id>_YYYYMMDD.json`.

## Finding backup IDs

```bash
python scripts/flow_cli.py backup list
```

Use the backup ID printed after any write operation, or pick one from the list.
