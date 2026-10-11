# 07 — Technical limitations and research risks

This project defines a local experiment. Implementation, measured performance, independent reproduction and customer outcomes are not established.

| Limitation | Consequence | Verification or disclosure required |
|---|---|---|
| Incomplete dependency capture | A relevant decision may not be selected for early review. | Measure missing/extracted-edge conditions separately; retain the shared final guard. |
| Unobserved or delayed facts | The system cannot act on unavailable information. | Preserve effective and observed times; state the knowledge cutoff in results. |
| Local transaction boundary | SQLite control does not establish atomicity across external services. | Test races inside the declared boundary; avoid distributed-execution claims. |
| Changed action identities | Idempotency keys alone may not identify equivalent business intent. | Test identity/content conflicts and publish the supported contract. |
| Conservative blocking | Blocking every decision can appear safe while preventing useful work. | Report valid completion, false escalation and review work with error rates. |
| Synthetic evaluation | Scenario balance and templates may differ from real operations. | Separate lineages, report provenance and avoid inferred financial savings. |
| Model proposal errors | Valid JSON can still contain unsupported content. | Validate references and authority; retain failures and bounded fallback behavior. |
| Grader or analysis defects | Apparent advantages may be measurement errors. | Hand-check scoring, publish deviations and consistently rescore corrected versions. |

The comparison tests selection and timing under a common execution guard. It does not prove that selective revalidation uniquely prevents losses, reverses completed transactions or establishes regulatory compliance. A negative or mixed result is useful when the methodology and failure inventory remain inspectable.

Keep expected labels outside runtime inputs. Report deterministic-control and agent-input studies separately, including optional work that remains incomplete. Changes to contracts or protocol require a documented rationale and versioned evidence.

See [evaluation](04-evaluation.md), [release gates](05-definition-of-done.md) and [publication rules](08-publication.md). Public examples must remain synthetic; operational data and confidential commercial material belong outside this repository.
