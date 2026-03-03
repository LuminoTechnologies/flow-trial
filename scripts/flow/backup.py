"""Backup and restore for Flow API operations.

Every write command snapshots affected resources before modifying them.
Backups are stored locally in backups/ and are gitignored.
"""

import json
import os
import sys
from datetime import datetime

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
BACKUPS_DIR = os.path.join(_REPO_ROOT, "backups")


def _ensure_backups_dir():
    os.makedirs(BACKUPS_DIR, exist_ok=True)


def create_backup(operation, data, manifest=None):
    """Save a snapshot before a write operation.

    Args:
        operation: short string label, e.g. 'req-update', 'import'
        data: dict or list of the pre-change state
        manifest: optional dict describing what will be changed

    Returns:
        backup_id (str) - use this to restore later
    """
    _ensure_backups_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_id = f"{timestamp}_{operation}"
    backup_dir = os.path.join(BACKUPS_DIR, backup_id)
    os.makedirs(backup_dir, exist_ok=True)

    with open(os.path.join(backup_dir, "snapshot.json"), "w") as f:
        json.dump(data, f, indent=2)

    if manifest:
        with open(os.path.join(backup_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)

    print(f"  Backup saved: {backup_id}", flush=True)
    return backup_id


def list_backups():
    """Return a list of backup IDs sorted newest-first."""
    _ensure_backups_dir()
    entries = []
    for name in os.listdir(BACKUPS_DIR):
        if os.path.isdir(os.path.join(BACKUPS_DIR, name)):
            entries.append(name)
    return sorted(entries, reverse=True)


def load_backup(backup_id):
    """Load snapshot data from a backup."""
    backup_dir = os.path.join(BACKUPS_DIR, backup_id)
    snapshot_path = os.path.join(backup_dir, "snapshot.json")
    manifest_path = os.path.join(backup_dir, "manifest.json")
    if not os.path.exists(snapshot_path):
        print(f"ERROR: Backup not found: {backup_id}", file=sys.stderr)
        sys.exit(1)
    with open(snapshot_path) as f:
        snapshot = json.load(f)
    manifest = None
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)
    return snapshot, manifest
