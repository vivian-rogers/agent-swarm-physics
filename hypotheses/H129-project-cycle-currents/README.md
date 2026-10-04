# H129: Project hopping carries cycle currents: the sticky Potts walker breaks detailed balance

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH370; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH370 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02*/`, `physics-models/10*/`, `physics-models/15*/`

## Source HH (verbatim from the HH list, including refinements)
- **HH370 · Project hopping carries cycle currents: the sticky Potts walker breaks detailed balance.** H93 found habit dominates project choice (b_own 2.5–6 nats). A kinetic Potts walker with a habit field hops rarely. If hopping only followed a fixed attractiveness, the flows A→B and B→A would balance. Projects being born, finished and abandoned instead drive a net circulation (A→B→C→A).
  - *Prediction:* on agent project-transition triples, the cycle affinity ln(P_ABC/P_CBA) is nonzero in shared-goal weeks, with the circulation running from older to newer projects. Dwell times are geometric with a rate that falls with habit.
  - *Check:* transitions between projects per agent in H93's choice table; cycle affinities with a time-reversal null.
  - *Kill:* cycle affinities within the reversal null.
  - *Impostors:* project age is a drift field by construction; that is the claimed mechanism, so the test is whether the circulation exceeds what age-ordering alone gives in a synthetic walker.
  - *Models:* 02, 10, 15 · *Builds on:* H93, H94, H56, HH56

## Question
<What do you want to know, in one or two sentences.>

## Model
**From:** `physics-models/<NN-slug>/`
<Which variant of that model this hypothesis uses, its parameters, and what it
predicts here. E.g. "SIS with spontaneous adoption field ε; λ, γ, ε fit per regime.">

## Data scheme (`scheme/`)
<How raw data becomes the processed dataset this hypothesis uses.>
- **Inputs:** <raw tables and fields>
- **Transform:** <steps>
- **Output:** `data/processed/H<NN>-<slug>/` (<files and columns>)
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
