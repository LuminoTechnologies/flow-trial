# Test Case Generation

The `flow testgen` command generates structured test case drafts from requirement statements.

## Workflow

1. Generate draft test cases and write them to a JSON file for review:
   ```bash
   python scripts/flow_cli.py testgen
   ```

2. Review and edit the file at `outputs/testcases_draft_YYYYMMDD_HHMMSS.json`.

3. Commit approved test cases to Flow and link them to their requirements:
   ```bash
   python scripts/flow_cli.py testgen --commit
   ```

## Options

```bash
# Generate for a single requirement
python scripts/flow_cli.py testgen --id 42

# Create test cases in Flow from the latest draft file
python scripts/flow_cli.py testgen --commit
```

## How generation works

Only requirements whose description contains "shall" are eligible for test generation.
For each eligible requirement, a test case is drafted with:

- A name derived from the requirement name
- Steps including setup, execution, verification, and documentation
- An expected result stating the requirement must be satisfied
- `stage: draft` and `source: auto-generated` tags for easy filtering

## Notes

Generated test cases are a starting point. Always review and refine them before committing.
Once committed, they are linked to their source requirement in Flow.
