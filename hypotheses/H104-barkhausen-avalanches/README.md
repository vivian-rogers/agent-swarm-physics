# H104: Barkhausen avalanches when a field is stepped

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH330; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH330 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/01*/`, `physics-models/10*/`, `physics-models/14*/`

## Source HH (verbatim from the HH list, including refinements)
Barkhausen avalanches: switches come in bursts when a field is stepped. In a disordered ferromagnet a slowly ramped field flips spins in avalanches with power-law sizes; this is crackling noise in the random-field Ising model. Here the field steps are mid-period human messages and kickoffs, and the flips are agents switching project or topic.
  - *Prediction:* switch bursts after field steps have a heavy-tailed size distribution whose exponent sits near the mean-field random-field Ising value τ ≈ 1.5. Burst size grows with step size. Between steps, switches are Poisson.
  - *Check:* DQ4 and `project_states` switch times, burst sizes after each step, and a time-shuffled null that keeps the step times.
  - *Kill:* burst sizes are no heavier than the null, or bursts are as frequent between steps as after them.
  - *Models:* 01, 10, 14 · *Builds on:* H54, H75, H53, HH129

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
