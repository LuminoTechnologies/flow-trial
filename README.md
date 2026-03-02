# flow-trial

This repository gives you a way to interact with [Flow](https://flowengineering.com) - our requirements management tool - using an AI assistant called **Claude Code**.

Instead of clicking through the Flow web interface, you can type plain English instructions like:

> "List all requirements in my project"
> "Create a new requirement called REQ-042"
> "Link requirement 12 to test case 7"

...and Claude will do it for you.

---
## Download this repo

Clone this repository using GitHub Desktop.

## Set up your Flow credentials

You need a personal API token from Flow so Claude can act on your behalf.

### Get your token from Flow

1. Log in to Flow at [app.flowengineering.com](https://app.flowengineering.com)
2. Click your profile icon (top right)
3. Go to **Settings** or **API Tokens**
4. Create a new token and copy it somewhere safe

### Create your credentials file

In your `flow-trial` folder, copy the example file:

```cmd
copy .env.example .env
```

Now open `.env` in Notepad:

```cmd
notepad .env
```

Replace the placeholder values with your real ones:

```text
export FLOW_REFRESH_TOKEN=paste-your-token-here
export FLOW_ORG=your-organisation-alias
export FLOW_PROJECT=your-project-alias
```

The **org alias** and **project alias** are the short names that appear in the Flow URL:
`https://app.flowengineering.com/org/`**your-org**`/project/`**your-project**

Save and close Notepad.

> **Important:** Never share your `.env` file or send it to anyone. It contains your personal credentials. It is automatically excluded from git so it can never be accidentally uploaded.

---

## Start using Claude

In Claude Code (either in the Desktop UI, or the terminal if installed). Type `/flow` followed by what you want to do. For example:

```text
/flow list my requirements
```

```text
/flow create a requirement called "The system shall operate at 28V DC"
```

```text
/flow show me requirement 42
```

Claude will figure out the right API calls and show you the results in a readable format.


## Need help?

- **Flow itself** (how to use the tool, set up integrations): [Flow knowledge base](https://flow-engineering-knowledge-base.help.usepylon.com/)
- **Claude Code** (the AI assistant): [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code)
