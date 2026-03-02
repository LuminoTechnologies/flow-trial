# Flow API Capabilities Index

Reference for the `/flow` Claude Code skill. All paths are relative to:
`https://api.flowengineering.com/rest/v1/org/{orgAlias}/project/{projectAlias}/`

`R` = read  `W` = write/create/update  `D` = delete

---

## Authentication

| Op | Endpoint | Description |
|----|----------|-------------|
| W | `POST /auth/exchange` | Exchange refresh token for short-lived access token |

---

## Organisation Members

| Op | Endpoint | Description |
|----|----------|-------------|
| R | `GET /org/{org}/members` | List all organisation members |
| W | `POST /org/{org}/members` | Add or update members (role assignment) |
| D | `DELETE /org/{org}/members/{email}` | Remove a member from the organisation |

---

## Project Setup

| Op | Endpoint | Description |
|----|----------|-------------|
| R | `GET .../members` | List project members |
| W | `POST .../members` | Add or update project members |
| D | `DELETE .../members/{email}` | Remove a project member |
| R | `GET .../configurations` | List project configurations (environments/variants) |
| W | `POST .../configurations` | Create a configuration |
| R | `GET .../requirementTypes` | List available requirement types |
| R | `GET .../requirementStages` | List available requirement stages |
| R | `GET .../testCaseTypes` | List available test case types |
| R | `GET .../testCaseStages` | List available test case stages |

---

## Requirements

### Querying
| Op | Endpoint | Description |
|----|----------|-------------|
| R | `GET .../requirements/paged` | List requirements (paginated; preferred) |
| R | `POST .../requirements/filter` | Filter requirements by custom field values |
| R | `GET .../requirements/organization` | List organisation-level requirements |
| R | `GET .../requirements/project` | List project-level requirements |
| R | `GET .../requirements/withoutSystem` | List requirements not assigned to any system |
| R | `GET .../requirement/{id}` | Get full detail of a single requirement |
| R | `GET .../requirements/customFields` | Get custom field definitions and constraints |

### Creating & Updating
| Op | Endpoint | Description |
|----|----------|-------------|
| W | `POST .../requirements` | Create one or more requirements |
| W | `PATCH .../requirements` | Update fields on one or more requirements |
| W | `PUT .../requirements/value` | Update requirement values (number/range/boolean etc.) |
| W | `PUT .../requirement/{id}/value` | Update value on a single requirement (deprecated) |
| W | `PUT .../requirement/status` | Update requirement status |
| W | `PUT .../requirements/stage` | Bulk update requirement stages |
| W | `PUT .../requirements/importid` | Set import IDs (for external system sync) |
| W | `PATCH .../requirements/customFields` | Update custom field definitions |
| W | `POST .../requirements/customFields/renameOption` | Rename a tag field option |

### Configurations
| Op | Endpoint | Description |
|----|----------|-------------|
| W | `POST .../requirements/configuration` | Add requirements to a configuration |
| D | `DELETE .../requirements/configuration` | Remove requirements from a configuration |

### Traceability Links
| Op | Endpoint | Description |
|----|----------|-------------|
| W | `POST .../requirement/{id}/links/{type}` | Link to another requirement (`parent`/`child`/`cross`) |
| D | `DELETE .../requirement/{id}/links/{type}/{linkedId}` | Remove a requirement-to-requirement link |
| D | `DELETE .../requirement/{id}/links/{type}/cross_project/{project}/{linkedId}` | Remove a cross-project req link |
| R | `GET .../requirement/{id}/testCases` | Get test cases linked to a requirement |
| R | `GET .../requirement/{id}/testPlans` | Get test plans linked to a requirement |

### Jira Integration
| Op | Endpoint | Description |
|----|----------|-------------|
| W | `POST .../requirement/{id}/jiraIssues` | Link a Jira issue to a requirement |
| D | `DELETE .../requirement/{id}/jiraIssues/{jiraId}` | Unlink a Jira issue from a requirement |

### Files & Images
| Op | Endpoint | Description |
|----|----------|-------------|
| W | `POST .../requirement/{id}/uploadFile` | Upload a file attachment to a requirement |
| W | `POST .../requirement/{id}/imageUrl/{fileId}` | Get a pre-signed URL for a requirement image |

### Deleting
| Op | Endpoint | Description |
|----|----------|-------------|
| D | `DELETE .../requirement/{id}` | Delete a requirement |

---

## Test Cases

### Querying
| Op | Endpoint | Description |
|----|----------|-------------|
| R | `GET .../testCases/paged` | List test cases (paginated; preferred) |
| R | `GET .../testCase/{id}` | Get full detail of a single test case |
| R | `GET .../testCase/{id}/links/requirements` | Get requirements linked to a test case |
| R | `GET .../testCases/customFields` | Get test case custom field definitions |

