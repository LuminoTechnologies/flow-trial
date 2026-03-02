# /flow - Interact with the Flow requirements management API

You are helping the user interact with Flow (flowengineering.com) via the REST API v1.

## Full API capabilities reference

See [docs/flow-api-capabilities.md](../../docs/flow-api-capabilities.md) for a complete index of every read and write operation available. The Python helper implements a commonly-used subset; for anything not yet in the helper, you can call the API directly using curl or extend the script.

If a user asks for something that does not appear in the capabilities document:

1. Check the Flow changelog at [flow-engineering.productlane.com/changelog](https://flow-engineering.productlane.com/changelog) for any mention of the feature.
2. If the changelog suggests it has been added or changed, re-fetch the OpenAPI spec at `https://api.flowengineering.com/rest/v1/openapi.json` and compare it against the current capabilities document.
3. Update `docs/flow-api-capabilities.md` to reflect any new or changed endpoints before proceeding.

## How to call the API

Use the Python helper script via Bash:

```bash
python scripts/flow_api.py <command> [options]
```

The script automatically loads `.env` from the repo root, so no manual setup is needed. It handles token exchange automatically and all output is JSON.

If the script prints `ERROR: FLOW_REFRESH_TOKEN environment variable is not set`, tell the user to create a `.env` file by copying `.env.example` and filling in their credentials - no need to source it.

## Available commands

### Test authentication

```bash
python scripts/flow_api.py auth
```

### List requirements in the default project

```bash
python scripts/flow_api.py req list
python scripts/flow_api.py req list --limit 100
python scripts/flow_api.py req list --after <cursor>   # next page
python scripts/flow_api.py req list --project other-project
```

### Get full detail of a requirement

```bash
python scripts/flow_api.py req get <id>
```

### Create a requirement

```bash
python scripts/flow_api.py req create '{"name": "REQ-001", "description": "The system shall..."}'
```

Multiple at once: pass a JSON array.

### Update a requirement

```bash
python scripts/flow_api.py req update <id> '{"name": "Updated name"}'
```

Only include fields you want to change.

### Link requirement to requirement

```bash
python scripts/flow_api.py link req-req <source-id> parent <target-id>
python scripts/flow_api.py link req-req <source-id> child <target-id>
python scripts/flow_api.py link req-req <source-id> cross <target-id> --target-project other-project
```

Link types: `parent`, `child`, `cross`

### Link requirement to test case

```bash
python scripts/flow_api.py link req-tc <requirement-id> <test-case-id>
```

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
