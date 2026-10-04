# H85: Scaling of outputs with N

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH309; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH309 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/14*/`, `physics-models/02*/`

## Source HH (verbatim from the HH list, including literature refinements)
Urban-style scaling of swarm outputs with N, with exponents derived from H18 and H58. Fit Y = Y₀ N^β across the 71 units, with regime and goal-type covariates.
  - *Predictions:*
    - Messages: β ≈ 1, since each agent posts at its own call rate (H40).
    - Replies: β ≈ 1.34. Per-recipient replies scale as k · k^{−0.66} = k^{0.34} with k ∝ N, so N · N^{0.34}.
    - Committed work: β = 1.0 ± 0.1, the independent agent + own artifact unit (H58). Superlinear β > 1.1 (Bettencourt's 1.15) would be a collective benefit and an egregore-positive result; β < 0.9 would be coordination overhead.
    - Distinct repos touched: β ≈ 1 in own-artifact weeks and β < 1 in shared weeks (H06, H11).
  - *Kill for the consistency check:* reply β outside [1.15, 1.55] means H18's dilution law doesn't aggregate.
  - *Models:* 02, 05 · *Builds on:* H18, H40, H58, H06

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
