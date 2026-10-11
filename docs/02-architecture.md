# 02 — Proposed architecture and contracts

Every choice here is proposed. There is no implementation yet. Architecture changes require a decision-log entry and corresponding protocol review.

## Components and ownership

```text
scenario -> validator -> clock/replay -> versioned facts + event log
                                        |                 |
                                        v                 v
                                  policy evaluator <- strategy selector
                                        |                 |
                         approval/revalidation proof -> case queue
                                        |
                                common dispatch guard
                                        |
                             simulated order mutation

hidden truth + output traces -> isolated evaluator -> aggregate report
optional agent -> validated proposal/dependency candidates -> normal review path
```

Use Python 3.12 and a uv-managed package. The core uses SQLite and standard-library arithmetic/time primitives; propose Pydantic for typed boundaries, jsonschema for fixture validation, pytest for tests, and Ruff for linting. Pin exact versions during the [contract milestone](03-build-plan.md) instead of treating a version guess as tested compatibility. The CLI is the primary interface. A later local FastAPI adapter calls the same application services; it must not implement a second dispatch path.

Suggested implementation layout is `src/decision_change_lab/` with `domain/`, `storage/`, `policies/`, `strategies/`, `replay/`, `agents/`, `evaluation/`, `reports/`, and `cli.py`. Keep hidden labels outside the package runtime input. A shared fixture/event utility may later be extracted into a versioned package, but this repository must install independently and must not import sibling repositories by relative path.

## Data model

| Table or object | Identity and important fields | Invariant |
|---|---|---|
| source_events | event_id; source_id + source_event_id; entity kind/ID; source_version; effective_at; observed_at; canonical payload/hash | Unique delivery identity; conflicting reuse is rejected, not overwritten. |
| fact_versions | entity kind/ID + source_version; effective interval; observed time; payload; correction reference | History remains queryable; ingest order does not determine business-effective order. |
| decision_revisions | decision_id + revision; proposed payload/hash; created_at; status; open_obligation | A changed payload creates a new revision. |
| decision_dependencies | revision; entity kind/ID; field path; recorded version; origin | Separate supplied, extracted, and injected-missing-edge conditions. |
| approvals | approval_id; revision/hash; actor; policy version; source digest; granted/expiry/revoked times | No approval can authorize a different revision or payload. |
| revalidation_proofs | proof_id; approval_id; checked knowledge time; versions; rule outcomes | Fresh proof never silently expands the original authority. |
| dispatch_receipts | idempotency key; request hash; result; execution ID; checked versions; committed_at | At most one simulated mutation for one request. |
| investigations | case_id; decision_id; triggering change; reason; owner; status/disposition | Unique case for the same decision/change/reason. |
| audit_events | monotonically assigned sequence; virtual timestamp; actor; object ID; reason; source references | Causal order can be reconstructed without assuming timestamps are unique. |
| runs | run ID; dataset/config/code digests; strategy; schedule; seed; status; counters | An error run is retained and cannot silently disappear. |

Use SQLite foreign keys, explicit uniqueness constraints, and schema migrations with a recorded version. Do not serialize floating-point money. Canonical payload hashing uses UTF-8 JSON with sorted keys, consistent separators, and no NaN; document this encoding and test it across processes. A hash establishes record equality, not truth or legal authenticity.

## Time and knowledge

Accept timezone-aware RFC 3339 timestamps; normalize to UTC and integer microseconds internally. Reject naive dates/times at event boundaries. Persist the original timestamp string when useful for debugging. The virtual clock advances from the schedule; real monotonic time measures performance only.

`effective_at` says when the source claims the fact became applicable. `observed_at` says when this simulator received it. A query at knowledge time K may use only versions with `observed_at <= K`. For business time T, select the applicable effective interval among those versions according to explicit source version/correction rules. Never use a future observation merely because its effective date is earlier.

Proposed precedence: a correction explicitly supersedes its referenced version for the stated interval; otherwise choose the greatest effective start not after T, then the greatest source version for a tie. Reject ambiguous overlapping intervals without a defined supersession. Backdated corrections remain new observations. Future-effective changes are stored and activate at their effective time after they are observed. Cross-source conflicts produce a review condition, not an arbitrary last-write winner.

## State transitions

Pending revision: `proposed -> approved -> committed`, with `approved -> on_hold`, `on_hold -> proposed` by creating a revised proposal, and explicit cancellation before commit. A new approval can restore an unchanged held revision only after all required checks pass. An expiry creates a freshness review, not automatic rejection of a business-valid action.

Committed orders stay `committed`. Their independent case state is `none -> open -> assigned -> resolved`. Resolution requires a disposition such as confirmed acceptable, contact supplier, or manual remediation required. Automatic reversal is out of scope. Repeated events cannot create repeated cases for the same cause.

The policy evaluator is a pure function of a proposed amendment, permitted facts, policy, and current authority. It returns `valid`, `invalid`, or `insufficient_evidence`, reason codes, and supporting record IDs. Strategy selectors decide which decisions to evaluate and when; they do not change business truth or available actions.

## Shared final dispatch boundary

