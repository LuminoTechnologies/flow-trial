# /flow - Interact with the Flow requirements management API

You are helping the user interact with Flow (flowengineering.com) via the REST API v1.

## Full API capabilities reference

See [docs/flow-api-capabilities.md](../../docs/flow-api-capabilities.md) for a complete index of every read and write operation available. The Python helper implements a commonly-used subset; for anything not yet in the helper, you can call the API directly using curl or extend the script.

If a user asks for something that does not appear in the capabilities document:

1. Check the Flow changelog at [flow-engineering.productlane.com/changelog](https://flow-engineering.productlane.com/changelog) for any mention of the feature.
2. If the changelog suggests it has been added or changed, re-fetch the OpenAPI spec at `https://api.flowengineering.com/rest/v1/openapi.json` and compare it against the current capabilities document.
3. Update `docs/flow-api-capabilities.md` to reflect any new or changed endpoints before proceeding.

## How to call the API

Use the CLI via Bash:

```bash
python scripts/flow_cli.py <command> [subcommand] [options]
```

The script automatically loads `.env` from the repo root, so no manual setup is needed.

If the script prints `ERROR: FLOW_REFRESH_TOKEN environment variable is not set`, tell the user to create a `.env` file by copying `.env.example` and filling in their credentials.

## Available commands

### Test authentication

```bash
python scripts/flow_cli.py auth
```

### Requirement CRUD

```bash
python scripts/flow_cli.py req list
python scripts/flow_cli.py req list --all           # fetch all pages automatically
python scripts/flow_cli.py req list --limit 100
python scripts/flow_cli.py req get <id>
python scripts/flow_cli.py req create '{"name": "REQ-001", "description": "The system shall..."}'
python scripts/flow_cli.py req update <id> '{"name": "Updated name"}'
```

### Traceability links

```bash
python scripts/flow_cli.py link req-req <source-id> parent <target-id>
python scripts/flow_cli.py link req-req <source-id> child <target-id>
python scripts/flow_cli.py link req-req <source-id> cross <target-id> --target-project other-project
python scripts/flow_cli.py link req-tc <requirement-id> <test-case-id>
```

### Backup and restore

```bash
python scripts/flow_cli.py backup list
python scripts/flow_cli.py restore <backup-id>
```

Every write command automatically creates a backup before modifying data.

### Import from Excel

```bash
python scripts/flow_cli.py import flow-test.xlsx --preview    # parse only, no API calls
python scripts/flow_cli.py import flow-test.xlsx --dry-run    # preview + quality check
python scripts/flow_cli.py import flow-test.xlsx              # full import with backup
```

See [docs/user-guide/02-importing-requirements.md](../../docs/user-guide/02-importing-requirements.md).

### Quality review (INCOSE rules)

```bash
python scripts/flow_cli.py quality                # review all requirements
python scripts/flow_cli.py quality --id 42        # review single requirement
python scripts/flow_cli.py quality --fix-hints    # show suggested corrections
```

See [docs/user-guide/03-quality-review.md](../../docs/user-guide/03-quality-review.md).

### Test case generation

```bash
python scripts/flow_cli.py testgen                # generate drafts for all 'shall' requirements
python scripts/flow_cli.py testgen --id 42        # generate for a single requirement
python scripts/flow_cli.py testgen --commit       # create approved drafts in Flow + link to reqs
```

See [docs/user-guide/04-test-cases.md](../../docs/user-guide/04-test-cases.md).

### Traceability analysis

```bash
python scripts/flow_cli.py trace systems
python scripts/flow_cli.py trace gaps
python scripts/flow_cli.py trace matrix [--format csv]
python scripts/flow_cli.py trace allocate <req-id> <sys-id>
python scripts/flow_cli.py trace suggest
```

See [docs/user-guide/05-traceability.md](../../docs/user-guide/05-traceability.md).

### Change impact analysis

```bash
python scripts/flow_cli.py impact req <id>
python scripts/flow_cli.py impact system <id>
python scripts/flow_cli.py impact diff <backup-id>
```

See [docs/user-guide/06-change-impact.md](../../docs/user-guide/06-change-impact.md).

### ICD generation

```bash
python scripts/flow_cli.py icd list
python scripts/flow_cli.py icd generate [--pair "SystemA-SystemB"]
```

Tag requirements with custom field `interface_pair: "SystemA-SystemB"` to define ICD scope.
See [docs/user-guide/07-icd-generation.md](../../docs/user-guide/07-icd-generation.md).

### Design values model awareness

```bash
python scripts/flow_cli.py models list
python scripts/flow_cli.py models sync --csv model_output.csv
```

See [docs/user-guide/08-design-values.md](../../docs/user-guide/08-design-values.md).

## Presenting results

- Format JSON results as readable markdown tables or summaries, not raw JSON dumps.
- For lists, show key fields: ID, name, and a brief description or status.
- For single items, show all fields in a structured format.
- If a command returns an error, show the error message clearly and suggest remediation.

## When the API cannot help

Some tasks cannot be done via the API (e.g. setting up GitHub/Jira integrations, configuring views, managing baselines, architecture diagrams). When that is the case, point the user to the relevant knowledge base article rather than attempting to use the API.

Knowledge base home: [flow-engineering-knowledge-base.help.usepylon.com](https://flow-engineering-knowledge-base.help.usepylon.com/)

### Getting started

- [Watch a Flow demo](https://flow-engineering-knowledge-base.help.usepylon.com/articles/8331525965-watch-a-flow-demo)
- [How-to videos](https://flow-engineering-knowledge-base.help.usepylon.com/articles/7555156599-how-to-videos)
- [Organising your first project](https://flow-engineering-knowledge-base.help.usepylon.com/articles/3853125637-organizing-your-first-project-in-flow)
- [Creating a new project](https://flow-engineering-knowledge-base.help.usepylon.com/articles/2885495415-creating-a-new-project)
- [Duplicating a project](https://flow-engineering-knowledge-base.help.usepylon.com/articles/6070110227-duplicating-a-project)
- [Inviting people to your project](https://flow-engineering-knowledge-base.help.usepylon.com/articles/3483166932-inviting-people-to-your-project)
- [Permissions in Flow](https://flow-engineering-knowledge-base.help.usepylon.com/articles/6806063151-permissions-in-flow)

### Requirements

- [Adding and organising requirements](https://flow-engineering-knowledge-base.help.usepylon.com/articles/1213306265-adding-and-organising-your-first-few-requirements)
- [Understanding data types](https://flow-engineering-knowledge-base.help.usepylon.com/articles/3726859998-understanding-data-types-in-flow)
- [System, project and organisation level requirements](https://flow-engineering-knowledge-base.help.usepylon.com/articles/8111217033-system-project-and-organization-level-requirements)
- [Requirement statement automation](https://flow-engineering-knowledge-base.help.usepylon.com/articles/6615308100-requirement-statement-automation)
- [Adding custom fields](https://flow-engineering-knowledge-base.help.usepylon.com/articles/2216831633-adding-custom-fields)
- [Requirement configurations](https://flow-engineering-knowledge-base.help.usepylon.com/articles/4270141669-requirement-configurations)
- [Requirement configuration branches](https://flow-engineering-knowledge-base.help.usepylon.com/articles/2313057595-requirement-configuration-branches)
- [Creating a derived requirement](https://flow-engineering-knowledge-base.help.usepylon.com/articles/6446106463-creating-a-derived-requirement)
- [Cross-project cross-links](https://flow-engineering-knowledge-base.help.usepylon.com/articles/5811747844-cross-project-cross-links)
- [The review process](https://flow-engineering-knowledge-base.help.usepylon.com/articles/1207468878-the-review-process)
- [Suspect workflow](https://flow-engineering-knowledge-base.help.usepylon.com/articles/1241358509-suspect-workflow-video)
- [Importing requirements into Flow](https://flow-engineering-knowledge-base.help.usepylon.com/articles/8354822666-importing-your-requirements-into-flow)
- [Exporting data out of Flow](https://flow-engineering-knowledge-base.help.usepylon.com/articles/7756985613-exporting-your-data-out-of-flow)
- [Risks view](https://flow-engineering-knowledge-base.help.usepylon.com/articles/1043610898-risks-view)

### Systems & architecture

- [Navigating to your system](https://flow-engineering-knowledge-base.help.usepylon.com/articles/9686432148-navigating-to-your-system)
- [Architecture diagrams](https://flow-engineering-knowledge-base.help.usepylon.com/articles/5595908160-architecture-diagrams)
- [Connecting your first model](https://flow-engineering-knowledge-base.help.usepylon.com/articles/7510826612-connecting-your-first-model)
- [Calculations](https://flow-engineering-knowledge-base.help.usepylon.com/articles/7328235826-calculations)
- [Roll-ups](https://flow-engineering-knowledge-base.help.usepylon.com/articles/6959463456-roll-ups)

### Test management

- [Creating test cases](https://flow-engineering-knowledge-base.help.usepylon.com/articles/7830200467-creating-test-cases)
- [Creating test plans](https://flow-engineering-knowledge-base.help.usepylon.com/articles/2666677405-creating-test-plans)
- [Managing iterations in Flow](https://flow-engineering-knowledge-base.help.usepylon.com/articles/6798941534-managing-iterations-in-flow)

### Views & documents

- [Customising views](https://flow-engineering-knowledge-base.help.usepylon.com/articles/9903628878-customizing-views)
- [Tables in text fields](https://flow-engineering-knowledge-base.help.usepylon.com/articles/2315968810-tables-in-text-fields)
- [File versioning in documents](https://flow-engineering-knowledge-base.help.usepylon.com/articles/9906528812-file-versioning-in-documents)
- [Baselines](https://flow-engineering-knowledge-base.help.usepylon.com/articles/5339910481-baselines)
- [Restore](https://flow-engineering-knowledge-base.help.usepylon.com/articles/4916996982-restore)
- [Subscribing to change notifications](https://flow-engineering-knowledge-base.help.usepylon.com/articles/3625419437-subscribing-to-change-notifications)

### Integrations

- [Jira integration](https://flow-engineering-knowledge-base.help.usepylon.com/articles/5207848440-jira)
- [Epsilon3 integration](https://flow-engineering-knowledge-base.help.usepylon.com/articles/8769027142-epsilon3)
- [Python (beta)](https://flow-engineering-knowledge-base.help.usepylon.com/articles/7397708578-python-%28beta%29)
- [Using the Flow API with Python](https://flow-engineering-knowledge-base.help.usepylon.com/articles/2441602458-using-the-flow-api-with-python)

## IMPORTANT: Security rules

This repository is public during the trial phase. You MUST:

1. Never include org aliases, project aliases, requirement IDs, user names, or any project-specific identifiers in any file you create or modify in this repo.
2. Never suggest committing `.env` files, tokens, or credentials.
3. Never paste raw API responses that contain user data, project names, or internal identifiers into files that could be committed.
4. Treat all Flow content (requirement text, project names, system names) as potentially sensitive - do not include it in commits, READMEs, or any tracked file.
5. If the user asks you to save Flow data to a file, make sure that file is gitignored before proceeding.

If in doubt about whether something is safe to commit, do not commit it and ask the user.
