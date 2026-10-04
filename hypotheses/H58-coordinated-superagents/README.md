# H58: Effective superagents are coordinated agents plus their artifacts

**Status:** specified (promoted 2026-10-04 from HH176; round 1 waits for its data-quality inputs)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH176 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/04-semantic-information/`
**Data inputs (shared tables first):** DQ4 work ledger (artifact state), DQ3 behavior states, `project_states`, H01 round-2 measures

## Question
Which composite of agents and artifacts best predicts its own future (information-theoretic individuality and autonomy), and is it a set of behaviorally coordinated agents together with the artifact they work on?

**Vivian's scope (2026-10-04):** superagents should be identified by *coordinated behavior*, not by room. Candidate composites come from coordination (behavior-state synchrony, co-adoption, joint work on the same artifact, reply/stance structure), possibly spanning rooms; rooms are only one baseline partition. Builds on H01 round 2 (R4–R8).

**Starting point from H01 round 2 (2026-10-04):** no effective superagent was found among coordination-defined units (crews, synchrony, co-allocation and reply communities; rooms and labs as baselines). Allocation persists across nights and memory loss through artifacts, but single agents with their own artifacts out-persist every grouping (15/18 units), and no unit carries measurable KW semantic information or repairs itself beyond aggregation. The binary "advanced or not" macro-state had ≤ 7% power to see a group store. H58 should (i) use a unit state that encodes *which* artifact is worked on, (ii) search coordination-first over behavior states, co-adoption, reply threads (DQ2) and artifacts together, (iii) treat "agent + own artifact" as the null unit to beat, and (iv) use the context ledger's re-acquisition path after erasures to separate artifact-held from prompt-held information.

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)

- **Replication:** the common estimator on every eligible goal period (comparable phase-diagram points). Period README role: `replication`.
- **Period-native tests:** 2–4 goal periods (or NEs) whose setup gives special leverage for this question, each with its own observable, null, ground truth or intervention, its own dated prediction, and period-specific tooling where needed. Period README role: `native`.

## Model
**From:** `physics-models/<NN-slug>/`
<Which variant of that model this hypothesis uses, its parameters, and what it
predicts here. E.g. "SIS with spontaneous adoption field ε; λ, γ, ε fit per regime.">

## Data scheme (`scheme/`)
<How raw data becomes the processed dataset this hypothesis uses.>
- **Inputs:** <raw tables and fields>
- **Transform:** <steps>
- **Output:** `data/processed/H58-coordinated-superagents/` (<files and columns>)
- **Regimes covered:** <which time intervals; see physics-models/DEFINITIONS.md "Regime">

## Observables
<The quantities computed from the processed data that the model makes predictions about.>

## Null / baseline
<What you'd see if the effect isn't there. E.g. shuffled timestamps, model with β = 0, independent agents.>

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** <the models that predict differently here>
**Locked holdout used for confirmation:** <goal periods / NEs>

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | | |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | | |
| C adequacy | beats the null hierarchy, day-blocked held-out data | | |
| D unfitted predictions | unfitted statistics and the model's signature | | |
| E interventional | predicts the change across a natural experiment | | |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | | |
| G ground truth | agrees with known structure | | |
| H comparative | beats the named rivals | | |
| I transfer | holds in other same-mode periods, including the holdout | | |

## Prediction
*Written <YYYY-MM-DD>, before running the analysis on real data.*
<What the model predicts for the observables, and what result would count against it.>

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G<NN>](goalperiod-subhypotheses/G<NN>/README.md) | exploratory | | |

## Results
<Cross-period synthesis, filled in after analysis: how the result depends on mode, regime and rooms; heterogeneity across periods. Link to analysis/ and figures/.>

## Notes
<Dated notes, dead ends, decisions.>
