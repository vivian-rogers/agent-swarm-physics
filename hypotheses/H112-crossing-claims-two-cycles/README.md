# H112: Crossing claims anti-coordinate: parallel updates make 2-cycles

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH343; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH343 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02*/`, `physics-models/10*/`

## Source HH (verbatim from the HH list, including refinements)
- **HH343 · Crossing claims anti-coordinate: parallel updates make 2-cycles.** In the Little model (all spins update at once), coupled spins can fall into period-2 oscillations that sequential updating never shows. In the village, two agents can switch to the same project within one read-out window without having read each other (a crossing, both messages in flight), or one after reading the other (sequential). H93 found that agents avoid occupied repos in #42 and #51.
  - *Prediction:* after a crossing co-switch, at least one of the two leaves the project within 5 calls ≥ 2× as often as after a sequential co-switch. Leaving is mostly mutual (a 2-cycle: both leave). Sequential co-switches stick (herding, H63).
  - *Check:* co-switches from `project_states` and DQ4 commits; crossing vs sequential classified from the ledger (each message's presence in the other agent's producing call); a time-shuffled null at matched lag.
  - *Kill:* departure rates are equal within CI.
  - *Impostors:* convergence: the in-flight vs read split is the design. Scheduler: matched lag. Exogenous: kickoff-named projects stratified. Priors: pair fixed effects.
  - *Models:* 02, 10 · *Builds on:* H93, H63, H40, H57

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
