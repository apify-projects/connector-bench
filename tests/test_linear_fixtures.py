"""Locks FIXTURES invariants that tasks/linear-*/tests/judge.toml KNOWN FACTS
assert. A failure here means a fixture edit broke a judge; fix the fixture or
update the judge (and reseed) together."""

from connector_evals.linear_fixtures import FIXTURES, fixtures_hash


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


def test_states_are_default_workflow():
    # The seeder maps states by name against a new team's default workflow;
    # any other name would KeyError at seed time.
    assert {i["state"] for i in FIXTURES["issues"]} <= {
        "Backlog", "Todo", "In Progress", "Done", "Canceled",
    }
