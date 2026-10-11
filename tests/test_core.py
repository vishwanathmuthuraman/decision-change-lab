import copy
import json
from pathlib import Path

import pytest

from decision_change_lab.common import ContractError
from decision_change_lab.core import FactStore, inspect, validate_scenario

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def scenario():
    return json.loads((ROOT / "examples/supplier-hold.json").read_text())


def test_contract_and_reference_history(scenario):
    validate_scenario(scenario)
    before = inspect(scenario, "2026-01-15T08:11:00Z")
    after = inspect(scenario, "2026-01-15T08:12:00Z")
    assert before["review_candidates"] == []
    assert {row["decision_id"] for row in after["review_candidates"]} == {"DEC-A", "DEC-C"}
    assert after["dispatch_implemented"] is False


def test_future_effective_fact_does_not_activate(scenario):
    scenario["changes"][0]["observed_at"] = "2026-01-15T08:05:00Z"
    assert inspect(scenario, "2026-01-15T08:09:00Z")["review_candidates"] == []


def test_identical_delivery_is_noop_and_persists(scenario, tmp_path):
    path = tmp_path / "facts.sqlite"
    store = FactStore(path)
    assert store.ingest(scenario["initial_facts"]) == 7
    assert store.ingest(scenario["initial_facts"]) == 0
    store.close()
    reopened = FactStore(path)
    assert len(reopened.visible(scenario["start_at"])) == 7
    reopened.close()


def test_conflict_rolls_back_entire_batch(scenario):
    store = FactStore()
    store.ingest(scenario["initial_facts"])
    conflict = copy.deepcopy(scenario["initial_facts"][0])
    conflict["payload"]["status"] = "on_hold"
    with pytest.raises(ContractError):
        store.ingest(scenario["changes"] + [conflict])
    assert len(store.visible(scenario["horizon_at"])) == 7
    assert all(row["source_version"] == 1 for row in store.visible(scenario["horizon_at"]))
    store.close()


def test_version_identity_cannot_be_overwritten(scenario):
    store = FactStore()
    store.ingest(scenario["initial_facts"])
    duplicate = copy.deepcopy(scenario["initial_facts"][0])
    duplicate["event_id"] = duplicate["source_event_id"] = "another-delivery"
    with pytest.raises(ContractError):
        store.ingest([duplicate])
    assert len(store.visible(scenario["horizon_at"])) == 7
    store.close()


@pytest.mark.parametrize(
    "mutation",
    ["float", "unknown_order", "naive_time", "duplicate_action", "expired_seed", "bad_window"],
)
def test_invalid_contracts_rejected(scenario, mutation):
    if mutation == "float":
        scenario["decisions"][0]["amendment"]["unit_price_minor"] = 1000.0
    elif mutation == "unknown_order":
        scenario["decisions"][0]["amendment"]["order_id"] = "absent"
    elif mutation == "naive_time":
        scenario["changes"][0]["observed_at"] = "2026-01-15T08:12:00"
    elif mutation == "duplicate_action":
        scenario["actions"].append(copy.deepcopy(scenario["actions"][-1]))
    elif mutation == "expired_seed":
        approval = scenario["decisions"][0]["approval_seed"]
        approval["valid_until"] = approval["granted_at"]
    else:
        scenario["horizon_at"] = "2026-01-15T07:00:00Z"
    with pytest.raises((ContractError, ValueError)):
        validate_scenario(scenario)


def test_inspection_is_repeatable_and_does_not_mutate_input(scenario):
    original = copy.deepcopy(scenario)
    assert inspect(scenario, scenario["horizon_at"]) == inspect(scenario, scenario["horizon_at"])
    assert scenario == original


def test_multi_source_conflict_requires_review(scenario):
    store = FactStore()
    row = copy.deepcopy(scenario["initial_facts"][0])
    other = dict(row, event_id="other", source_id="other-source", source_event_id="other")
    store.ingest([row, other])
    with pytest.raises(ContractError, match="ambiguity"):
        store.visible(scenario["start_at"])
    store.close()
