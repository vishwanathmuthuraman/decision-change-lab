# 06 — Sources and design rationale

Sources checked on 11 October 2026. Brief paraphrases below distinguish published material from this project’s own proposals. No report PDF or third-party dataset is redistributed. These sources do not endorse this repository.

## Business origin

| Source | What it contributes | What we infer and still need to test |
|---|---|---|
| [PwC, The path to trusted autonomy](https://www.pwc.com/gx/en/issues/technology/three-governance-shifts-agentic-ai.html), 11 September 2026 | Discusses accountable ownership, operational oversight, and records connecting agent objectives, actions, evidence, and exceptions. | A change-linked decision record may help a reviewer act on stale evidence. This is our product hypothesis; the article does not measure demand for this tool. |
| [McKinsey, Redefining procurement performance in the era of agentic AI](https://www.mckinsey.com/capabilities/operations/our-insights/redefining-procurement-performance-in-the-era-of-agentic-ai), 5 February 2026 | Describes procurement agents working with changing supplier information and tradeoffs involving cost, service, and risk. | A purchase-order amendment is a concrete setting for a controlled experiment. The article does not validate our revalidation design or prove procurement teams will buy it. |

The origin is therefore **two reported operational themes plus an original experimental proposal**. Procurement discovery must still establish incident frequency, existing controls, reviewer workflow, integration burden, and useful outcomes. Do not present a broad AI-adoption report as a purchasing commitment, market-size estimate, or novelty search.

## Established concepts and technical choices

| Primary source | Relevant concept | Proposed use and limit |
|---|---|---|
| [W3C PROV-DM](https://www.w3.org/TR/prov-dm/), recommendation 2013 | Provenance relates entities, activities, derivations, and responsible agents. | Model decisions and their source relationships. We do not claim to invent provenance or implement full PROV conformance. |
| [MITRE CWE-367](https://cwe.mitre.org/data/definitions/367.html) | State can change between a check and subsequent use. | Test stale preflight and enforce the local transaction boundary. Naming the weakness does not prove our mitigation works. |
| [SQLite transactions](https://www.sqlite.org/lang_transaction.html) | SQLite permits multiple readers but a single writer; an immediate transaction acquires write access and may encounter contention. | Co-locate simulator facts and execution state and test contention/rollback. This does not provide atomicity across remote systems. |
| [Python 3.12 sqlite3](https://docs.python.org/3.12/library/sqlite3.html) | Python’s standard adapter exposes SQLite connections and transaction controls. | Choose and test an explicit transaction-control mode; do not rely on an unspecified default. |
| [uv project guide](https://docs.astral.sh/uv/guides/projects/) | Project metadata and a lockfile support managed Python environments. | Pin the runtime/dependencies and verify clean installation. A lockfile alone is not a reproducibility result. |
| [JSON Schema 2020-12](https://json-schema.org/draft/2020-12) | Standard vocabulary for structural validation. | Validate fixture shape, then run separate reference/time/business semantic checks. The schema cannot encode all workflow correctness. |
| [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/) | Typed request/response boundaries and API construction. | Optional local interface after CLI correctness; no second implementation of business rules. |
| [Anthropic, Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | Discusses tasks, trials, graders, and separating evaluation machinery from the agent under test. | Use explicit tasks, repeated agent trials, and inspectable grading. Vendor guidance is not independent validation of our benchmark. |
| [AI Agents That Matter](https://arxiv.org/abs/2407.01502) | Research argues for considering agent cost alongside capability and careful evaluation design. | Report work/cost with outcomes. Our experiment and any novelty must stand on their own evidence. |

No model vendor is required for the deterministic system. If an agent adapter is added, choose its interface using that provider’s current official documentation and record the access date. This blueprint does not supply vendor-specific API instructions or current prices.

## Design hypotheses to challenge

- A recorded dependency graph may lower revalidation work, but missing edges can conceal affected decisions.
- Full revalidation may use more compute without creating more reviewer escalations if its evaluator correctly recognizes benign changes.
- A shared final guard may make pending invalid-execution rates similar across strategies; differences may appear mainly in review lead time, completed investigations, and work.
- A complete immutable trace can still contain false or incomplete inputs.
- A benchmark can be useful even if selective revalidation performs poorly. Research novelty may lie in failure characterization or reproducibility, but is not established by this blueprint.

Before a research submission, extend the related-work review to current provenance systems, incremental computation, approval binding, event sourcing, and agent evaluation. Verify adjacent products’ documented capabilities directly; do not claim an unoccupied market from a short search.
