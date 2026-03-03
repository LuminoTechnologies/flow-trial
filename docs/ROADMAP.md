# Flow Integration Roadmap

## Implemented (current sprint)

| Capability | Command | Status |
|------------|---------|--------|
| Authentication | `flow auth` | Done |
| Requirement CRUD | `flow req list/get/create/update` | Done |
| Traceability links | `flow link req-req/req-tc` | Done |
| Backup/restore | `flow backup list`, `flow restore <id>` | Done |
| Excel import | `flow import <file.xlsx>` | Done |
| Quality review (INCOSE rules) | `flow quality` | Done |
| Test case generation | `flow testgen` | Done |
| Traceability analysis | `flow trace systems/gaps/matrix/allocate/suggest` | Done |
| Change impact analysis | `flow impact req/system/diff` | Done |
| ICD generation | `flow icd list/generate` | Done |
| Design values model awareness | `flow models list/sync` | Done |

## Planned (future sprints)

| Capability | Notes | Priority |
|------------|-------|----------|
| Private Flow instance migration | Update BASE_URL when trial converts | High |
| GitHub Actions CI integration | Run quality checks automatically on push | High |
| Baseline comparison | Diff two Flow baselines (no API support yet) | Medium |
| Word/PDF ICD export | Convert markdown ICD via pandoc | Medium |
| Two-way Excel sync | Detect spreadsheet changes and push deltas only | Medium |
| MCP server | Expose Flow operations as MCP tool for desktop app | Low |
| Permissions management | Bulk-add team members when project goes live | Low |

## Out of scope

- Setting up GitHub/Jira integrations (requires Flow UI)
- Configuring architecture diagram views (requires Flow UI)
- Managing baselines (no API support)
