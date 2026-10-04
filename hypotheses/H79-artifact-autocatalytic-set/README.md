# H79: An artifact-only autocatalytic set

**Status:** specified (promoted 2026-10-04 from HH327 by Vivian; round 1 launching)
**Fields:** <to be filled by the round-1 agent>
**Literature:** <links to literature/*.md>
**Definitions used:** <terms from physics-models/DEFINITIONS.md, with variant names if any>
**From:** HH327 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("From the thermodynamics and origins-of-life notes") · **Models:** `physics-models/05-replicator-dissipation/`

## Source HH (verbatim from the HH list)
Is there an artifact-only autocatalytic set? Build session × repo reactions from `work_commits`, `artifact_mentions` and `artifact_commands_text`.
  - Catalysts are executed artifacts and automated streams.
  - The food set is platforms plus kickoff-named and pre-period artifacts.
  - Agents are excluded as catalysts, because they are operator-supplied.
  - Nulls: rewired and time-reversed catalysis.

  *Prediction:* the largest RAF covers ≤ 20% of work commits, and minimal sets of size ≥ 3 occur in ≤ 1/3 of periods. That would make HH244's automata mostly single cron jobs feeding their own repo, not a self-sustaining artifact layer.
  *Egregore-positive:* a RAF beyond the nulls that persists across member turnover.
  *Models:* 05 · *Builds on:* HH244, HH301, HH302 · *Literature:* OoLEN 2026 (RAF background; Hordijk–Steel to grab)

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
