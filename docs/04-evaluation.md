# 04 — Evaluation protocol

Status: proposed protocol, not preregistered, frozen, or executed. These are planning sample sizes, not a statistical power guarantee. A freeze record will replace open configuration choices after development. [Build plan WP-09–12](03-build-plan.md) defines the execution gates.

## Question and estimands

Can selective revalidation after source-data changes reduce missed affected decisions and review work compared with cached approval, fixed expiry, and full revalidation? The primary comparison is **revalidation selection and timing under a common dispatch guard**. It is not a test of selective-only execution protection.

Prespecify two primary contrasts: selective minus fixed-expiry for missed-affected proportion; selective minus full for policy-evaluation work. Report both error and work dimensions. A lower work count accompanied by more missed decisions is a tradeoff, not unqualified improvement. All other contrasts are secondary and are labeled exploratory unless frozen otherwise.

## Dataset, independence, and sealing

Create original synthetic scenarios with explicit rules and independently derived expected outcomes. Five families:

1. Supplier status or eligibility changes.
2. Price and quantity corrections.
3. Contract or policy changes.
4. Approval expiry, revocation, or authority changes.
5. Delayed, backdated, or corrected records.

Each scenario includes pending amendments, at least one open committed order, and unrelated decisions. Proposed standard population: three decisions, as in the worked example. If a family needs more, freeze and report the population rule before generating test cases. A “material” case has at least one oracle-required action; a control has none under its declared horizon. Include benign value changes as well as unchanged controls.

| Partition | Per family | Total | Use |
|---|---|---:|---|
| Development | 5 material + 5 control | 50 | Tune rules, expiry, prompts, graders, and reporting. |
| Held-out test | 20 material + 20 control | 200 | Final comparison only after freeze. |
| Agent subset of test | 4 material + 4 control | 40 | Paired generated-input revalidation study. |

The agent subset is part of the 200, not 40 additional independent cases. Select it by a frozen seeded procedure before inspecting outcomes. Group by the underlying incident or instantiated template; all variants stay in one partition. Generic family names can recur across partitions, but merely changing names/amounts does not make near-identical incident templates independent. Store `template_group_id` plus the highest shared incident/template-lineage identifier needed to join closely related derived templates; use that highest shared lineage for both partitioning and uncertainty clusters. Audit overlap and disclose how templates differ. Broad family labels alone do not establish common incident lineage.

Seal the test manifest, fixture files, oracle, and configuration with content hashes. During tuning, developers access development cases only; use a separate evaluator/reviewer for the test material where feasible. A solo developer cannot claim an independently protected test set if they inspect its answers. Record that limitation honestly and obtain an external reproduction set later. Public release of test data ends its usefulness as a secret future test set.

## Four strategy definitions

| Strategy | Trigger and population | Shared behavior |
|---|---|---|
| cached | No source-event-triggered revalidation; explicit dispatch still checks current state. | Same evaluator, knowledge access, escalation rules, and final guard. |
| expiry | At a frozen interval, revalidate every pending and open committed decision due for freshness review. A completed order carries a monitoring timestamp even though approval expiry no longer authorizes an action. | Same population eligibility and available response as other strategies. |
| full | After each delivered source change, revalidate every pending and open committed decision. | Does not gain hidden facts or a better guard. |
| selective | After each delivered source change, select decisions from recorded dependency edges and evaluate those decisions. | Same policy evaluator and dispatch guard; missing edges remain a failure mode. |

Use exactly the same source materialization, notification schedule, review-service delay, approval semantics, and dispatch attempts per paired run. Freeze expiry and event-coalescing settings on development data. Full revalidation can examine unaffected decisions without necessarily escalating them: **work and unnecessary escalation are separate metrics**. All strategies may open investigations for committed decisions once selected and found affected. Do not withhold that response from a baseline.

## Two modes and exact run counts

**Control mode:** fixed proposed amendments, no model calls. Initial reference dependencies are supplied from the scenario’s intended relationships. The clean condition therefore measures an oracle-dependency control system. When a schedule explicitly removes an edge, label it a corrupted-dependency stress condition; do not report it as perfect-oracle performance. Truth labels still remain outside the system.

**Paired agent-input mode:** after freezing model/version, prompt, decoding, tools, limits, and validation rules, generate one amendment/dependency bundle for each of 40 cases × three trials: **120 proposal-generation samples**. Each sample receives only sanitized synthetic text and allowed tool evidence, with no strategy label or oracle information. Cache the actual output, validation status, captured dependencies, sanitized input digest, model configuration, token usage, and immutable proposal ID. Replay that identical cached sample across all four strategies, producing **480 episodes**. Do not replace extraction errors with oracle values. An invalid output, refusal, or failed generation remains a recorded sample and produces the same no-proposal/failure input for all four strategies; do not resample until success. Report extraction/dependency errors at the 120-sample level and downstream outcomes at the 480-episode level.

This paired-input design isolates revalidation behavior **conditional on proposal generation**. It includes observed proposal errors but does not compare four independently adaptive end-to-end agents. Any independent end-to-end sampling, adaptive model calls during replay, or second-model replication requires a separate frozen protocol and additional budget. Sharing trial labels alone would not pair stochastic proposals; the cached content and evidence digests must match.

| Mode | Calculation | Runs |
|---|---|---:|
| Deterministic control | 200 scenarios × 4 strategies × 3 schedules | 2,400 episodes |
| Agent proposal generation | 40 scenarios × 3 sampled proposals | 120 generation samples |
| Paired agent-input replay | 120 cached samples × 4 strategies × 1 assigned schedule | 480 episodes |

