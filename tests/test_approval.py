import copy
import json
from pathlib import Path

import pytest

from decision_change_lab.approval import bind_approval, verify_binding
from decision_change_lab.common import ContractError
from decision_change_lab.core import FactStore

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "synthetic-procurement"


@pytest.fixture
def scenario():
    return json.loads((ROOT / "examples/supplier-hold.json").read_text())


def fact(kind, entity, version, observed, payload):
    return {
        "event_id": f"E-{kind}-{version}",
        "source_id": SOURCE,
        "source_event_id": f"E-{kind}-{version}",
        "entity_kind": kind,
        "entity_id": entity,
        "source_version": version,
        "effective_at": "2026-01-15T08:00:00Z",
        "observed_at": observed,
        "payload": payload,
    }


def store_for(scenario, extra=()):
    store = FactStore()
    store.ingest(scenario["initial_facts"] + list(extra))
    return store


def actor_fact(scenario, observed):
    return fact("actor", "REVIEWER-1", 2, observed, {**scenario["actors"][0], "source_version": 2})


def policy_fact(scenario, observed):
    return fact("policy", "POL-1", 2, observed, {**scenario["policy"], "source_version": 2})


def test_binding_is_deterministic_and_holds(scenario):
    store = store_for(scenario)
    first = bind_approval(scenario, "DEC-A", store, "2026-01-15T08:01:00Z")
    assert first == bind_approval(scenario, "DEC-A", store, "2026-01-15T08:01:00Z")
    assert first["source_versions"]["supplier:SUP-A"] == 1
    assert first["source_versions"]["actor:REVIEWER-1"] == 1
    assert verify_binding(first, scenario, store, "2026-01-15T08:30:00Z") == []


@pytest.mark.parametrize("kind", ["actor", "policy"])
def test_visible_fact_overrides_baseline_snapshot(scenario, kind):
    build = actor_fact if kind == "actor" else policy_fact
    entity = "REVIEWER-1" if kind == "actor" else "POL-1"
    store = store_for(scenario, [build(scenario, "2026-01-15T08:02:00Z")])
    key = f"{kind}:{entity}"
    before = bind_approval(scenario, "DEC-A", store, "2026-01-15T08:01:59Z")
    at = bind_approval(scenario, "DEC-A", store, "2026-01-15T08:02:00Z")
    assert before["source_versions"][key] == 1  # baseline fallback
    assert at["source_versions"][key] == 2  # visible fact wins at observation time
    assert before["binding_digest"] != at["binding_digest"]
    if kind == "policy":
        assert at["policy_version"] == 2


@pytest.mark.parametrize("kind", ["actor", "policy"])
def test_later_authority_change_invalidates_binding(scenario, kind):
    build = actor_fact if kind == "actor" else policy_fact
    store = store_for(scenario, [build(scenario, "2026-01-15T08:10:00Z")])
    binding = bind_approval(scenario, "DEC-A", store, "2026-01-15T08:05:00Z")
    assert verify_binding(binding, scenario, store, "2026-01-15T08:09:59Z") == []
    assert verify_binding(binding, scenario, store, "2026-01-15T08:10:00Z") == [
        "source_versions_changed"
    ]


def test_source_change_expiry_and_mutation(scenario):
    store = store_for(scenario, scenario["changes"])
    binding = bind_approval(scenario, "DEC-A", store, "2026-01-15T08:11:00Z")
    assert verify_binding(binding, scenario, store, "2026-01-15T08:12:00Z") == [
        "source_versions_changed"
    ]
    assert verify_binding(binding, scenario, store, "2026-01-15T09:00:00Z") == [
        "approval_expired",
        "source_versions_changed",
    ]
    tampered = {**binding, "actor_id": "OTHER"}
    assert verify_binding(tampered, scenario, store, "2026-01-15T08:11:30Z") == ["binding_tampered"]


def test_payload_and_revision_change_are_rejected(scenario):
    store = store_for(scenario)
    binding = bind_approval(scenario, "DEC-A", store, "2026-01-15T08:01:00Z")
    changed = copy.deepcopy(scenario)
    changed["decisions"][0]["amendment"]["quantity"] = 11
    changed["decisions"][0]["revision"] = 2
    assert verify_binding(binding, changed, store, "2026-01-15T08:02:00Z") == [
        "revision_mismatch",
        "payload_mismatch",
    ]


def test_binding_outside_approval_window_or_unknown_decision(scenario):
    store = store_for(scenario)
    with pytest.raises(ContractError):
        bind_approval(scenario, "DEC-A", store, "2026-01-15T09:00:00Z")
    with pytest.raises(ContractError):
        bind_approval(scenario, "DEC-Z", store, "2026-01-15T08:01:00Z")


def test_missing_non_authority_fact_is_not_filled_from_baseline(scenario):
    store = FactStore()
    store.ingest(scenario["initial_facts"][1:])  # SUP-A absent
    with pytest.raises(ContractError):
        bind_approval(scenario, "DEC-A", store, "2026-01-15T08:01:00Z")
