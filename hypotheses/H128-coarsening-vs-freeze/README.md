# H128: Free kickoffs coarsen, named kickoffs freeze: a kinetic Potts quench

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH369; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH369 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/10*/`

## Source HH (verbatim from the HH list, including refinements)
- **HH369 · Free kickoffs coarsen, named kickoffs freeze: a kinetic Potts quench.** In a zero-temperature Potts quench, many small domains merge and the number of distinct domains falls as a power of time (coarsening). A strong field (a named project) skips coarsening and freezes at once. H75 found named kickoffs freeze instantly (slack 1.0–1.4) and free ones are slow (5–15).
  - *Prediction:* in free-kickoff weeks, the number of active projects falls as t^(−α) with α ≈ 0.3–0.5 over the first days; in named-kickoff weeks it drops to its final value within hours, with no power-law stretch.
  - *Check:* H94/H77 project tables; active projects per active hour from each kickoff; fit power law vs exponential vs step.
  - *Kill:* the free and named curves have the same shape.
  - *Impostors:* projects finish for exogenous reasons (deadlines); exclude finished-and-shipped projects from "merged" counts.
  - *Models:* 10 · *Builds on:* H75, H94, H93

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
