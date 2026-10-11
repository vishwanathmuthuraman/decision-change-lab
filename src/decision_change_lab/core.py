"""Validated scenarios and immutable, knowledge-bounded SQLite fact history."""

import json
import sqlite3

from .common import (
    ContractError,
    canonical,
    exact_integer,
    timestamp,
    unique,
    validate_shape,
    validator,
)


def validate_scenario(scenario):
    validate_shape(scenario, "scenario")
    start, horizon = timestamp(scenario["start_at"]), timestamp(scenario["horizon_at"])
    if start > horizon:
        raise ContractError("reversed observation window")
    actors = unique(scenario["actors"], lambda row: row["actor_id"])
    decisions = unique(scenario["decisions"], lambda row: row["decision_id"])
    events = {}
    for event in scenario["initial_facts"] + scenario["changes"]:
        validate_event(event)
        if event["event_id"] in events and events[event["event_id"]] != event:
            raise ContractError("conflicting event identity")
        events[event["event_id"]] = event
    initial = {(row["entity_kind"], row["entity_id"]): row for row in scenario["initial_facts"]}
    for decision in decisions.values():
        amendment, approval = decision["amendment"], decision["approval_seed"]
        for kind in ("order", "supplier", "contract"):
            if (kind, amendment[kind + "_id"]) not in initial:
                raise ContractError("unresolved decision reference")
        quantity = exact_integer(amendment["quantity"], 1)
        price = exact_integer(amendment["unit_price_minor"], 1)
        exact_integer(quantity * price, 1)
        if (
            approval["actor_id"] not in actors
            or approval["policy_id"] != scenario["policy"]["policy_id"]
        ):
            raise ContractError("unresolved approval authority")
        if (
            not timestamp(decision["created_at"])
            <= timestamp(approval["granted_at"])
            < timestamp(approval["valid_until"])
        ):
            raise ContractError("invalid approval window")
        for dependency in decision["dependencies"]:
            kind, identity = dependency["entity_kind"], dependency["entity_id"]
            exists = (kind, identity) in initial
            exists |= kind == "actor" and identity in actors
            exists |= kind == "policy" and identity == scenario["policy"]["policy_id"]
            if not exists:
                raise ContractError("unresolved dependency")
    sequences = set()
    previous = start
    for action in scenario["actions"]:
        at = timestamp(action["at"])
        if action["sequence"] in sequences or not previous <= at <= horizon:
            raise ContractError("invalid action schedule")
        sequences.add(action["sequence"])
        previous = at
        if action["type"] == "dispatch" and action["decision_id"] not in decisions:
            raise ContractError("unknown decision")
        if action["type"] != "dispatch" and action["event_id"] not in events:
            raise ContractError("unknown event")
    return scenario


def validate_event(event):
    schema = validator("scenario").schema
    errors = (
        validator("scenario")
        .evolve(schema={"$defs": schema["$defs"], "$ref": "#/$defs/event"})
        .iter_errors(event)
    )
    if next(errors, None) is not None:
        raise ContractError("invalid source event contract")
    timestamp(event["effective_at"])
    timestamp(event["observed_at"])
    exact_integer(event["source_version"], 1)
    until = event.get("effective_until")
    if until is not None and timestamp(until) <= timestamp(event["effective_at"]):
        raise ContractError("invalid effective interval")
    for field in (
        "unit_price_minor",
        "max_unit_price_minor",
        "max_amendment_total_minor",
        "quantity",
        "max_quantity",
    ):
        if field in event["payload"]:
            exact_integer(event["payload"][field], 1)


class FactStore:
    """An isolated local store; no external ERP transaction is performed."""

    def __init__(self, path=":memory:"):
        self.connection = sqlite3.connect(path, isolation_level=None, timeout=2)
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.execute("""CREATE TABLE IF NOT EXISTS facts (
            event_id TEXT PRIMARY KEY, source_id TEXT NOT NULL,
            source_event_id TEXT NOT NULL, entity_kind TEXT NOT NULL,
            entity_id TEXT NOT NULL, version INTEGER NOT NULL, body TEXT NOT NULL,
            UNIQUE(source_id, source_event_id),
            UNIQUE(source_id, entity_kind, entity_id, version))""")

    def close(self):
        self.connection.close()

    def ingest(self, events):
        self.connection.execute("BEGIN IMMEDIATE")
        accepted = 0
        try:
            for event in events:
                validate_event(event)
                body = canonical(event)
                existing = self.connection.execute(
                    "SELECT body FROM facts WHERE event_id=? OR (source_id=? AND source_event_id=?)",
                    (event["event_id"], event["source_id"], event["source_event_id"]),
                ).fetchall()
                if existing:
                    if any(row[0] != body for row in existing):
                        raise ContractError("conflicting event delivery")
                    continue
                self.connection.execute(
                    "INSERT INTO facts VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        event["event_id"],
                        event["source_id"],
                        event["source_event_id"],
                        event["entity_kind"],
                        event["entity_id"],
                        event["source_version"],
                        body,
                    ),
                )
                accepted += 1
            self.connection.execute("COMMIT")
        except sqlite3.IntegrityError as exc:
            self.connection.execute("ROLLBACK")
            raise ContractError("conflicting source version identity") from exc
        except BaseException:
            self.connection.execute("ROLLBACK")
            raise
        return accepted

    def visible(self, knowledge_at, effective_at=None):
        knowledge = timestamp(knowledge_at)
        effective = timestamp(effective_at or knowledge_at)
        selected = {}
        sources = {}
        for (body,) in self.connection.execute("SELECT body FROM facts ORDER BY event_id"):
            row = json.loads(body)
            if (
                timestamp(row["observed_at"]) > knowledge
                or timestamp(row["effective_at"]) > effective
            ):
                continue
            if row.get("effective_until") and effective >= timestamp(row["effective_until"]):
                continue
            key = row["entity_kind"], row["entity_id"]
            if key in sources and sources[key] != row["source_id"]:
                raise ContractError("cross-source ambiguity requires review")
            sources[key] = row["source_id"]
            precedence = (timestamp(row["effective_at"]), row["source_version"])
            if key not in selected or precedence > selected[key][0]:
                selected[key] = precedence, row
        return [selected[key][1] for key in sorted(selected)]


def inspect(scenario, at):
    validate_scenario(scenario)
    if not timestamp(scenario["start_at"]) <= timestamp(at) <= timestamp(scenario["horizon_at"]):
        raise ContractError("inspection cutoff outside scenario window")
    store = FactStore()
    try:
        store.ingest(scenario["initial_facts"] + scenario["changes"])
        facts = store.visible(at)
        versions = {
            (fact["entity_kind"], fact["entity_id"]): fact["source_version"] for fact in facts
        }
        affected = []
        for decision in scenario["decisions"]:
            changed = [
                dependency
                for dependency in decision["dependencies"]
                if dependency["entity_kind"] not in {"actor", "policy"}
                and versions.get((dependency["entity_kind"], dependency["entity_id"]))
                != dependency["source_version"]
            ]
            if changed:
                affected.append(
                    {"decision_id": decision["decision_id"], "changed_dependencies": changed}
                )
        return {
            "schema_version": "0.1",
            "kind": "fact_history_inspection",
            "knowledge_at": at,
            "visible_facts": facts,
            "review_candidates": affected,
            "dispatch_implemented": False,
        }
    finally:
        store.close()
