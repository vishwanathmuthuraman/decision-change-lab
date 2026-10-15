"""Immutable approval bindings over knowledge-bounded source versions (FR-04)."""

from types import MappingProxyType

from .common import ContractError, digest, timestamp


def _decision(scenario, decision_id):
    for decision in scenario["decisions"]:
        if decision["decision_id"] == decision_id:
            return decision
    raise ContractError("unknown decision")


def bound_versions(scenario, decision, store, knowledge_at):
    """Source versions for the decision dependencies visible at knowledge_at.

    Visible actor and policy facts take precedence; the scenario's baseline
    snapshots are only a fallback when no such fact is visible yet.
    """
    visible = {
        (f["entity_kind"], f["entity_id"]): f["source_version"] for f in store.visible(knowledge_at)
    }
    baseline = {("policy", scenario["policy"]["policy_id"]): scenario["policy"]["source_version"]}
    baseline.update(
        {("actor", row["actor_id"]): row["source_version"] for row in scenario["actors"]}
    )
    versions = {}
    for dependency in decision["dependencies"]:
        key = dependency["entity_kind"], dependency["entity_id"]
        version = visible.get(key)
        if version is None and key[0] in {"actor", "policy"}:
            version = baseline.get(key)
        if version is None:
            raise ContractError("dependency not visible at knowledge cutoff")
        versions[key[0] + ":" + key[1]] = version
    return versions


def bind_approval(scenario, decision_id, store, knowledge_at):
    """Freeze a trusted fixture approval at its grant-time evidence versions.

    This in-memory record is not an authenticated approval or issuance ledger.
    """
    decision = _decision(scenario, decision_id)
    seed = decision["approval_seed"]
    if (
        not timestamp(seed["granted_at"])
        <= timestamp(knowledge_at)
        < timestamp(seed["valid_until"])
    ):
        raise ContractError("approval not active at binding time")
    versions = bound_versions(scenario, decision, store, seed["granted_at"])
    if bound_versions(scenario, decision, store, knowledge_at) != versions:
        raise ContractError("approval evidence changed since grant")
    recorded = {
        row["entity_kind"] + ":" + row["entity_id"]: row["source_version"]
        for row in decision["dependencies"]
    }
    if recorded != versions or seed["policy_version"] != versions["policy:" + seed["policy_id"]]:
        raise ContractError("approval evidence does not match recorded versions")
    binding = {
        "approval_id": seed["approval_id"],
        "decision_id": decision_id,
        "revision": decision["revision"],
        "payload_digest": digest(decision["amendment"]),
        "actor_id": seed["actor_id"],
        "policy_id": seed["policy_id"],
        "policy_version": versions["policy:" + seed["policy_id"]],
        "source_versions": versions,
        "source_digest": digest(versions),
        "granted_at": seed["granted_at"],
        "valid_until": seed["valid_until"],
    }
    binding["binding_digest"] = digest(binding)
    binding["source_versions"] = MappingProxyType(versions)
    return MappingProxyType(binding)


def verify_binding(binding, scenario, store, at):
    """Check local consistency and freshness; an empty list does not authorize dispatch."""
    body = {k: v for k, v in binding.items() if k != "binding_digest"}
    body["source_versions"] = dict(body["source_versions"])
    if digest(body) != binding.get("binding_digest"):
        return ["binding_tampered"]
    decision = _decision(scenario, binding["decision_id"])
    reasons = []
    if timestamp(at) < timestamp(binding["granted_at"]):
        return ["approval_not_yet_valid"]
    if timestamp(at) >= timestamp(binding["valid_until"]):
        reasons.append("approval_expired")
    if decision["revision"] != binding["revision"]:
        reasons.append("revision_mismatch")
    if digest(decision["amendment"]) != binding["payload_digest"]:
        reasons.append("payload_mismatch")
    if digest(bound_versions(scenario, decision, store, at)) != binding["source_digest"]:
        reasons.append("source_versions_changed")
    return reasons


def _current(store, at, kind, entity_id, baseline):
    """Visible fact payload for an actor/policy; the baseline is only a fallback."""
    for row in store.visible(at):
        if (row["entity_kind"], row["entity_id"]) == (kind, entity_id):
            return row["payload"]
    return baseline


def final_guard(binding, scenario, store, at):
    """Deterministic pre-dispatch decision; returns (allowed, reasons).

    Allows only when the binding verifies, the currently visible actor is active and
    the amendment total (integer minor units) is within the current policy limit.
    It does not dispatch or record any effect.
    """
    reasons = list(verify_binding(binding, scenario, store, at))
    if "binding_tampered" in reasons:
        return False, tuple(reasons)
    decision = _decision(scenario, binding["decision_id"])
    baseline = next((a for a in scenario["actors"] if a["actor_id"] == binding["actor_id"]), None)
    actor = _current(store, at, "actor", binding["actor_id"], baseline)
    if not actor or actor.get("active") is not True:
        reasons.append("actor_inactive")
    policy = _current(store, at, "policy", binding["policy_id"], scenario["policy"])
    amendment = decision["amendment"]
    if amendment["quantity"] * amendment["unit_price_minor"] > policy["max_amendment_total_minor"]:
        reasons.append("policy_limit_exceeded")
    return not reasons, tuple(reasons)
