# H111: A fluctuation–response sum rule for talk: Fano factor = 1/(1 − g)²

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH342; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH342 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/09*/`, `physics-models/14*/`

## Source HH (verbatim from the HH list, including refinements)
- **HH342 · A fluctuation–response sum rule for talk: Fano factor = 1/(1 − g)².** In a branching process with gain g, the variance of counts in long windows exceeds Poisson by exactly 1/(1 − g)². H67 measured g from read-out responses (regime III median 0.13, maximum 0.39). If the read-out loop is the only source of talk clustering, the spontaneous Fano factor of trimmed talk counts must equal 1/(1 − g_lag)² with no free parameter. Any excess is a field.
  - *Prediction:* after DQ8 trimming and removal of c_×, the long-window Fano factor of per-unit talk matches 1/(1 − g_lag)² within 20% in ≥ 2/3 of regime-III units. Untrimmed, it exceeds the prediction: that excess is the scheduler field (H38).
  - *Check:* per-unit talk counts in windows ≫ t_read; compare with H67's per-unit g; block-shift null for the field part.
  - *Kill:* trimmed Fano still exceeds the prediction by ≥ 2× in most units. Talk then clusters by a hidden field or coupling that the read-out loop misses.
  - *Impostors:* scheduler: trimming plus c_×. Exogenous: human and kickoff windows excluded. Priors: n/a (count statistic). Convergence: g comes from read-gated responses only.
  - *Models:* 09, 14 · *Builds on:* H67, H86, H38, H03

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
