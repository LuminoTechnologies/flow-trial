# Traceability Analysis

The `flow trace` command helps you understand and manage system allocation.

## Subcommands

### List systems and requirement counts

```bash
python scripts/flow_cli.py trace systems
```

Shows all systems and how many requirements are allocated to each.

### Find unallocated requirements

```bash
python scripts/flow_cli.py trace gaps
```

Lists all requirements not allocated to any system. Use this to find traceability gaps before reviews.

### Generate a traceability matrix

```bash
python scripts/flow_cli.py trace matrix
python scripts/flow_cli.py trace matrix --format csv
```

Creates a requirement x system matrix. Saved to `outputs/traceability_matrix_YYYYMMDD.md` (or `.csv`).

### Allocate a requirement to a system

```bash
python scripts/flow_cli.py trace allocate <req-id> <system-id>
```

Assigns a requirement to a system. A backup is created before the change.

### Get allocation suggestions

```bash
python scripts/flow_cli.py trace suggest
```

Analyses unallocated requirement text and suggests which system each should belong to.
Suggestions are written to `outputs/trace_suggestions_YYYYMMDD.json` for review.
Use `flow trace allocate` to commit them.
