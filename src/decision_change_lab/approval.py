"""Immutable approval bindings over knowledge-bounded source versions (FR-04)."""

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
    """Create an immutable binding; it never authorizes another revision or payload."""
    decision = _decision(scenario, decision_id)
    seed = decision["approval_seed"]
    if (
        not timestamp(seed["granted_at"])
        <= timestamp(knowledge_at)
        < timestamp(seed["valid_until"])
    ):
        raise ContractError("approval not active at binding time")
    versions = bound_versions(scenario, decision, store, knowledge_at)
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
        "valid_until": seed["valid_until"],
    }
    binding["binding_digest"] = digest(binding)
    return binding


def verify_binding(binding, scenario, store, at):
    """Return deterministic rejection reasons; an empty list means the binding holds."""
    body = {k: v for k, v in binding.items() if k != "binding_digest"}
    if digest(body) != binding.get("binding_digest"):
        return ["binding_tampered"]
    decision = _decision(scenario, binding["decision_id"])
    reasons = []
    if timestamp(at) >= timestamp(binding["valid_until"]):
        reasons.append("approval_expired")
    if decision["revision"] != binding["revision"]:
        reasons.append("revision_mismatch")
    if digest(decision["amendment"]) != binding["payload_digest"]:
        reasons.append("payload_mismatch")
    if digest(bound_versions(scenario, decision, store, at)) != binding["source_digest"]:
        reasons.append("source_versions_changed")
    return reasons
