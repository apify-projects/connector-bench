"""Notion fixture definitions + one-time seeding.

Notion has no public API surface (every call needs an integration token plus
explicit page sharing), so tasks read static fixture pages seeded once into the
user's own workspace via `connector-evals seed notion` - not per trial, which
would race parallel trials on titles and burn the shared 3 req/s token limit.

A manifest page titled `connector-evals-manifest-<hash>` under the parent page
records which fixture version the workspace holds. Notion cells' setup.sh
compares it against NOTION_FIXTURES_HASH (computed from FIXTURES here, exported
by the run CLI) and aborts the trial with a reseed hint on mismatch. Only data
changes churn the hash; refactoring the seeding logic does not.

Stdlib-only (urllib) so the seeder needs no extra deps.
"""

import hashlib
import json
import urllib.request

NOTION_VERSION = "2022-06-28"
MANIFEST_PREFIX = "connector-evals-manifest-"

_SCRAPERS = [
    "google-maps-scraper",
    "amazon-crawler",
    "news-harvester",
    "jobs-radar",
    "forum-archiver",
]

# 154 domains; the needle sits past the first 100 so a correct answer requires
# paginating blocks/children (tasks/notion-blocklist-needle).
_BLOCKLIST_DOMAINS = [f"blocked-{i:03d}.example.com" for i in range(1, 154)]
_BLOCKLIST_DOMAINS.insert(129, "acme-metrics.io")

# (run, scraper, status, date, rows scraped). August 2026 failures: run-007 +
# run-011 only; July/September failures exist to force date filtering. Max rows
# scraped: run-013. No row uses status "cancelled" (schema-only, see below).
_RUNS = [
    ("run-001", "google-maps-scraper", "success", "2026-07-03", 12500),
    ("run-002", "news-harvester", "success", "2026-07-06", 8400),
    ("run-003", "jobs-radar", "failed", "2026-07-09", 0),
    ("run-004", "forum-archiver", "success", "2026-07-15", 3200),
    ("run-005", "google-maps-scraper", "success", "2026-07-21", 13100),
    ("run-006", "amazon-crawler", "success", "2026-07-28", 9800),
    ("run-007", "amazon-crawler", "failed", "2026-08-14", 1200),
    ("run-008", "google-maps-scraper", "success", "2026-08-02", 12900),
    ("run-009", "forum-archiver", "success", "2026-08-09", 3500),
    ("run-010", "news-harvester", "success", "2026-08-20", 8700),
    ("run-011", "news-harvester", "failed", "2026-08-27", 300),
    ("run-012", "jobs-radar", "success", "2026-08-05", 2100),
    ("run-013", "google-maps-scraper", "success", "2026-09-01", 14200),
    ("run-014", "forum-archiver", "success", "2026-09-03", 3400),
    ("run-015", "amazon-crawler", "failed", "2026-09-05", 0),
    ("run-016", "news-harvester", "success", "2026-09-06", 8900),
]

# Content referenced by tasks/notion-*/. Verifier judges assert facts from
# these blocks/rows, so any edit here means updating the affected judge.toml
# KNOWN FACTS too. Pages may nest via "children"; "- " prefixed lines become
# bulleted_list_item blocks, everything else paragraphs.
FIXTURES: dict = {
    "pages": [
        {
            "title": "Scraper Inventory",
            "blocks": [
                "Inventory of the scrapers our team runs.",
                "- google-maps-scraper | owner: Alice | status: active",
                "- amazon-crawler | owner: Bob | status: deprecated",
                "- news-harvester | owner: Carol | status: active",
                "- jobs-radar | owner: Dana | status: deprecated",
                "- forum-archiver | owner: Alice | status: active",
            ],
        },
        {
            "title": "Engineering Wiki",
            "blocks": ["Root of the engineering wiki. Runbooks and process docs live here."],
            "children": [
                {
                    "title": "Runbooks",
                    "blocks": ["Operational runbooks, one child page per system."],
                    "children": [
                        {
                            "title": "Postgres Runbook",
                            "blocks": [
                                "Owner: infra team.",
                                "- Staging Postgres listens on port 6543 (via pgbouncer)",
                                "- Nightly backups run at 03:30 UTC",
                                "- Max connections: 200",
                            ],
                        },
                        {
                            "title": "Deploy Runbook",
                            "blocks": [
                                "- Deploys go out via the deploy bot, weekdays only",
                                "- Rollback: re-run the previous release tag",
                            ],
                        },
                    ],
                },
                {
                    "title": "Incident Response",
                    "blocks": ["- Page the on-call first, write the timeline doc second"],
                },
            ],
        },
        {
            "title": "Team Sync 2026-08-11",
            "blocks": [
                "Attendees: Alice, Bob, Carol, Dana.",
                "- Discussed raising the Pro plan price from $29 to $39/month; no decision yet",
                "- news-harvester migration on track",
            ],
        },
        {
            "title": "Team Sync 2026-08-18",
            "blocks": [
                "- Tentative agreement: Pro plan moves to $39/month, pending finance review",
                "- Hiring: two backend candidates in final round",
            ],
        },
        {
            "title": "Team Sync 2026-08-25",
            "blocks": [
                "- Finance pushed back on $39; agreed to set the Pro plan price at $35/month instead",
                "- Deploy freeze next Friday",
            ],
        },
        {
            "title": "Team Sync 2026-09-01",
            "blocks": [
                "- Confirmed: Pro plan price is $35/month, effective October 1",
                "- Retro scheduled for next sprint",
            ],
        },
        {
            "title": "Engineering Onboarding",
            "blocks": [
                "Welcome checklist for new engineers.",
                "- Set up laptop and dev environment",
                "- Read the Engineering Wiki",
                "- For production access, follow the Access Requests Guide page",
            ],
        },
        {
            "title": "Access Requests Guide",
            "blocks": [
                "How to request access to internal systems.",
                "- Production access: complete the security training, then open a DEVOPS ticket in the tracker",
                "- Production access requests are approved by the Infrastructure lead (see Team Directory)",
                "- VPN access: automatic for all employees",
            ],
        },
        {
            "title": "Team Directory",
            "blocks": [
                "- Priya | Infrastructure lead",
                "- Alice | Data team lead",
                "- Bob | Backend engineer",
                "- Carol | Frontend engineer",
            ],
        },
        {
            "title": "Domain Blocklist",
            "blocks": [
                "Domains blocked by the crawler proxy. One entry per line.",
                *[f"- {d}" for d in _BLOCKLIST_DOMAINS],
            ],
        },
    ],
    "databases": [
        {
            "title": "Scraper Runs",
            "properties": {
                "Run": {"title": {}},
                "Scraper": {"select": {"options": [{"name": s} for s in _SCRAPERS]}},
                "Status": {
                    "select": {
                        "options": [{"name": s} for s in ("success", "failed", "cancelled")]
                    }
                },
                "Date": {"date": {}},
                "Rows scraped": {"number": {}},
            },
            "rows": [
                {"Run": r, "Scraper": s, "Status": st, "Date": d, "Rows scraped": n}
                for r, s, st, d, n in _RUNS
            ],
        },
    ],
}


