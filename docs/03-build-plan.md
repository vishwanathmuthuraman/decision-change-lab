# 03 — Build plan, in execution order

**All commands in this document are FUTURE commands.** The package, CLI, tests, manifests, and reports they reference do not exist yet. Implement each interface before using its command as evidence. Never mark a task complete just because its documentation exists. Update [tasks.csv](../tasks.csv) with actual status and evidence when work starts.

Estimates below are focused engineering/research hours, not promises or elapsed calendar time. Total baseline estimate: **184–250 hours**, plus 20–30% contingency and independent reviewer time. Optional UI work is excluded. Move later gates if implementation or evidence takes longer; never replace missing evaluation with invented results.

## WP-01 — Validate the workflow and freeze v1 scope (8–12 h)

Dependencies: none. Inputs: requirements, synthetic example, and source rationale.

1. Walk through the example by hand and list each business rule and responsible reviewer.
2. Ask permitted procurement/automation practitioners about a recent changed-fact incident and current controls. No outreach or data collection is automated by this blueprint.
3. Keep raw interview notes and identities outside this repository. Write only reviewed, permitted aggregate findings in `docs/discovery.md`: interview count, role categories, incident patterns, workarounds, supporting public evidence, and contradictions. An unanswered question stays unanswered.
4. Confirm the one-currency, one-amendment scope and the difference between hold and investigation. Record changes in the decision log before coding.

Expected output: bounded scope, documented uncertainties, and a manually verified example. Check: every proposed consequence has an explicit synthetic rule. No implementation command is required.

## WP-02 — Bootstrap the package and quality tools (6–8 h)

Depends on WP-01. Create `pyproject.toml`, `.python-version`, `src/decision_change_lab/__init__.py`, `cli.py`, and `tests/test_cli.py`. Set Python 3.12, define the `dcl` entry point, and select compatible dependency versions. Add pytest/Ruff/jsonschema to the development group and an optional API group only if needed. Do not add a provider SDK to the default install.

