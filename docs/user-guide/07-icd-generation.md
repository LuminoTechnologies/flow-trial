# ICD Generation

The `flow icd` command extracts interface requirements from Flow and generates
Interface Control Documents as markdown files.

## Setup: tagging interface requirements

Requirements that describe an interface should be tagged with the custom field
`interface_pair: "SystemA-SystemB"` in Flow. This identifies which ICD they belong to.

Both interface systems should also be allocated to the requirement (via system allocation).

## Subcommands

### List detected interface pairs

```bash
python scripts/flow_cli.py icd list
```

Shows all interface pairs found in the project based on `interface_pair` custom field tags.

### Generate an ICD document

```bash
# Generate ICDs for all detected interface pairs
python scripts/flow_cli.py icd generate

# Generate for a specific pair
python scripts/flow_cli.py icd generate --pair "SystemA-SystemB"
```

Documents are saved to `outputs/icd_SystemA-SystemB_YYYYMMDD.md`.

## ICD document structure

Each generated document contains:

1. **Interface summary** - interface pair, direction, protocol/medium (if tagged)
2. **Interface requirements** - table of requirements with ID, statement, verification method, owner, stage
3. **Design values** - requirements tagged with `value_source: model`
4. **Open items** - draft requirements or those missing a verification method

## Notes

The ICD format is a suggested starting point. Agree with your team on the final structure
before sharing with external stakeholders. The markdown can be converted to Word/PDF
using pandoc when that capability is added (see ROADMAP).
