# H110: Exchange bias: an agent's own artifact shifts its goal-switch loop

**Status:** specified (approved by Vivian in the dashboard vetting panel 2026-10-04 from HH340; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH340 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/01*/`

## Source HH (verbatim from the HH list, including refinements)
- **HH340 · Exchange bias: an agent's own artifact shifts its goal-switch loop.** In a ferromagnet bonded to a pinned layer, the hysteresis loop shifts sideways. H100's GPT-5.4 kept its old room's content after a move while it kept its old project, and H70 found that agents return to their own repo after an erasure. If the own artifact is the pinned layer, agents with a live own repo at a goal boundary should carry a constant offset toward the old goal, and the offset should last as long as they still commit to that repo.
  - *Prediction:* at goal boundaries, the old-goal alignment of agents who committed to their own repo in the last 2 days of the old period decays ≥ 2× slower than for unpinned agents. The offset ends within a day of their last commit to that repo.
  - *Check:* H96's old-goal alignment series, split by pinning status from DQ4 `work_commits`. Use agent fixed effects across boundaries, so that the same agent is pinned at some boundaries and not at others. Confirmatory: NE24 (06-29, GitHub → GitLab, inside the holdout window) replaces the pinning layer, so the bias should vanish there.
  - *Kill:* pinned and unpinned decay rates are within 25% of each other.
  - *Impostors:* priors: within-agent contrast. Exogenous: same boundary, same kickoff. Scheduler: n/a. Convergence: n/a (individual carry).
  - *Models:* 01 (hysteresis), 11 · *Builds on:* H96, H70, H100, H58

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
