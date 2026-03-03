# Requirements Quality Review

The `flow quality` command checks your requirements against INCOSE good-writing rules
and any custom rules defined in `config/quality_rules.yaml`.

## Usage

```bash
# Review all requirements in the project
python scripts/flow_cli.py quality

# Review a single requirement
python scripts/flow_cli.py quality --id 42

# Show fix hints for each violation
python scripts/flow_cli.py quality --fix-hints

# Use a custom rules file
python scripts/flow_cli.py quality --rules path/to/my_rules.yaml
```

## Built-in INCOSE rules

| ID | Rule | Severity |
|----|------|----------|
| INC001 | Statement must contain "shall" | error |
| INC002 | Avoid "should", "will", "must" | warning |
| INC003 | No ambiguous terms | warning |
| INC004 | No compound requirements | error |
| INC005 | Owner field must be set | warning |
| INC006 | Verification method must be set | warning |
| INC007 | Requirement must be allocated to a system | warning |
| INC008 | Statement should reference a measurable quantity | info |

## Adding custom rules

Edit `config/quality_rules.yaml` and add entries under the `custom:` section.
Rule check types available: `regex_must_match`, `regex_must_not_match`, `keyword_forbidden`, `field_must_be_set`.

## Output

Results are printed grouped by severity (errors first) and saved to `outputs/quality_YYYYMMDD.json`.
