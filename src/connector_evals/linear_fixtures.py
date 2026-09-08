"""Linear fixture definitions + one-time seeding.

Linear workspaces are private (no public data to point read-only tasks at), so
tasks read a static fixture team seeded once into the user's own workspace via
`connector-evals seed linear` - not per trial, which would race parallel trials
and burn the shared 2,500 req/h API-key limit.

Everything managed lives inside one dedicated team (FIXTURES["team"]). The
free plan caps the workspace at one team (teamCreate returns FORBIDDEN), so
the seeder adopts the workspace's sole team by renaming it - use a dedicated
eval workspace, not a real one. A team label named
`connector-evals-manifest-<hash>` records which fixture version the workspace
holds. Linear cells' setup.sh compares it against LINEAR_FIXTURES_HASH
(computed from FIXTURES here, exported by the run CLI) and aborts the trial
with a reseed hint on mismatch. Only data changes churn the hash; refactoring
the seeding logic does not.

Design constraints (learned the hard way, keep in mind when editing):
- Issue identifiers (FLEET-N) churn on reseed - the counter never resets, so
  no task fact may reference one. Titles only.
- createdAt/completedAt are stamped at seed time - no facts on them.
- Cycles auto-roll and can't be pinned; single-member workspace rules out
  assignee facts.
- Label names are unique workspace-wide case-insensitively (default workspace
  'Bug' blocks a team 'bug'); the seeder resolves labels case-insensitively.
- Custom workflow states are created if missing and never deleted (archiving
  a state that ever held issues is messy); states are matched by name.

Stdlib-only (urllib) so the seeder needs no extra deps.
"""

import hashlib
import json
import urllib.request

GRAPHQL_URL = "https://api.linear.app/graphql"
MANIFEST_PREFIX = "connector-evals-manifest-"

# 80 near-identical backlog chores; exactly one 'security' needle hides among
# them (tasks/linear-backlog-count-needle). MCP list_issues defaults to 50
# per page (max 250), so a correct Backlog count requires paginating or
# raising the limit.
_CHORES = [
    {
        "title": f"Rotate credentials for scraper batch {i:03d}",
        "description": "Scheduled credential rotation for this scraper batch.",
        "state": "Backlog",
        "priority": 4,
        "labels": ["chore"],
    }
    for i in range(1, 81)
]
_NEEDLE = {
    "title": "Audit proxy credentials for leaked tokens",
    "description": "One-off audit after the vendor security bulletin.",
    "state": "Backlog",
    "priority": 3,
    "labels": ["security"],
}

