"""Locks FIXTURES invariants that tasks/notion-*/tests/judge.toml KNOWN FACTS
assert. A failure here means a fixture edit broke a judge; fix the fixture or
update the judge (and reseed) together."""

from connector_evals.notion_fixtures import FIXTURES, fixtures_hash


def _page(title):
    return next(p for p in FIXTURES["pages"] if p["title"] == title)


def _runs():
    db = next(d for d in FIXTURES["databases"] if d["title"] == "Scraper Runs")
    return db, db["rows"]


def test_hash_is_deterministic():
    assert fixtures_hash() == fixtures_hash()
    assert len(fixtures_hash()) == 12


def test_scraper_inventory():  # notion-scraper-inventory
    bullets = [b for b in _page("Scraper Inventory")["blocks"] if b.startswith("- ")]
    assert len(bullets) == 5
    deprecated = [b for b in bullets if "status: deprecated" in b]
    assert len(deprecated) == 2
    assert any("amazon-crawler" in b and "Bob" in b for b in deprecated)
    assert any("jobs-radar" in b and "Dana" in b for b in deprecated)


def test_inventory_actor_reference():  # cross-inventory-actor-audit
    bullets = [b for b in _page("Scraper Inventory")["blocks"] if b.startswith("- ")]
    refs = [b for b in bullets if "Apify Store Actor" in b]
    assert len(refs) == 1
    assert "news-harvester" in refs[0] and "apify/rag-web-browser" in refs[0]


def test_incident_response_hop():  # cross-incident-runbook-hop
    wiki = _page("Engineering Wiki")
    incident = next(c for c in wiki["children"] if c["title"] == "Incident Response")
    assert any("security-labeled issue" in b and "Linear" in b for b in incident["blocks"])
    assert any("Fleet Runbook" in b for b in incident["blocks"])


def test_blocklist_needle():  # notion-blocklist-needle
    blocks = _page("Domain Blocklist")["blocks"]
    domains = [b[2:] for b in blocks if b.startswith("- ")]
    assert len(domains) == 154
    # Needle must sit past the first 100 blocks so a correct answer requires
    # paginating blocks/children.
    assert blocks.index("- acme-metrics.io") > 100


def test_failed_runs_august():  # notion-failed-runs-august
    _, rows = _runs()
    aug_failed = {
        (r["Run"], r["Scraper"])
        for r in rows
        if r["Status"] == "failed" and r["Date"].startswith("2026-08")
    }
    assert aug_failed == {("run-007", "amazon-crawler"), ("run-011", "news-harvester")}
    # Distractor failures outside August must exist to force date filtering.
    other_failed = [r for r in rows if r["Status"] == "failed" and not r["Date"].startswith("2026-08")]
    assert other_failed


def test_status_options():  # notion-run-status-options
    db, rows = _runs()
    options = {o["name"] for o in db["properties"]["Status"]["select"]["options"]}
    assert options == {"success", "failed", "cancelled"}
    # cancelled is schema-only: visible via database introspection, never in rows.
    assert all(r["Status"] != "cancelled" for r in rows)


def test_wiki_postgres_leaf():  # notion-wiki-postgres-port
    runbooks = next(c for c in _page("Engineering Wiki")["children"] if c["title"] == "Runbooks")
    postgres = next(c for c in runbooks["children"] if c["title"] == "Postgres Runbook")
    assert any("port 6543" in b for b in postgres["blocks"])
    assert any("03:30 UTC" in b for b in postgres["blocks"])


def test_pricing_decision():  # notion-pricing-decision
    assert any("$35/month" in b for b in _page("Team Sync 2026-08-25")["blocks"])
    assert any("Confirmed" in b and "$35/month" in b for b in _page("Team Sync 2026-09-01")["blocks"])
    # $39 must only ever appear as tentative/rejected, never as the final price.
    for title in ("Team Sync 2026-08-11", "Team Sync 2026-08-18"):
        assert not any("$35" in b for b in _page(title)["blocks"])


def test_prod_access_steps():  # notion-prod-access-steps
    guide = _page("Access Requests Guide")["blocks"]
    assert any("security training" in b and "DEVOPS ticket" in b for b in guide)
    assert any("Infrastructure lead" in b for b in guide)
    assert any("Priya" in b and "Infrastructure lead" in b for b in _page("Team Directory")["blocks"])
    assert any("Access Requests Guide" in b for b in _page("Engineering Onboarding")["blocks"])