def fixtures_hash() -> str:
    payload = json.dumps(FIXTURES, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()[:12]


def manifest_title() -> str:
    return MANIFEST_PREFIX + fixtures_hash()


def _api(token: str, method: str, path: str, payload: dict | None = None) -> dict:
    req = urllib.request.Request(
        f"https://api.notion.com/v1/{path}",
        method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _rich_text(content: str) -> list[dict]:
    return [{"type": "text", "text": {"content": content}}]


def _block(line: str) -> dict:
    """`- ` prefix -> bulleted_list_item, else paragraph."""
    if line.startswith("- "):
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": _rich_text(line[2:])},
        }
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": _rich_text(line)},
    }


def _parent_children(token: str, parent_page_id: str) -> list[tuple[str, str, str]]:
    """(block_id, title, kind) for child_page / child_database blocks of the
    parent, paginated."""
    children: list[tuple[str, str, str]] = []
    cursor: str | None = None
    while True:
        path = f"blocks/{parent_page_id}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        data = _api(token, "GET", path)
        for block in data.get("results", []):
            kind = block.get("type")
            if kind in ("child_page", "child_database"):
                children.append((block["id"], block[kind].get("title", ""), kind))
        if not data.get("has_more"):
            return children
        cursor = data.get("next_cursor")


def _create_page(
    token: str, parent_page_id: str, title: str, blocks: list[str], children=()
) -> None:
    # Page create caps children at 100 blocks; append the rest in chunks.
    rendered = [_block(line) for line in blocks]
    page = _api(
        token,
        "POST",
        "pages",
        {
            "parent": {"page_id": parent_page_id},
            "properties": {"title": {"title": _rich_text(title)}},
            "children": rendered[:100],
        },
    )
    for i in range(100, len(rendered), 100):
        _api(token, "PATCH", f"blocks/{page['id']}/children", {"children": rendered[i : i + 100]})
    for child in children:
        _create_page(
            token, page["id"], child["title"], child["blocks"], child.get("children", ())
        )


def _row_value(prop_schema: dict, value) -> dict:
    if "title" in prop_schema:
        return {"title": _rich_text(value)}
    if "select" in prop_schema:
        return {"select": {"name": value}}
    if "date" in prop_schema:
        return {"date": {"start": value}}
    if "number" in prop_schema:
        return {"number": value}
    raise ValueError(f"Unsupported property schema: {prop_schema}")


def _create_database(token: str, parent_page_id: str, db: dict) -> None:
    created = _api(
        token,
        "POST",
        "databases",
        {
            "parent": {"page_id": parent_page_id},
            "title": _rich_text(db["title"]),
            "properties": db["properties"],
        },
    )
    for row in db["rows"]:
        _api(
            token,
            "POST",
            "pages",
            {
                "parent": {"database_id": created["id"]},
                "properties": {
                    name: _row_value(db["properties"][name], value)
                    for name, value in row.items()
                },
            },
        )


def seed_notion(token: str, parent_page_id: str, log=print) -> bool:
    """Idempotent reseed: no-op when the manifest hash matches, else archive
    every managed child page / database and recreate from FIXTURES. Returns
    True if it wrote anything. Reads parent children (not the search API,
    whose index lags behind fresh writes)."""
    children = _parent_children(token, parent_page_id)
    if any(title == manifest_title() for _, title, _ in children):
        log(f"notion fixtures up to date ({manifest_title()})")
        return False

    managed = {p["title"] for p in FIXTURES["pages"]}
    managed |= {d["title"] for d in FIXTURES["databases"]}
    for block_id, title, kind in children:
        if title in managed or title.startswith(MANIFEST_PREFIX):
            if kind == "child_database":
                _api(token, "DELETE", f"blocks/{block_id}")
            else:
                _api(token, "PATCH", f"pages/{block_id}", {"archived": True})
            log(f"archived stale fixture {kind}: {title}")

    for page in FIXTURES["pages"]:
        _create_page(token, parent_page_id, page["title"], page["blocks"], page.get("children", ()))
        log(f"created fixture page: {page['title']}")
    for db in FIXTURES["databases"]:
        _create_database(token, parent_page_id, db)
        log(f"created fixture database: {db['title']} ({len(db['rows'])} rows)")
    _create_page(token, parent_page_id, manifest_title(), [])
    log(f"created manifest: {manifest_title()}")
    return True
