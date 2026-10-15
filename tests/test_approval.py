import copy
import json
from pathlib import Path

import pytest

from decision_change_lab.approval import bind_approval, bound_versions, final_guard, verify_binding
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
    decision = scenario["decisions"][0]
    before = bound_versions(scenario, decision, store, "2026-01-15T08:01:59Z")
    at = bound_versions(scenario, decision, store, "2026-01-15T08:02:00Z")
    assert before[key] == 1  # baseline fallback
    assert at[key] == 2  # visible fact wins at observation time


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


@pytest.mark.parametrize("kind", ["actor", "policy"])
def test_old_seed_cannot_bind_new_authority_versions(scenario, kind):
    build = actor_fact if kind == "actor" else policy_fact
    store = store_for(scenario, [build(scenario, "2026-01-15T08:02:00Z")])
    with pytest.raises(ContractError, match="approval evidence changed since grant"):
        bind_approval(scenario, "DEC-A", store, "2026-01-15T08:02:00Z")


@pytest.mark.parametrize("nested", [False, True])
def test_binding_cannot_be_mutated(scenario, nested):
    binding = bind_approval(scenario, "DEC-A", store_for(scenario), "2026-01-15T08:01:00Z")
    with pytest.raises(TypeError):
        if nested:
            binding["source_versions"]["actor:REVIEWER-1"] = 2
        else:
            binding["actor_id"] = "OTHER"


def test_verification_rejects_time_before_grant(scenario):
    scenario["decisions"][0]["approval_seed"]["granted_at"] = "2026-01-15T08:01:00Z"
    store = store_for(scenario)
    binding = bind_approval(scenario, "DEC-A", store, "2026-01-15T08:01:00Z")
    assert verify_binding(binding, scenario, store, "2026-01-15T08:00:59Z") == [
        "approval_not_yet_valid"
    ]
    assert verify_binding(binding, scenario, store, "2026-01-15T08:01:00Z") == []


@pytest.mark.parametrize("kind", ["actor", "policy"])
def test_new_approval_can_bind_new_authority_versions(scenario, kind):
    build = actor_fact if kind == "actor" else policy_fact
    at = "2026-01-15T08:02:00Z"
    store = store_for(scenario, [build(scenario, at)])
    decision = scenario["decisions"][0]
    decision["approval_seed"].update(approval_id="APR-NEW", granted_at=at)
    for dependency in decision["dependencies"]:
        if dependency["entity_kind"] == kind:
            dependency["source_version"] = 2
    if kind == "policy":
        decision["approval_seed"]["policy_version"] = 2
    binding = bind_approval(scenario, "DEC-A", store, at)
    assert binding["approval_id"] == "APR-NEW"
    assert verify_binding(binding, scenario, store, at) == []


def test_seed_policy_version_must_match_grant_evidence(scenario):
    scenario["decisions"][0]["approval_seed"]["policy_version"] = 7
    with pytest.raises(ContractError, match="does not match recorded versions"):
        bind_approval(scenario, "DEC-A", store_for(scenario), "2026-01-15T08:01:00Z")


def test_binding_retains_evidence_after_input_mutation(scenario):
    store = store_for(scenario)
    binding = bind_approval(scenario, "DEC-A", store, "2026-01-15T08:01:00Z")
    scenario["actors"][0]["source_version"] = 2
    assert binding["source_versions"]["actor:REVIEWER-1"] == 1
    assert verify_binding(binding, scenario, store, "2026-01-15T08:01:00Z") == [
        "source_versions_changed"
    ]


def test_final_guard_allows_valid_binding_at_boundaries(scenario):
    store = store_for(scenario)
    binding = bind_approval(scenario, "DEC-A", store, "2026-01-15T08:01:00Z")
    assert final_guard(binding, scenario, store, "2026-01-15T08:30:00Z") == (True, ())
    assert final_guard(binding, scenario, store, "2026-01-15T08:59:59Z")[0]
    assert final_guard(binding, scenario, store, "2026-01-15T09:00:00Z") == (
        False,
        ("approval_expired",),
    )


def test_final_guard_rejects_inactive_actor_at_observation_cutoff(scenario):
    inactive = actor_fact(scenario, "2026-01-15T08:10:00Z")
    inactive["payload"]["active"] = False
    store = store_for(scenario, [inactive])
    binding = bind_approval(scenario, "DEC-A", store, "2026-01-15T08:05:00Z")
    assert final_guard(binding, scenario, store, "2026-01-15T08:09:59Z")[0]
    allowed, reasons = final_guard(binding, scenario, store, "2026-01-15T08:10:00Z")
    assert not allowed
    assert set(reasons) == {"source_versions_changed", "actor_inactive"}


def test_final_guard_uses_visible_policy_limit_over_baseline(scenario):
    new = policy_fact(scenario, "2026-01-15T08:10:00Z")
    new["payload"]["max_amendment_total_minor"] = 9999  # total is 10 * 1000
    store = store_for(scenario, [new])
    binding = bind_approval(scenario, "DEC-A", store, "2026-01-15T08:05:00Z")
    assert final_guard(binding, scenario, store, "2026-01-15T08:09:59Z")[0]
    allowed, reasons = final_guard(binding, scenario, store, "2026-01-15T08:10:00Z")
    assert not allowed and "policy_limit_exceeded" in reasons


def test_final_guard_limit_is_inclusive_and_exact(scenario):
    scenario["policy"]["max_amendment_total_minor"] = 10000
    store = store_for(scenario)
    binding = bind_approval(scenario, "DEC-A", store, "2026-01-15T08:01:00Z")
    assert final_guard(binding, scenario, store, "2026-01-15T08:01:00Z")[0]
    scenario["policy"]["max_amendment_total_minor"] = 9999
    assert final_guard(binding, scenario, store, "2026-01-15T08:01:00Z")[1] == (
        "policy_limit_exceeded",
    )


def test_final_guard_denies_tampered_binding_and_payload_change(scenario):
    store = store_for(scenario)
    binding = dict(bind_approval(scenario, "DEC-A", store, "2026-01-15T08:01:00Z"))
    binding["actor_id"] = "OTHER"
    assert final_guard(binding, scenario, store, "2026-01-15T08:02:00Z") == (
        False,
        ("binding_tampered",),
    )
    good = bind_approval(scenario, "DEC-A", store, "2026-01-15T08:01:00Z")
    scenario["decisions"][0]["amendment"]["quantity"] = 11
    allowed, reasons = final_guard(good, scenario, store, "2026-01-15T08:02:00Z")
    assert not allowed and "payload_mismatch" in reasons
