# Decision Change Lab

**Status: documentation blueprint. Implementation has not started.** This repository contains a proposed product, architecture, build sequence, evaluation protocol, and original synthetic example. There is no runnable application, completed benchmark, or demonstrated performance yet. All acceptance targets below are unachieved.

Decision Change Lab asks: **when facts change after approval, which pending decisions should be checked again, and which completed decisions need investigation?** The first workflow is a simulated purchase-order amendment. It links decisions to source versions, replays changes, and compares four revalidation strategies under the same final execution check.

Reports identify the operational problem; this exact product is our hypothesis. [PwC’s governance discussion](https://www.pwc.com/gx/en/issues/technology/three-governance-shifts-agentic-ai.html) motivates accountable ongoing oversight. [McKinsey’s procurement analysis](https://www.mckinsey.com/capabilities/operations/our-insights/redefining-procurement-performance-in-the-era-of-agentic-ai) supplies a relevant business workflow. Neither establishes demand, novelty, or the effectiveness of this design. [Sources and rationale](docs/06-sources-and-design-rationale.md) separates evidence from inference.

## Start here

1. Read [requirements](docs/01-product-requirements.md) to understand the user, boundaries, and numbered requirements.
2. Read [architecture](docs/02-architecture.md) before implementing the state model, clock, or dispatch control.
3. Work through [the build plan](docs/03-build-plan.md) in dependency order; maintain [the tracker](tasks.csv).
4. Freeze [the evaluation protocol](docs/04-evaluation.md) before opening the held-out cases.
5. Use [definition of done](docs/05-definition-of-done.md) as the release gate, then [publication runbook](docs/08-publication.md).
6. Keep [delivery decisions and risks](docs/07-delivery-and-risk.md) current using actual evidence.

## What is here now

- Eight design and delivery documents.
- [An original synthetic supplier-hold scenario](examples/supplier-hold.json), [its schema](schemas/scenario.schema.json), and [specified expected outcome](examples/supplier-hold.expected.json).
- [Example-reading instructions](examples/README.md) and [an expected-result schema](schemas/expected-result.schema.json).
- An implementation tracker, ignore rules, and optional model configuration example.

The expected outcome is a specification, **not output from a working system**. No private operational data is needed. The example is separate from the planned development and held-out datasets.

## Intended release

Proposed stack: Python 3.12, uv, SQLite, a command-line runner, and a read-only local report. FastAPI is an optional local interface after the core works. The deterministic demo must run without a model provider or API key. An optional model adapter proposes amendments and dependency candidates; it cannot execute actions.

Version 1 should ship a reproducible demo, four baseline implementations, tests for consequential state transitions, 2,400 deterministic control episodes, and a separately reported agent-input study with 120 cached proposal-generation samples replayed across four strategies for 480 episodes if its budget and implementation gates pass. An incomplete agent evaluation must be prominently marked incomplete; it cannot be counted as delivered.

No install command is available today. Commands in the build plan are explicitly **FUTURE interface contracts**, to implement and verify before copying them into a runnable quick start.

## Scope and limitations

This is a local simulator for research and operational-control design. It does not place real orders, transfer money, reverse completed transactions, certify compliance, or prove losses prevented. Atomicity claims apply only to the specified SQLite transaction boundary. Unknown source changes, incomplete dependencies, and delayed human review remain visible limitations.

A useful negative result is acceptable. A selective strategy must earn any efficiency claim against the same guard and evidence used by its baselines; blocking all decisions is not success.

## License and ownership

License selection is pending. No code, documentation, or data license grant is supplied in this blueprint. Choose and record the licenses and dependency compatibility before an openly licensed release. All example records in this repository were created synthetically for this project; they are not copied from operational records. Report sources are linked, not redistributed.
