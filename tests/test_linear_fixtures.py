"""Locks FIXTURES invariants that tasks/linear-*/tests/judge.toml KNOWN FACTS
assert. A failure here means a fixture edit broke a judge; fix the fixture or
update the judge (and reseed) together."""

from connector_evals.linear_fixtures import FIXTURES, fixtures_hash


def _issues(**filters):
    out = FIXTURES["issues"]
    for key, value in filters.items():
        out = [i for i in out if i.get(key) == value]
    return out


def _project(name):
    return next(p for p in FIXTURES["projects"] if p["name"] == name)


def test_hash_is_deterministic():
    assert fixtures_hash() == fixtures_hash()
    assert len(fixtures_hash()) == 12


def test_bug_triage():  # linear-bug-triage
    bugs = [i for i in FIXTURES["issues"] if "bug" in i["labels"]]
    open_bugs = [i for i in bugs if i["state"] not in ("Done", "Canceled")]
    assert len(open_bugs) == 4
    urgent = {i["title"] for i in open_bugs if i["priority"] == 1}
    assert urgent == {
        "amazon-crawler hits captcha wall on product pages",
        "google-maps-scraper returns stale opening hours",
    }
    # Closed-state bug distractors must exist to force state filtering.
    assert any(i["state"] == "Done" for i in bugs)
    assert any(i["state"] == "Canceled" for i in bugs)


def test_backlog_count_needle():  # linear-backlog-count-needle
    backlog = _issues(state="Backlog")
    assert len(backlog) == 85
    # Backlog must overflow MCP list_issues' default page (50) so a correct
    # count requires paginating or raising the limit.
    assert len(backlog) > 50
    security = [i for i in FIXTURES["issues"] if "security" in i["labels"]]
    assert [i["title"] for i in security] == [
        "Audit proxy credentials for leaked tokens"
    ]


def test_release_blockers():  # linear-release-blockers
    blockers = {
        r["issue"] for r in FIXTURES["relations"] if r["blocks"] == "Ship crawler v2"
    }
    assert len(blockers) == 3
    states = {t: _issues(title=t)[0]["state"] for t in blockers}
    open_blockers = {t for t, s in states.items() if s not in ("Done", "Canceled")}
    assert open_blockers == {"Sign proxy vendor contract", "Load-test proxy failover"}
    assert states["Update scraper base image for v2"] == "Done"


def test_project_status():  # linear-project-status
    in_project = _issues(project="Crawler v2 Launch")
    assert len([i for i in in_project if i["state"] == "Done"]) == 3
    milestones = _project("Crawler v2 Launch")["milestones"]
    earliest = min(milestones, key=lambda m: m["target_date"])
    assert earliest["name"] == "Vendor selected"


def test_health_update():  # linear-health-update
    updates = _project("Crawler v2 Launch")["updates"]
    assert updates[-1]["health"] == "offTrack"
    assert "vendor contract" in updates[-1]["body"]
    # An earlier onTrack update must exist as a distractor.
    assert any(u["health"] == "onTrack" for u in updates[:-1])


def test_vendor_decision():  # linear-vendor-decision
    comments = _issues(title="Choose proxy vendor for the fleet")[0]["comments"]
    assert "NimbusProxy at $2.40/GB" in comments[-1]
    # Rejected candidates appear earlier as distractors, one of them as a
    # tentative pick that later gets reversed.
    assert any("HydraNet" in c for c in comments[:-1])
    assert any("GridRelay" in c and "Proposal" in c for c in comments[:-1])
    assert not any("NimbusProxy" in c and "Decision" in c for c in comments[:-1])


def test_review_states():  # linear-review-states
    # Default started-type state (In Progress) + the seeded custom one.
    started = [s for s in FIXTURES["workflow_states"] if s["type"] == "started"]
    assert [s["name"] for s in started] == ["In Review"]
    assert _issues(state="In Review")  # the custom state is actually used


def test_fleet_runbook():  # linear-fleet-runbook
    doc = _project("Crawler v2 Launch")["documents"][0]
    assert doc["title"] == "Fleet Runbook"
    assert "every 6 hours" in doc["content"]
    assert "FLEET_HALT=1" in doc["content"]


def test_new_issues_never_use_bug_label():
    # linear-bug-triage facts depend on exactly the original bug set; any new
    # fixture issue must pick a different label.
    bugs = [i for i in FIXTURES["issues"] if "bug" in i["labels"]]
    assert len(bugs) == 6


def test_states_exist_at_seed_time():
    # The seeder maps states by name against the default workflow plus the
    # custom states above; any other name would KeyError at seed time.
    known = {"Backlog", "Todo", "In Progress", "Done", "Canceled"}
    known |= {s["name"] for s in FIXTURES["workflow_states"]}
    assert {i["state"] for i in FIXTURES["issues"]} <= known
