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

# Page content referenced by tasks/notion-*/. Verifier judges assert facts from
# these blocks (tasks/notion-scraper-inventory: 5 scrapers, 2 deprecated), so
# any edit here means updating the affected judge.toml KNOWN FACTS too.
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


def _parent_child_pages(token: str, parent_page_id: str) -> list[tuple[str, str]]:
    """(page_id, title) for child pages of the parent, paginated."""
    pages: list[tuple[str, str]] = []
    cursor: str | None = None
    while True:
        path = f"blocks/{parent_page_id}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        data = _api(token, "GET", path)
        for block in data.get("results", []):
            if block.get("type") == "child_page":
                pages.append((block["id"], block["child_page"].get("title", "")))
        if not data.get("has_more"):
            return pages
        cursor = data.get("next_cursor")


def _create_page(token: str, parent_page_id: str, title: str, blocks: list[str]) -> None:
    _api(
        token,
        "POST",
        "pages",
        {
            "parent": {"page_id": parent_page_id},
            "properties": {"title": {"title": _rich_text(title)}},
            "children": [_block(line) for line in blocks],
        },
    )


def seed_notion(token: str, parent_page_id: str, log=print) -> bool:
    """Idempotent reseed: no-op when the manifest hash matches, else archive
    every managed child page and recreate from FIXTURES. Returns True if it
    wrote anything. Reads parent children (not the search API, whose index
    lags behind fresh writes)."""
    children = _parent_child_pages(token, parent_page_id)
    if any(title == manifest_title() for _, title in children):
        log(f"notion fixtures up to date ({manifest_title()})")
        return False

    managed = {p["title"] for p in FIXTURES["pages"]}
    for page_id, title in children:
        if title in managed or title.startswith(MANIFEST_PREFIX):
            _api(token, "PATCH", f"pages/{page_id}", {"archived": True})
            log(f"archived stale fixture page: {title}")

    for page in FIXTURES["pages"]:
        _create_page(token, parent_page_id, page["title"], page["blocks"])
        log(f"created fixture page: {page['title']}")
    _create_page(token, parent_page_id, manifest_title(), [])
    log(f"created manifest: {manifest_title()}")
    return True
