# H108: Goldstone wandering: the spontaneous room direction should drift, while a fielded one stays pinned

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH338; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH338 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11*/`

## Source HH (verbatim from the HH list, including refinements)
- **HH338 · Goldstone wandering: the spontaneous room direction should drift, while a fielded one stays pinned.** With no field, the direction of an ordered state costs no energy to rotate, so it diffuses (a Goldstone mode). With a field, it is pinned. H91 found that content modes rotate about 1 SD a day, but it did not compare fielded and unfielded rooms.
  - *Prediction:* the day-to-day angular diffusion of the room-difference direction Δ(d) is ≥ 2× larger in identical-kickoff periods than in #38 and #44 (room-specific kickoffs), after noise correction. Within identical periods, it scales as 1/(N_room |Δ|²).
  - *Check:* daily Δ(d), both models, style-residualized. Correct for noise with within-day split-half estimates. Compare with a relabel null.
  - *Kill:* identical-kickoff rotation ≤ fielded rotation. The "spontaneous" direction is then pinned like a field, and H100's residual is an unmeasured field.
  - *Impostors:* exogenous: the contrast is field vs no field. Priors: agent constants removed. Scheduler: n/a. Convergence: n/a (direction statistic).
  - *Models:* 11 · *Builds on:* H100, H91, H92

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