For the agent study, assign **one** of the three schedules to each scenario before running it, balancing schedule allocation within family/material strata as closely as 40 cases permit. Store the assignment in the subset manifest. Do not run all three schedules and still call the total 480; that would produce 1,440 episodes. Three generation trials measure proposal variability, not three independent underlying cases. Preserve each sampled proposal and replay it unchanged across strategies; hosted generation itself may not be exactly reproducible, but its recorded output is inspectable and replayable. The 120 generation samples are a separate accounting stage, not an additional 120 strategy episodes. Count all model/tool calls made within each bounded sample, including failures.

## Three prescribed schedules

Proposed stress recipes below must be made executable and frozen on development cases. They are not a Cartesian sweep. For each family, document equivalent valid transformations and preserve material/control labels under the final oracle.

| ID | Recipe | What it tests |
|---|---|---|
| S0 canonical | Complete recorded dependencies; source observations and notifications delivered in timestamp order; ordinary dispatch. | Reference behavior; supplied dependencies are explicitly an oracle condition in control mode. |
| S1 delayed | Deliver a nonmaterial older notification after a newer notification; delay a designated observation; remove one designated recorded dependency edge after initial capture. | Time/knowledge handling and dependency loss. The same edge corruption and event inputs reach every strategy. |
| S2 boundary | Materialize a designated source update but suppress its notification through the observation horizon; interleave another designated update after preflight and before final transaction acquisition. | Missing event notification and stale preflight. Separate unit tests cover a writer blocked during the transaction. |

For a control case, the injected update remains benign; dependency removal alone must not manufacture a business-invalid label. Do not inject a future source update invisibly and then claim a system failed to use knowledge it never received. Report cases whose invalidity is knowable by the current observation cutoff separately from retrospective invalidity revealed later.

Fix virtual-time horizon, designated edges/events, delays, review-service times, dispatch attempt times, expiry, and seeds in the freeze file. A proposed development starting point is a 30-minute horizon with an expiry interval chosen from 5, 10, and 15 minutes on development data. These values are **tuning candidates**, not frozen parameters. Count extra exploratory sweeps, guard-off ablations, or new stress recipes separately.

## Oracle and scoring

An evaluator-only truth file describes, for each decision/change pair, whether review is required, the correct pending/committed consequence, earliest knowable time, and the eligible observation window. It is never passed into a strategy or agent. The runtime projection also removes split/family/template metadata, injected-fault labels, descriptive scenario IDs and file paths. Use opaque per-episode record IDs with an evaluator-only mapping, preserving the same substantive evidence for every strategy. Audit tool responses as well as the initial prompt; a label-free prompt with a revealing filename is still leakage. Use executable state assertions for action outcomes; use a human reviewer to audit realism and ambiguous policies. A model-based judge is unnecessary for the core deterministic truth.

| Measure | Definition and denominator |
|---|---|
| Missed affected decisions | Oracle-required decision/change pairs with no correct hold or case by the frozen deadline / all oracle-required pairs. Report pending and committed separately. |
| Unnecessary escalations | Oracle-unaffected decision/change opportunities receiving a hold or investigation / all oracle-unaffected opportunities. Also show absolute queue size. |
| Invalid pending allowed | Invalid dispatch attempts that commit / oracle-invalid dispatch attempts, using currently knowable facts; show retrospective invalidity separately. |
| Completed routed correctly | Affected open committed decision/change pairs with the required case / affected open committed pairs. Never count an automatic reversal as correct. |
| Valid-action completion | Oracle-valid eligible actions committed by horizon / oracle-valid eligible actions. Include holds and timeouts in the denominator. |
| Detection delay | First correct action time minus earliest knowable time; show distribution for detected cases plus missed fraction and censoring horizon. |
| Revalidation work | Policy evaluator invocations, decisions selected, records read, and queue entries; report per scenario and per affected pair. |
| Cost/runtime | Model tokens/calls and measured provider cost assumptions, local runtime/hardware, and human review effort only if actually measured. |
| Agent errors | Field/dependency precision and recall against intended references; invalid schema, unknown IDs, missing evidence, and refusal rates. |

When a denominator is zero, print “not applicable (0 eligible)” rather than 0% success. Count a crash as an error, not a valid abstention. Preserve a run-status table and sensitivity analysis for incomplete runs; never calculate success only over convenient survivors. Report material/control strata and each family before an aggregate.

## Uncertainty and decision rules

Compute paired differences for each scenario under matched schedules and trials. Average repeats within scenario for a scenario-level estimate; resample at the highest shared incident/template-lineage level when scenarios or derived templates share one. Keep the four strategy outputs for each cached proposal together, and do not treat its three generation samples as independent scenarios. Preserve all strategy outputs for a sampled group together. Proposed method: 10,000 seeded cluster-bootstrap replicates with 95% percentile intervals, accompanied by raw paired counts and the number of independent groups. Few groups or near-zero events make intervals fragile; disclose this rather than implying precision from 2,880 repeated runs.

Predeclare that an efficiency claim requires lower work with an acceptable error/completion tradeoff whose margin is chosen on development data and justified by the synthetic task. Do not choose the margin after seeing test results. A safety-unit-test gate can require zero known-invalid executions in specified races; finite benchmark zero errors does not establish zero real-world risk.

Record dataset/protocol/code digests, source-event ordering, run seed, policy version, model ID, prompts/tools, grader version, price date, machine details, and all deviations. If a grader defect is discovered, explain it, version the correction, and rescore every affected strategy consistently. Freeze changes to the system require a new evaluation version. Publish negative results and missing-data limits. No synthetic result supports financial-loss, compliance, or productivity claims by itself.