# Priorities: 1 urgent, 2 high, 3 medium, 4 low. States are the default
# workflow of a new team (Backlog / Todo / In Progress / Done / Canceled)
# plus the custom 'In Review' seeded below, matched by name at seed time.
# Verifier judges assert facts from this data, so any edit here means
# updating the affected judge.toml KNOWN FACTS too. Facts locked by
# tests/test_linear_fixtures.py:
# - 4 open bug-labeled issues, 2 urgent (linear-bug-triage); new issues must
#   never carry the 'bug' label.
# - 85 Backlog issues, one 'security' needle (linear-backlog-count-needle).
# - 'Ship crawler v2' blocked by 3 issues, 2 still open
#   (linear-release-blockers).
# - Project 'Crawler v2 Launch': 3 Done issues, earliest milestone 'Vendor
#   selected' (linear-project-status); latest update offTrack over the
#   unsigned vendor contract (linear-health-update).
# - Vendor thread ends on NimbusProxy at $2.40/GB (linear-vendor-decision).
# - started-type states: In Progress + In Review (linear-review-states).
# - Fleet Runbook: rotation every 6 hours, halt via FLEET_HALT=1
#   (linear-fleet-runbook).
FIXTURES: dict = {
    # Not "Scraper Ops"/"SCR": that name+key sits in the workspace's trash
    # (a teamCreate half-succeeded before free-plan limit enforcement) and
    # trashed teams keep their identifiers while being invisible to the API.
    "team": {"name": "Scraper Fleet", "key": "FLEET"},
    "labels": ["bug", "infra", "enhancement", "chore", "security"],
    "workflow_states": [{"name": "In Review", "type": "started", "color": "#26b5ce"}],
    "projects": [
        {
            "name": "Crawler v2 Launch",
            "description": "Migrate the scraper fleet to the v2 crawler runtime.",
            "target_date": "2026-12-15",
            "milestones": [
                {"name": "Vendor selected", "target_date": "2026-09-30"},
                {"name": "Staged rollout", "target_date": "2026-10-31"},
                {"name": "Full migration", "target_date": "2026-11-30"},
            ],
            # Seeded in order; the last one is the newest update.
            "updates": [
                {
                    "health": "onTrack",
                    "body": "Kickoff complete. Base image work started and the "
                    "migration steps are scoped.",
                },
                {
                    "health": "offTrack",
                    "body": "Off track: the proxy vendor contract is still unsigned, "
                    "which puts the staged rollout at risk. Migration work "
                    "continues in parallel.",
                },
            ],
            "documents": [
                {
                    "title": "Fleet Runbook",
                    "content": (
                        "Operational guide for the scraper fleet.\n\n"
                        "## Proxy credentials\n"
                        "- Proxy credential rotation runs automatically every 6 hours.\n"
                        "- Manual rotation: run `fleet rotate --all` from the ops box.\n\n"
                        "## Emergency stop\n"
                        "- Set the environment variable FLEET_HALT=1 to halt the whole "
                        "fleet; scrapers check it before each batch.\n"
                        "- Page the on-call before halting during business hours.\n\n"
                        "## Dashboards\n"
                        "- Run stats live in the ops dashboard; alerts fire after two "
                        "consecutive failed runs.\n"
                    ),
                }
            ],
        }
    ],
    "issues": [
        {
            "title": "amazon-crawler hits captcha wall on product pages",
            "description": "Captcha rate jumped to 40% on category crawls; runs stall.",
            "state": "In Progress",
            "priority": 1,
            "labels": ["bug"],
        },
        {
            "title": "jobs-radar pagination drops last page",
            "description": "Result count is short by up to 20 items per query.",
            "state": "Todo",
            "priority": 2,
            "labels": ["bug"],
        },
        {
            "title": "Rotate proxy pool for google-maps-scraper",
            "description": "Current pool is 60% burned; rotate before next sweep.",
            "state": "Todo",
            "priority": 2,
            "labels": ["infra"],
        },
        {
            "title": "news-harvester misses paywalled articles",
            "description": "Paywalled outlets return teaser text only.",
            "state": "Backlog",
            "priority": 3,
            "labels": ["bug"],
        },
        {
            "title": "Upgrade scraper runtime to Node 24",
            "description": "Node 20 EOL; bump base image and re-test all actors.",
            "state": "Backlog",
            "priority": 3,
            "labels": ["infra"],
        },
        {
            "title": "forum-archiver: dedupe reposted threads",
            "description": "Same thread archived multiple times when cross-posted.",
            "state": "Backlog",
            "priority": 4,
            "labels": ["enhancement"],
        },
        {
            "title": "Dashboard for scraper run stats",
            "description": "Single page with per-scraper success rate and row counts.",
            "state": "Todo",
            "priority": 3,
            "labels": ["enhancement"],
        },
        {
            "title": "google-maps-scraper returns stale opening hours",
            "description": "Opening hours lag reality by weeks; cache layer suspected.",
            "state": "In Progress",
            "priority": 1,
            "labels": ["bug"],
        },
        {
            "title": "Fix flaky retry logic in fetch queue",
            "description": "Retries fired twice for the same URL under load.",
            "state": "Done",
            "priority": 2,
            "labels": ["bug"],
        },
        {
            "title": "Add alerting when a run fails twice",
            "description": "Page the on-call after two consecutive failed runs.",
            "state": "Todo",
            "priority": 2,
            "labels": ["infra"],
        },
        {
            "title": "amazon-crawler memory leak on large categories",
            "description": "Superseded by the runtime upgrade; closing.",
            "state": "Canceled",
            "priority": 3,
            "labels": ["bug"],
        },
        {
            "title": "Document scraper onboarding checklist",
            "description": "Steps to add a new scraper to the fleet.",
            "state": "Backlog",
            "priority": 4,
            "labels": ["enhancement"],
        },
        # --- Crawler v2 Launch project ---
        {
            "title": "Sign proxy vendor contract",
            "description": "Legal review done; waiting on vendor countersignature.",
            "state": "In Progress",
            "priority": 2,
            "labels": ["infra"],
            "project": "Crawler v2 Launch",
        },
        {
            "title": "Load-test proxy failover",
            "description": "Verify failover holds at 3x normal request volume.",
            "state": "Todo",
            "priority": 2,
            "labels": ["infra"],
            "project": "Crawler v2 Launch",
        },
        {
            "title": "Update scraper base image for v2",
            "description": "New base image built and rolled to staging.",
            "state": "Done",
            "priority": 3,
            "labels": ["infra"],
            "project": "Crawler v2 Launch",
        },
        {
            "title": "Ship crawler v2",
            "description": "Cut the v2 release once all blockers clear.",
            "state": "Todo",
            "priority": 1,
            "labels": ["infra"],
            "project": "Crawler v2 Launch",
        },
        {
            "title": "Migrate google-maps-scraper to v2",
            "description": "Port config and re-run the golden-output suite.",
            "state": "In Review",
            "priority": 3,
            "labels": [],
            "project": "Crawler v2 Launch",
        },
        {
            "title": "Migrate amazon-crawler to v2",
            "description": "Blocked on captcha handling parity.",
            "state": "Todo",
            "priority": 3,
            "labels": [],
            "project": "Crawler v2 Launch",
        },
        {
            "title": "Write v2 rollback plan",
            "description": "Documented; rollback is re-deploying the v1 image tag.",
            "state": "Done",
            "priority": 2,
            "labels": [],
            "project": "Crawler v2 Launch",
        },
        {
            "title": "Benchmark v2 vs v1 throughput",
            "description": "v2 is 1.8x faster on the standard corpus.",
            "state": "Done",
            "priority": 3,
            "labels": [],
            "project": "Crawler v2 Launch",
        },
        {
            "title": "Spike: evaluate residential proxy pools",
            "description": "Out of budget for this quarter; revisit later.",
            "state": "Canceled",
            "priority": 4,
            "labels": [],
            "project": "Crawler v2 Launch",
        },
        {
            "title": "Announce v2 to data consumers",
            "description": "Changelog entry + email to downstream teams.",
            "state": "Todo",
            "priority": 4,
            "labels": ["enhancement"],
            "project": "Crawler v2 Launch",
        },
        # --- vendor decision thread ---
        {
            "title": "Choose proxy vendor for the fleet",
            "description": "Pick the proxy vendor for the v2 rollout. Decision in comments.",
            "state": "Done",
            "priority": 2,
            "labels": ["infra"],
            "comments": [
                "Candidates: NimbusProxy ($2.40/GB), GridRelay ($4.10/GB), "
                "HydraNet ($1.90/GB).",
                "HydraNet is the cheapest, leaning that way.",
                "HydraNet failed the geo-coverage test - only 40 countries. "
                "Dropping it.",
                "Proposal: go with GridRelay, best reliability record of the three.",
                "Finance pushback: GridRelay at $4.10/GB doubles our proxy budget. "
                "Please reconsider.",
                "Decision: NimbusProxy at $2.40/GB. Contract to be signed this "
                "quarter.",
            ],
        },
        *_CHORES[:40],
        _NEEDLE,
        *_CHORES[40:],
    ],
    # `issue` blocks `blocks` (issueRelationCreate: issueId blocks relatedIssueId).
    "relations": [
        {"type": "blocks", "issue": "Sign proxy vendor contract", "blocks": "Ship crawler v2"},
        {"type": "blocks", "issue": "Load-test proxy failover", "blocks": "Ship crawler v2"},
        {"type": "blocks", "issue": "Update scraper base image for v2", "blocks": "Ship crawler v2"},
    ],
}


