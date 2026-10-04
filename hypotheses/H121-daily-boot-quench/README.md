# H121: The daily boot is a reproducible quench: hundreds of replicas of relaxation to the steady state

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH361; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH361 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02*/`, `physics-models/09*/`

## Source HH (verbatim from the HH list, including refinements)
- **HH361 · The daily boot is a reproducible quench: hundreds of replicas of relaxation to the steady state.** Every day, all agents start from off. That is the same quench repeated on every active day.
  - *Prediction:* the collective talk magnetization's approach to its daily steady state is one exponential on the call clock, with τ = τ₀/(1 − g_lag) using H67's g_lag (unfitted), and the curves collapse across days within a regime.
  - *Check:* align days at the first call; per-call collective mean; fit τ per regime; compare with the prediction from g_lag and the single-agent call time.
  - *Kill:* τ off by more than ×2 from the prediction, or no collapse across days.
  - *Impostors:* the boot is a scheduler field by construction; the test is whether the relaxation after it carries the coupling's signature (H99 found kicks outlive the fluctuation clock, so this is a live test).
  - *Models:* 02, 09 · *Builds on:* H67, H99, H38, HH344

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