### Creating & Updating
| Op | Endpoint | Description |
|----|----------|-------------|
| W | `POST .../testCases` | Create one or more test cases |
| W | `PATCH .../testCases` | Update fields on one or more test cases |
| W | `PUT .../testCase/{id}/steps` | Replace all steps on a test case |
| W | `PUT .../testCases/stage` | Bulk update test case stages |
| W | `PUT .../testCases/importid` | Set import IDs |
| W | `PATCH .../testCases/customFields` | Update custom field definitions |
| W | `POST .../testCases/customFields/renameOption` | Rename a tag field option |

### Configurations
| Op | Endpoint | Description |
|----|----------|-------------|
| W | `POST .../testCases/configuration` | Add test cases to a configuration |
| D | `DELETE .../testCases/configuration` | Remove test cases from a configuration |

### Jira Integration
| Op | Endpoint | Description |
|----|----------|-------------|
| W | `POST .../testCase/{id}/jiraIssues` | Link a Jira issue to a test case |
| D | `DELETE .../testCase/{id}/jiraIssues/{jiraId}` | Unlink a Jira issue from a test case |

### Deleting
| Op | Endpoint | Description |
|----|----------|-------------|
| D | `DELETE .../testCase/{id}` | Delete a test case |

---

## Test Runs

| Op | Endpoint | Description |
|----|----------|-------------|
| R | `GET .../testCase/{id}/testRuns/paged` | List test runs for a test case (paginated; preferred) |
| W | `POST .../testCase/{id}/testRun` | Create a new test run |
| W | `PATCH .../testCase/{id}/testRun/{runId}` | Update test run result/status |
| W | `PATCH .../testCase/{id}/testRun/{runId}/steps` | Update individual step results in a test run |

---

## Test Plans & Cycles

| Op | Endpoint | Description |
|----|----------|-------------|
| R | `GET .../testPlans/paged` | List test plans (paginated) |
| R | `GET .../testPlan/{id}` | Get a specific test plan |
| W | `POST .../testPlans` | Create test plans |
| W | `PUT .../testPlan/{id}/importid` | Set test plan import ID |
| W | `POST .../testPlan/{id}/testCycle` | Create a test cycle from a test plan |
| R | `GET .../testCycle/{id}` | Get a test cycle with all its runs |

---

## Systems (MBSE hierarchy)

### Querying
| Op | Endpoint | Description |
|----|----------|-------------|
| R | `GET .../systems/paged` | List systems (paginated; preferred) |
| R | `GET .../system/{id}` | Get a specific system |
| R | `GET .../system/{id}/links/requirements` | List requirements in a system |
| R | `GET .../system/{id}/links/testCases` | List test cases in a system |
| R | `GET .../system/{id}/links/testPlans` | List test plans in a system |
| R | `GET .../system/{id}/links/documents` | List documents in a system |

### Creating & Updating
| Op | Endpoint | Description |
|----|----------|-------------|
| W | `POST .../system` | Create a system |
| W | `PUT .../system/{id}` | Update a system |
| W | `PUT .../systems` | Batch update multiple systems |
| W | `POST .../systems/customFields/renameOption` | Rename a system tag field option |

### Links
| Op | Endpoint | Description |
|----|----------|-------------|
| W | `POST .../system/{id}/links/requirements` | Add requirements to a system |
| D | `DELETE .../system/{id}/links/requirement/{reqId}` | Remove a requirement from a system |
| W | `POST .../system/{id}/links/testCases` | Add test cases to a system |
| D | `DELETE .../system/{id}/links/testCase/{tcId}` | Remove a test case from a system |
| W | `POST .../system/{id}/links/testPlans` | Add test plans to a system |
| W | `POST .../system/{id}/links/documents` | Add documents to a system |

### Deleting
| Op | Endpoint | Description |
|----|----------|-------------|
| D | `DELETE .../system/{id}` | Delete a system |

---

## Cross-Project Links

| Op | Endpoint | Description |
|----|----------|-------------|
| W | `PUT .../link/requirementTestCase` | Link requirements to test cases (same project) |
| W | `PUT .../link/requirementTestCase/crossProject` | Link requirements to test cases across projects |
| W | `PUT .../link/testPlanTestCase` | Link test plans to test cases (same project) |
| W | `PUT .../link/testPlanTestCase/crossProject` | Link test plans to test cases across projects |

---

## Documents

| Op | Endpoint | Description |
|----|----------|-------------|
| W | `PUT .../documents/importid` | Set import IDs on documents |

---

## Notes

- Prefer `paged` variants over non-paged list endpoints (non-paged are deprecated).
- The `scripts/flow_api.py` helper currently implements a subset: auth, req list/get/create/update, req-to-req links, req-to-testcase links. Other operations can be called directly via the `api_request()` helper or added as new subcommands.
- All write operations that accept arrays can batch multiple items in a single call.
