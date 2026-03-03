# flow-trial

This repository lets you interact with [Flow](https://flowengineering.com) - our requirements management tool - using the AI assistant **Claude Code**.

Instead of clicking through the Flow web interface, you can type plain English instructions and Claude will handle the API calls for you. You can also run a set of professional engineering workflows directly from the command line.

**What you can do:**

- Create, update, and query requirements
- Import requirements from Excel spreadsheets
- Run INCOSE quality checks across your entire project
- Generate draft test cases from "shall" statements
- Analyse traceability gaps and generate a requirements-to-systems matrix
- Assess the impact of a change before making it
- Generate Interface Control Documents (ICDs) from tagged requirements
- Sync numeric values from analysis models into Flow

---

## Setup

### 1. Download this repo

Clone using GitHub Desktop or `git clone`.

### 2. Install Python dependencies

```cmd
pip install -r requirements.txt
```

This installs `openpyxl` (Excel reading) and `PyYAML` (config files).

### 3. Set up your Flow credentials

You need a personal API token from Flow so Claude can act on your behalf.

**Get your token:**

1. Log in to Flow at [app.flowengineering.com](https://app.flowengineering.com)
2. Click your profile icon (top right) > **Settings** > **API Tokens**
3. Create a new token and copy it somewhere safe

**Create your credentials file:**

```cmd
copy .env.example .env
notepad .env
```

Replace the placeholder values:

```text
export FLOW_REFRESH_TOKEN=paste-your-token-here
export FLOW_ORG=your-organisation-alias
export FLOW_PROJECT=your-project-alias
```

The **org alias** and **project alias** are the short names in the Flow URL:
`https://app.flowengineering.com/org/`**your-org**`/project/`**your-project**

> **Important:** Never share your `.env` file. It is automatically excluded from git.

### 4. Verify your setup

```cmd
python scripts/flow_cli.py auth
```

You should see `{"status": "ok", ...}`.

---

## Using Claude Code (conversational)

In Claude Code, type `/flow` followed by what you want:

```text
/flow list my requirements
```

```text
/flow check the quality of all my requirements and show fix hints
```

```text
/flow import requirements from flow-test.xlsx - preview first
```

```text
/flow generate test cases for all requirements
```

```text
/flow show me the traceability gaps
```

Claude figures out the right commands and presents results in a readable format.

---

## Using the command line directly

All commands use:

```cmd
python scripts/flow_cli.py <command> [options]
```

| What you want to do | Command |
| ------------------- | ------- |
| Test your credentials | `flow_cli.py auth` |
| List all requirements | `flow_cli.py req list --all` |
| Preview an Excel import | `flow_cli.py import file.xlsx --preview` |
| Run quality checks | `flow_cli.py quality --fix-hints` |
| Generate test case drafts | `flow_cli.py testgen` |
| Find unallocated requirements | `flow_cli.py trace gaps` |
| See what a change affects | `flow_cli.py impact req <id>` |
| List your backups | `flow_cli.py backup list` |

See the [quickstart guide](docs/user-guide/00-quickstart.md) for a step-by-step walkthrough.

---

## User guides

Detailed guides for each capability are in [docs/user-guide/](docs/user-guide/):

- [Setup](docs/user-guide/01-setup.md)
- [Importing requirements](docs/user-guide/02-importing-requirements.md)
- [Quality review](docs/user-guide/03-quality-review.md)
- [Test case generation](docs/user-guide/04-test-cases.md)
- [Traceability analysis](docs/user-guide/05-traceability.md)
- [Change impact analysis](docs/user-guide/06-change-impact.md)
- [ICD generation](docs/user-guide/07-icd-generation.md)
- [Design values](docs/user-guide/08-design-values.md)

---

## Need help?

- **Flow itself** (how to use the tool, set up integrations): [Flow knowledge base](https://flow-engineering-knowledge-base.help.usepylon.com/)
- **Claude Code** (the AI assistant): [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code)