def fixtures_hash() -> str:
    payload = json.dumps(FIXTURES, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:12]


def manifest_label() -> str:
    return MANIFEST_PREFIX + fixtures_hash()


def _gql(api_key: str, query: str, variables: dict | None = None) -> dict:
    req = urllib.request.Request(
        GRAPHQL_URL,
        method="POST",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": api_key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    if data.get("errors"):
        raise RuntimeError(f"Linear GraphQL error: {data['errors']}")
    return data["data"]


def _ensure_team(api_key: str, log) -> str:
    key = FIXTURES["team"]["key"]
    teams = _gql(api_key, "{ teams { nodes { id key name } } }")["teams"]["nodes"]
    for team in teams:
        if team["key"] == key:
            return team["id"]
    # Free plan caps the workspace at one team (teamCreate returns FORBIDDEN),
    # so adopt the sole existing team by renaming it.
    if len(teams) != 1:
        raise RuntimeError(
            f"no team with key '{key}' and {len(teams)} teams in the workspace; "
            f"rename one to key '{key}' manually or remove the extras"
        )
    team = teams[0]
    _gql(
        api_key,
        "mutation($id: String!, $input: TeamUpdateInput!) "
        "{ teamUpdate(id: $id, input: $input) { success } }",
        {"id": team["id"], "input": {"name": FIXTURES["team"]["name"], "key": key}},
    )
    log(
        f"renamed team {team['name']} ({team['key']}) -> "
        f"{FIXTURES['team']['name']} ({key})"
    )
    return team["id"]


def _ensure_workflow_states(api_key: str, team_id: str, log) -> dict[str, str]:
    """name -> id for the team's states, creating missing custom ones."""
    states = {
        n["name"]: n["id"]
        for n in _gql(
            api_key,
            "query($id: String!) { team(id: $id) { states { nodes { id name } } } }",
            {"id": team_id},
        )["team"]["states"]["nodes"]
    }
    for spec in FIXTURES["workflow_states"]:
        if spec["name"] in states:
            continue
        created = _gql(
            api_key,
            "mutation($input: WorkflowStateCreateInput!) "
            "{ workflowStateCreate(input: $input) { workflowState { id } } }",
            {"input": {**spec, "teamId": team_id}},
        )["workflowStateCreate"]["workflowState"]
        states[spec["name"]] = created["id"]
        log(f"created workflow state: {spec['name']} ({spec['type']})")
    return states


def _all_labels(api_key: str) -> dict[str, str]:
    """Workspace + team labels, name -> id. Label names are unique across the
    whole workspace case-insensitively (the default workspace 'Bug' label
    blocks a team-level 'bug'), so fixture labels are resolved against
    everything and matched case-insensitively."""
    nodes = _gql(api_key, "{ issueLabels(first: 250) { nodes { id name } } }")[
        "issueLabels"
    ]["nodes"]
    return {n["name"]: n["id"] for n in nodes}


def _team_issues(api_key: str, team_id: str) -> list[dict]:
    issues: list[dict] = []
    cursor = None
    while True:
        data = _gql(
            api_key,
            "query($id: String!, $after: String) { team(id: $id) "
            "{ issues(first: 250, after: $after) "
            "{ nodes { id identifier } pageInfo { hasNextPage endCursor } } } }",
            {"id": team_id, "after": cursor},
        )["team"]["issues"]
        issues.extend(data["nodes"])
        if not data["pageInfo"]["hasNextPage"]:
            return issues
        cursor = data["pageInfo"]["endCursor"]


def _delete_stale(api_key: str, team_id: str, labels: dict[str, str], log) -> None:
    for issue in _team_issues(api_key, team_id):
        _gql(
            api_key,
            "mutation($id: String!) { issueDelete(id: $id) { success } }",
            {"id": issue["id"]},
        )
    log("deleted stale fixture issues")
    for project in FIXTURES["projects"]:
        found = _gql(
            api_key,
            "query($name: String!) { projects(filter: { name: { eq: $name } }) "
            "{ nodes { id } } }",
            {"name": project["name"]},
        )["projects"]["nodes"]
        for node in found:
            _gql(
                api_key,
                "mutation($id: String!) { projectDelete(id: $id) { success } }",
                {"id": node["id"]},
            )
            log(f"deleted stale fixture project: {project['name']}")
    for name, label_id in labels.items():
        if name.startswith(MANIFEST_PREFIX):
            _gql(
                api_key,
                "mutation($id: String!) { issueLabelDelete(id: $id) { success } }",
                {"id": label_id},
            )
            log(f"deleted stale manifest label: {name}")


def _create_project(api_key: str, team_id: str, project: dict, log) -> str:
    created = _gql(
        api_key,
        "mutation($input: ProjectCreateInput!) "
        "{ projectCreate(input: $input) { project { id } } }",
        {
            "input": {
                "name": project["name"],
                "description": project["description"],
                "teamIds": [team_id],
                "targetDate": project["target_date"],
            }
        },
    )["projectCreate"]["project"]
    for ms in project["milestones"]:
        _gql(
            api_key,
            "mutation($input: ProjectMilestoneCreateInput!) "
            "{ projectMilestoneCreate(input: $input) { projectMilestone { id } } }",
            {
                "input": {
                    "name": ms["name"],
                    "projectId": created["id"],
                    "targetDate": ms["target_date"],
                }
            },
        )
    for update in project["updates"]:
        _gql(
            api_key,
            "mutation($input: ProjectUpdateCreateInput!) "
            "{ projectUpdateCreate(input: $input) { projectUpdate { id } } }",
            {"input": {"projectId": created["id"], **update}},
        )
    for doc in project["documents"]:
        _gql(
            api_key,
            "mutation($input: DocumentCreateInput!) "
            "{ documentCreate(input: $input) { document { id } } }",
            {"input": {"projectId": created["id"], **doc}},
        )
    log(
        f"created fixture project: {project['name']} "
        f"({len(project['milestones'])} milestones, {len(project['updates'])} "
        f"updates, {len(project['documents'])} documents)"
    )
    return created["id"]


def seed_linear(api_key: str, log=print) -> bool:
    """Idempotent reseed: no-op when the manifest label hash matches, else
    delete every issue in the fixture team plus managed projects and stale
    manifest labels, and recreate from FIXTURES. Returns True if it wrote
    anything."""
    team_id = _ensure_team(api_key, log)
    labels = _all_labels(api_key)
    if manifest_label() in labels:
        log(f"linear fixtures up to date ({manifest_label()})")
        return False

    _delete_stale(api_key, team_id, labels, log)
    states = _ensure_workflow_states(api_key, team_id, log)

    labels = _all_labels(api_key)
    by_lower = {name.lower(): label_id for name, label_id in labels.items()}
    # The manifest label is deliberately NOT created here: it lands last, so a
    # seeder crash mid-way leaves no manifest and the next run reseeds.
    for name in FIXTURES["labels"]:
        if name.lower() in by_lower:
            labels[name] = by_lower[name.lower()]
            continue
        created = _gql(
            api_key,
            "mutation($input: IssueLabelCreateInput!) "
            "{ issueLabelCreate(input: $input) { issueLabel { id } } }",
            {"input": {"name": name, "teamId": team_id}},
        )["issueLabelCreate"]["issueLabel"]
        labels[name] = created["id"]

    project_ids = {
        p["name"]: _create_project(api_key, team_id, p, log)
        for p in FIXTURES["projects"]
    }

    issue_ids: dict[str, str] = {}
    for issue in FIXTURES["issues"]:
        payload = {
            "teamId": team_id,
            "title": issue["title"],
            "description": issue["description"],
            "stateId": states[issue["state"]],
            "priority": issue["priority"],
            "labelIds": [labels[name] for name in issue["labels"]],
        }
        if issue.get("project"):
            payload["projectId"] = project_ids[issue["project"]]
        created = _gql(
            api_key,
            "mutation($input: IssueCreateInput!) "
            "{ issueCreate(input: $input) { issue { id identifier } } }",
            {"input": payload},
        )["issueCreate"]["issue"]
        issue_ids[issue["title"]] = created["id"]
        for body in issue.get("comments", ()):
            _gql(
                api_key,
                "mutation($input: CommentCreateInput!) "
                "{ commentCreate(input: $input) { comment { id } } }",
                {"input": {"issueId": created["id"], "body": body}},
            )
    log(f"created {len(FIXTURES['issues'])} fixture issues")

    for rel in FIXTURES["relations"]:
        _gql(
            api_key,
            "mutation($input: IssueRelationCreateInput!) "
            "{ issueRelationCreate(input: $input) { issueRelation { id } } }",
            {
                "input": {
                    "issueId": issue_ids[rel["issue"]],
                    "relatedIssueId": issue_ids[rel["blocks"]],
                    "type": rel["type"],
                }
            },
        )
    log(f"created {len(FIXTURES['relations'])} issue relations")
    _gql(
        api_key,
        "mutation($input: IssueLabelCreateInput!) "
        "{ issueLabelCreate(input: $input) { issueLabel { id } } }",
        {"input": {"name": manifest_label(), "teamId": team_id}},
    )
    log(f"created manifest label: {manifest_label()}")
    return True
