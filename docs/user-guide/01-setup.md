# Setup Guide

## Prerequisites

- Python 3.9 or later
- A Flow account with API access (refresh token)

## Installation

1. Clone the repository and navigate to the project root.

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create your credentials file:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and fill in your `FLOW_REFRESH_TOKEN`, `FLOW_ORG`, and `FLOW_PROJECT` values.

4. Verify your setup:
   ```bash
   python scripts/flow_cli.py auth
   ```
   You should see `{"status": "ok", "accessToken": "..."}`.

## Command reference

All commands use the same entrypoint:

```bash
python scripts/flow_cli.py <command> [subcommand] [options]
```

Run `python scripts/flow_cli.py --help` to see all available commands.

## Security notes

- Never commit `.env` or any file containing your refresh token.
- The `backups/` and `outputs/` directories are gitignored - they may contain project data.
- The repository is public during the trial phase. Do not include project identifiers in committed files.

## Troubleshooting

**`ERROR: FLOW_REFRESH_TOKEN environment variable is not set`**
Create `.env` by copying `.env.example` and filling in your credentials.

**`ERROR: Token exchange failed (401)`**
Your refresh token has expired. Generate a new one in the Flow web app under Settings > API.

**`ModuleNotFoundError: No module named 'openpyxl'`**
Run `pip install -r requirements.txt`.
