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

Stdlib-only (urllib) so the seeder needs no extra deps.
"""

import hashlib
import json
import urllib.request

GRAPHQL_URL = "https://api.linear.app/graphql"
MANIFEST_PREFIX = "connector-evals-manifest-"

# Priorities: 1 urgent, 2 high, 3 medium, 4 low. States are the default
# workflow of a new team (Backlog / Todo / In Progress / Done / Canceled),
# matched by name at seed time. Verifier judges assert facts from these
# issues, so any edit here means updating the affected judge.toml KNOWN
# FACTS too. Open bug-labeled issues: 4 (the Done and Canceled bugs exist to
# force state filtering); urgent among them: amazon-crawler captcha +
# google-maps-scraper stale hours (tasks/linear-bug-triage).
FIXTURES: dict = {
    # Not "Scraper Ops"/"SCR": that name+key sits in the workspace's trash
    # (a teamCreate half-succeeded before free-plan limit enforcement) and
    # trashed teams keep their identifiers while being invisible to the API.
    "team": {"name": "Scraper Fleet", "key": "FLEET"},
    "labels": ["bug", "infra", "enhancement"],
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


def _all_labels(api_key: str) -> dict[str, str]:
    """Workspace + team labels, name -> id. Label names are unique across the
    whole workspace case-insensitively (the default workspace 'Bug' label
    blocks a team-level 'bug'), so fixture labels are resolved against
    everything and matched case-insensitively."""
    nodes = _gql(api_key, "{ issueLabels(first: 250) { nodes { id name } } }")[
        "issueLabels"
    ]["nodes"]
    return {n["name"]: n["id"] for n in nodes}


def seed_linear(api_key: str, log=print) -> bool:
    """Idempotent reseed: no-op when the manifest label hash matches, else
    delete every issue in the fixture team plus stale manifest labels and
    recreate from FIXTURES. Returns True if it wrote anything."""
    team_id = _ensure_team(api_key, log)
    labels = _all_labels(api_key)
    if manifest_label() in labels:
        log(f"linear fixtures up to date ({manifest_label()})")
        return False

    issues = _gql(
        api_key,
        "query($id: String!) { team(id: $id) { issues(first: 250) "
        "{ nodes { id identifier } } } }",
        {"id": team_id},
    )["team"]["issues"]["nodes"]
    for issue in issues:
        _gql(
            api_key,
            "mutation($id: String!) { issueDelete(id: $id) { success } }",
            {"id": issue["id"]},
        )
        log(f"deleted stale fixture issue: {issue['identifier']}")
    for name, label_id in labels.items():
        if name.startswith(MANIFEST_PREFIX):
            _gql(
                api_key,
                "mutation($id: String!) { issueLabelDelete(id: $id) { success } }",
                {"id": label_id},
            )
            log(f"deleted stale manifest label: {name}")

    by_lower = {name.lower(): label_id for name, label_id in labels.items()}
    for name in [*FIXTURES["labels"], manifest_label()]:
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

    states = {
        n["name"]: n["id"]
        for n in _gql(
            api_key,
            "query($id: String!) { team(id: $id) { states { nodes { id name } } } }",
            {"id": team_id},
        )["team"]["states"]["nodes"]
    }
    for issue in FIXTURES["issues"]:
        _gql(
            api_key,
            "mutation($input: IssueCreateInput!) "
            "{ issueCreate(input: $input) { issue { identifier } } }",
            {
                "input": {
                    "teamId": team_id,
                    "title": issue["title"],
                    "description": issue["description"],
                    "stateId": states[issue["state"]],
                    "priority": issue["priority"],
                    "labelIds": [labels[name] for name in issue["labels"]],
                }
            },
        )
        log(f"created fixture issue: {issue['title']}")
    log(f"created manifest label: {manifest_label()}")
    return True
