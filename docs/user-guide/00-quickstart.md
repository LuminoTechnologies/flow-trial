# Quickstart Guide

This guide walks you through the most useful workflows in about 10 minutes.
It assumes you have completed the [setup steps](01-setup.md) in the README.

---

## Step 1 - Verify your connection

```bash
python scripts/flow_cli.py auth
```

Expected output: `{"status": "ok", "accessToken": "..."}`.
If you see an error, check your `.env` file.

---

## Step 2 - See what's in your project

```bash
python scripts/flow_cli.py req list --all
```

This fetches every requirement across all pages and prints them as JSON.
When using Claude Code, ask instead:

```text
/flow list all my requirements as a table
```

---

## Step 3 - Import requirements from Excel

If you have requirements in a spreadsheet:

```bash
# Check what would be imported (no changes made)
python scripts/flow_cli.py import flow-test.xlsx --preview

# Check data quality too (still no changes)
python scripts/flow_cli.py import flow-test.xlsx --dry-run

# Import for real (a backup is created automatically first)
python scripts/flow_cli.py import flow-test.xlsx
```

The import is safe to re-run - already-imported rows are skipped automatically.

---

## Step 4 - Check requirement quality

```bash
python scripts/flow_cli.py quality --fix-hints
```

This checks every requirement against 8 INCOSE rules and shows suggested fixes.
Errors (e.g. missing "shall") are shown first, then warnings, then informational notes.

To check a single requirement:

```bash
python scripts/flow_cli.py quality --id 42 --fix-hints
```

---

## Step 5 - Find traceability gaps

```bash
# Which requirements aren't allocated to any system?
python scripts/flow_cli.py trace gaps

# How many requirements does each system have?
python scripts/flow_cli.py trace systems

# Generate a full requirements x systems matrix
python scripts/flow_cli.py trace matrix
```

The matrix is saved to `outputs/traceability_matrix_YYYYMMDD.md`.

---

## Step 6 - Generate test case drafts

```bash
# Draft test cases for all requirements containing "shall"
python scripts/flow_cli.py testgen
```

This writes `outputs/testcases_draft_YYYYMMDD_HHMMSS.json`. Review and edit the file,
then create the test cases in Flow and link them to their requirements:

```bash
python scripts/flow_cli.py testgen --commit
```

---

## Step 7 - Assess change impact before making a change

Before modifying a requirement, check what else might be affected:

```bash
python scripts/flow_cli.py impact req <id>
```

This shows parent/child requirements, cross-links, linked test cases, and system allocation.

---

## Step 8 - Undo a change

Every write command saves a backup automatically. To see your backups:

```bash
python scripts/flow_cli.py backup list
```

To restore:

```bash
python scripts/flow_cli.py restore <backup-id>
```

---

## Common Claude Code patterns

You can also do all of this conversationally. Some useful prompts:

```text
/flow check the quality of all requirements and show me only the errors
```

```text
/flow import flow-test.xlsx - show me a preview first, then ask me before importing
```

```text
/flow what requirements are not allocated to any system?
```

```text
/flow generate test cases for requirement 42
```

```text
/flow what would be affected if I change requirement 15?
```

```text
/flow generate an ICD for the SystemA-SystemB interface
```

---

## Where to go next

| Guide | What it covers |
| ----- | -------------- |
| [Importing requirements](02-importing-requirements.md) | Column mapping, idempotency, config file |
| [Quality review](03-quality-review.md) | INCOSE rules, custom rules, output report |
| [Test cases](04-test-cases.md) | Draft workflow, committing to Flow |
| [Traceability](05-traceability.md) | Matrix, allocation suggestions |
| [Change impact](06-change-impact.md) | Diffing against backups |
| [ICD generation](07-icd-generation.md) | Tagging interface requirements, document structure |
| [Design values](08-design-values.md) | Syncing values from analysis models |