All four strategies call the same service. The guard derives required supplier, order, policy, contract, and approval records from the typed amendment and fixed policy rules, rather than trusting the selective strategy’s possibly incomplete dependency graph. It sees only currently observed facts. This means missing dependency capture can harm early detection while the guard still prevents a known-invalid pending execution. That is the intended fair comparison.

Proposed local transaction procedure:

1. Validate the request and canonical request hash. Do model calls and expensive preparation outside the transaction.
2. Open `BEGIN IMMEDIATE` with an explicit, bounded busy timeout and retry policy. The writer lock covers source materialization and simulated execution in this same database.
3. Check the idempotency receipt. Return the prior result for the same key/hash; reject a changed request using that key.
4. Re-read decision revision, latest visible source versions, approval/revocation state, current policy, and order status inside the transaction. Ignore earlier preflight success.
5. Evaluate the fixed dispatch rules. On a business rejection, persist the receipt, reason, and hold atomically; do not mutate the order.
6. On success, conditionally update the order using its expected version, create the execution receipt, and append the audit event. A zero-row conditional update is a conflict and must not count as execution.
7. Commit once. On exception, roll back and return an infrastructure error. Never report success before commit.

A source writer scheduled between preflight and the transaction must become visible to step 4. A competing writer after the transaction starts must wait or fail; it cannot alter the checked state before this local commit. A change learned after commit can create an investigation but cannot retroactively make the earlier knowledge available. Test both orders with independent SQLite connections and deterministic barriers. Do not claim this boundary spans an external ERP API. [SQLite’s transaction documentation](https://www.sqlite.org/lang_transaction.html) describes the single-writer behavior used by this proposal.

## Proposed service/API contracts

The CLI calls these services directly. HTTP paths below are optional future adapters, not implemented endpoints. For every mutation use a request ID; execution additionally requires an `Idempotency-Key`. Errors return `{code, message, request_id, details}` with stable codes and no secret values.

| Service / optional path | Required input | Successful output | Rejection cases |
|---|---|---|---|
| ingest / POST `/v1/events` | Event envelope and payload | event_id, accepted/duplicate, observed_at | 422 invalid; 409 identity conflict |
| propose / POST `/v1/decisions` | Amendment, dependency candidates, origin | decision_id, revision, proposed status | 422 bad references or amounts |
| approve / POST `/v1/decisions/{id}/approvals` | revision, payload hash, actor, expiry | approval_id and bound source digest | 409 stale revision; 422 unauthorized actor in fixture |
| review / POST `/v1/decisions/{id}/revalidate` | revision, cause event, knowledge time | outcome, reasons, proof/case IDs | 409 conflicting revision |
| dispatch / POST `/v1/decisions/{id}/dispatch` | revision, approval_id, expected order version, idempotency key | receipt with committed execution or replayed receipt | 409 stale/conflict/invalid; 503 busy/error |
| case / GET `/v1/investigations/{id}` | case ID | change, evidence references, status, owner | 404 unknown case |
| disposition / POST `/v1/investigations/{id}/disposition` | expected case version, actor, disposition | new case version and audit entry | 409 concurrent change |
| replay / CLI `dcl replay` | fixture, strategy, schedule, seed, output | manifest + traces + summary | Nonzero exit for infrastructure/validation failure |

A rejection receipt also binds its key: retrying the exact request returns that rejection. A new approval or changed amendment requires a new request/key. Runtime request IDs and keys are supplied by the caller or generated once by the CLI, never regenerated during retry. The example fixture uses readable IDs; UUIDs can be used later without changing semantics.

## Faults, model boundary, and observability

Source ingestion and notification delivery are separate simulator operations. A lost notification can leave the source version visible in the database while a strategy misses an early review. The dispatch guard still reads the database. A source change never observed by the system is a different failure and must be labeled separately. Replay records dropped notifications; restoring delivery is an explicit scheduled action, not an invisible repair.

A dedicated runtime projection must strip partition, family, template/group lineage, expected labels, fault assignments, evaluator notes, future events, and descriptive fixture IDs or filenames. Replace internal record IDs with stable opaque IDs within each episode and preserve a private evaluator mapping so citations can be scored. Apply the same observable projection to every baseline; human-readable development/example labels must never become benchmark hints. Test both initial input and every tool response/export visible to the system.

An optional model receives only allowed text and tool results. It returns amendment fields and candidate dependencies under a strict schema. It receives no dispatch tool, truth labels, future events, or benchmark family labels. Validate output before creating a proposal; refuse unknown entity IDs and enforce call/step limits. Log model identifier, prompt-template digest, token usage, errors, and price-date assumptions. Publish only reviewed synthetic traces.

For the proposed agent-input evaluation, generate and cache one sanitized proposal/dependency bundle for each of 40 cases × three trials (120 samples). Store an immutable sample ID, sanitized input hash, model configuration, raw-output status, validated output, dependency candidates, token usage, and content digest. Replay the identical bundle across all four strategies (480 episodes), using the same opaque-ID mapping and event schedule within each matched set. Cache an invalid-output or provider-failure status as well; do not regenerate until a favorable proposal appears. No additional model call occurs during these replays. This measures revalidation conditional on generated proposals, not an independently adaptive end-to-end agent comparison.