Prerequisite: install Python 3.12 and uv using the current [official uv installation guide](https://docs.astral.sh/uv/getting-started/installation/), then verify `uv --version` and the selected interpreter. uv is not assumed to be installed. Follow the documented platform-specific method; no installation is performed by this blueprint.

FUTURE commands after the project files exist:

```sh
uv lock
uv sync --locked
uv run dcl --help
uv run pytest tests/test_cli.py
uv run ruff check .
```

Expected output: committed lockfile eventually, working help, and one real command-contract test. Check: a clean environment resolves from the lock without undocumented global packages. Record the actual uv/Python versions.

## WP-03 — Typed models, fixture validation, and money (10–14 h)

Depends on WP-02. Inputs: existing JSON schemas/example. Create `domain/models.py`, `domain/money.py`, `replay/validation.py`, `tests/test_fixture_validation.py`, and `tests/test_money.py`.

Implement schema checks followed by semantic checks: unique IDs; all references resolve; initial decisions cite initial facts; positive bounded integer amounts/quantities; UTC-aware times; valid source-version progression; no ambiguous corrections. Derive totals with integer arithmetic and explicit bounds. Validate the expected-result schema separately from system input.

FUTURE: `uv run dcl validate examples/supplier-hold.json` and `uv run pytest tests/test_fixture_validation.py tests/test_money.py`.

Expected output: readable validation errors including JSON path; malformed and conflicting inputs rejected. Check: the example validates, and negative fixtures fail for the intended reason.

## WP-04 — Versioned storage and knowledge-time queries (14–18 h)

Depends on WP-03. Create `storage/schema.sql`, `storage/repository.py`, `storage/migrations.py`, `domain/time.py`, and `tests/test_fact_history.py`.

Implement event identity/hash checks, fact history, deterministic precedence, effective intervals, corrections, and observed-time filtering. Use injected clocks. Define migration version 1 and ensure foreign keys are enabled for every connection. Keep fixture load atomic.

FUTURE: `uv run pytest tests/test_fact_history.py`.

Expected output: a database can answer “what was known then?” and “what was effective then?” differently. Checks: duplicate delivery, conflicting same ID, future fact, late correction, offset normalization, out-of-order arrival, migration failure rollback, and restart preservation.

## WP-05 — Policy, decisions, and approval binding (14–18 h)

Depends on WP-04. Create `policies/purchasing.py`, `domain/decisions.py`, `domain/approvals.py`, and `tests/test_approvals.py`.

Implement the pure evaluator and every v1 business rule. Store immutable revisions and dependencies; distinguish extracted from supplied dependencies. Bind approvals and allow a benign revalidation proof only under the frozen rule. Implement actor authority using fixture role records, without implying production identity verification.

FUTURE: `uv run pytest tests/test_approvals.py`.

Expected output: rule-level reasons and evidence references. Checks: changed payload, changed policy, revoked actor, expired approval, benign source update, insufficient evidence, integer totals, and revision conflict.

## WP-06 — Atomic dispatch and retry safety (18–24 h)

Depends on WP-05. Create `domain/dispatch.py`, `storage/transactions.py`, `tests/test_dispatch.py`, and `tests/test_dispatch_races.py`.

Implement the exact common boundary in the architecture. Use one database for source materialization and simulated order mutation. Add deterministic barriers for concurrency tests; never test a race using unreliable sleeps. Persist rejected receipts as well as successful ones. Return stable business/infrastructure error codes.

FUTURE: `uv run pytest tests/test_dispatch.py tests/test_dispatch_races.py`.

Expected output: one execution receipt at most, with the exact versions used. Checks: simultaneous duplicate request, changed-content key reuse, commit failure rollback, lock timeout, stale preflight, change before final transaction, competing writer during transaction, and reapproval/new key. This gate must pass before any demo is called safe within its local boundary.

## WP-07 — Four strategies and investigation lifecycle (16–20 h)

Depends on WP-05 and WP-06. Create `strategies/base.py`, `cached.py`, `expiry.py`, `full.py`, `selective.py`, `domain/investigations.py`, and `tests/test_strategies.py`.

Use a shared `select(cause, now, population)` interface. Implement the fixed-expiry scheduler and keep full/selective revalidation on the same pending-plus-open-committed population. Share evaluator, escalation, dispatch, and case deduplication. Preserve committed status when opening a case. Log selected, checked, escalated, and unchanged decisions separately.

FUTURE: `uv run pytest tests/test_strategies.py`.

Expected output: meaningful selection/work differences with common downstream behavior. Check the supplied example across all four strategies without requiring identical detection times or early case counts.

## WP-08 — Replay, audit trace, and offline demo (14–18 h)

Depends on WP-07. Create `replay/clock.py`, `replay/runner.py`, `replay/schedules.py`, `reports/case_report.py`, `tests/test_replay.py`, and `tests/test_export.py`.

Implement fixture actions in explicit order, event delivery separate from ingestion, virtual ticks, dispatch attempts, and schedule-injected faults. Normalize transient fields before hashing replay output. Add CLI `validate`, `replay`, and `demo`; demo should print a case summary and write a local report with source links inside the report.

FUTURE:

```sh
uv run dcl demo --offline --output reports/demo
uv run dcl replay --fixture examples/supplier-hold.json --strategy selective --schedule canonical --seed 41 --output reports/example
uv run pytest tests/test_replay.py tests/test_export.py
```

Expected output: supplier-A pending action held; supplier-B action completed; supplier-A committed action retains status with one case. Check against specified expected output; label discrepancies as defects or document justified specification changes.

## WP-09 — Development dataset and independent truth (18–24 h)

Depends on WP-08. Create `datasets/generator.py`, `evaluation/oracle.py`, `evaluation/metrics.py`, `tests/test_oracle.py`, `tests/test_metrics.py`, and a dev-only `protocol/dev-config.json`.

Author 50 development cases across five families, separated by incident/template group. Manually derive truth for representative material and benign cases before writing metric code. Store truth in an evaluator-only file. Implement all metric denominators and report failure/timeouts. Build and test a runtime projection using opaque record IDs: no future observation, oracle label, partition/family/template field, fault hint, or descriptive scenario path may reach a strategy through prompts or tools.

FUTURE: `uv run dcl evaluate --partition dev --mode control --output reports/dev` and `uv run pytest tests/test_oracle.py tests/test_metrics.py`.

Expected output: a development report with errors visible, a calibrated grader, and a leakage audit. Check hand-calculated numerator/denominator examples, empty denominator handling, and block-all behavior.

## WP-10 — Optional agent path required for the agent study (14–20 h)

Depends on WP-09. Create `agents/protocol.py`, `agents/mock.py`, one explicitly chosen adapter, `agents/validation.py`, `agents/proposal_cache.py`, `tests/test_agent_boundary.py`, and `protocol/agent-config.json`.

First implement a mock provider and structured output validation. Only then add a provider-neutral connection using the selected provider’s current official documentation. Keep credentials in the environment. Pilot on development cases, inspect extraction errors, and choose prompts, model snapshot, limits, and a stop-spend threshold. Add immutable proposal caching and a test that all four strategies receive the same proposal/dependency content and sanitized evidence digest. Cache invalid/failure outcomes without success-seeking regeneration. This blueprint authorizes no paid calls.

FUTURE: `uv run pytest tests/test_agent_boundary.py` and `uv run dcl generate-proposals --partition dev --max-samples 8 --output reports/agent-pilot`.

Expected output: real pilot cost/latency estimates and a bounded agent path. Check no execution tool, hidden truth, future event, uncontrolled retry, or malformed proposal crosses the boundary. If this gate does not pass, release the control study with the agent study explicitly deferred. Record the deferral in the tracker: WP-11 may proceed for control mode after WP-09, while its agent branch remains blocked on WP-10.

## WP-11 — Seal protocol, test partition, and subset (12–16 h)

Depends on WP-09 and WP-10 for the agent configuration. Create `protocol/frozen.json`, `datasets/test-manifest.json`, `datasets/agent-subset.json`, and `docs/protocol-freeze.md` only after the freeze decisions are real.

Generate 200 held-out cases by disjoint incident/template groups; verify each family contains 20 material and 20 control cases. Select the 40-case agent subset without looking at outcomes. Freeze schedules, thresholds, analysis, seeds, highest shared lineage cluster unit, proposal-cache contract, generation failure handling, and recovery behavior. Have another reviewer audit realism and hidden truth separately from developers tuning strategies.

FUTURE: `uv run dcl audit-dataset --manifest datasets/test-manifest.json` and `uv run dcl freeze --config protocol/frozen.json --output reports/freeze`.

Expected output: content hashes, zero group overlap, complete strata, and dated freeze record. Do not label a public fixture “held out” after it has been used for tuning. Development continues on development cases only.

## WP-12 — Execute and analyze the held-out study (18–26 h)

Depends on WP-11. Create run manifests and analysis outputs using the already frozen evaluator. Capture failures before retrying, permit only documented infrastructure retries, and retain both attempts. Keep deterministic and paired agent-input result tables separate. Generate and seal 120 held-out proposal samples only after protocol freeze; replay each cached output across all four strategies. Record its identical content digest in each matched episode. No new model calls occur during replay.

FUTURE:

```sh
uv run dcl evaluate --config protocol/frozen.json --partition test --mode control --output reports/control
uv run dcl generate-proposals --config protocol/frozen.json --partition test --output reports/proposals
uv run dcl evaluate --config protocol/frozen.json --partition test --mode agent --proposals reports/proposals --output reports/agent
uv run dcl analyze --input reports/control --output reports/analysis-control
uv run dcl analyze --input reports/agent --output reports/analysis-agent
```

Expected output: 2,400 control episodes and, if its gate passes, 120 generated proposal samples and 480 replay episodes accounted for, including refusals, invalid output, business rejections, and infrastructure failures. Check the 120-to-480 mapping, identical proposal/evidence hashes across strategies, highest-lineage clustered intervals, and cost reconciliation. The study estimates revalidation conditional on generated inputs; independently adaptive end-to-end sampling is extra scope. A corrected grader requires documented consistent rescoring, not selective deletion.

## WP-13 — Technical report, failure analysis, and delivery review (14–20 h)

Depends on WP-12. Create `docs/results/technical-report.md`, `docs/results/failure-cases.md`, and `docs/retrospective.md` only with actual measurements. Include methods, protocol deviations, counts, uncertainty, costs, limitations, and negative results. Choose representative failures by a declared rule, not just favorable screenshots.

FUTURE: `uv run dcl verify-report --input docs/results/technical-report.md --manifest reports/control/manifest.json` after implementing a checker for referenced run IDs/tables.

Expected output: claims trace to artifacts; reviewer feedback and resulting changes are recorded. A software release and technical report do not establish peer review or novelty. Review every requirement against evidence in the definition of done.

## WP-14 — Fresh install and release preparation (8–12 h)

Depends on WP-13. Create `CHANGELOG.md`, a real installation section, CI configuration, selected license files, and a release manifest with reviewed public artifacts. Use the publication runbook. Optional hosting is a separate decision; a local demo suffices.

FUTURE:

```sh
uv sync --locked
uv run pytest
uv run ruff check .
uv run dcl demo --offline --output reports/reproduction
uv build
```

Expected output: another person can reproduce the example from a clean checkout using the documented version. The release gate includes license/ownership review and a status-correct README. Publishing and tagging require an explicit release action; none occurs through this plan.

## Optional interface after the core

Estimate an additional 12–20 hours for a local FastAPI adapter and a minimal view of decisions, source changes, and cases. Bind to localhost by default and use the same services. Test adapter-level validation and guard bypass. Do not add auth, cloud hosting, or ERP integration as incidental tasks; each needs a revised scope.
