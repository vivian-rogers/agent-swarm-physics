# H55 × G51: maximize your private assigned role (2026-07-06 → 2026-09-04 non-holdout)

**Verdict:** mixed
**Role:** native
**Period:** regime III · mode I/K · 21 → 32 agents · one room (#general; #focus from 08-05) · 45 non-holdout days. Units 51a–51l (NE32, NE33 joins; NE38; NE43 drive withdrawal). The #51 tail (09-07 → 09-21) is locked holdout and not used.

## Why this period
The only period with norm-enforcing roles assigned by the operator, with ground truth and time bounds (DQ6 `ground_truth_labels`): Psychologist (Claude Haiku 4.5), Ethicist (GPT-5.1), Diplomats (DeepSeek-V3.2, GPT-5.6 Luna); H37's post hoc grouping adds the Performance coach (Claude Opus 4.8) and the Village helper (Gemini 3.8 Flash, from 09-04). The roles are a treatment label independent of the correction sensor, so they test the sensor's construct validity and the friction claim without circularity. H37 found, post hoc and with its own labels, that 10 of 13 antagonistic pairs involve these roles (OR 4.4).

## Prediction
*Written 2026-10-04 06:41 UTC, before any H55 statistic on this period.* Primary enforcer set E = {psychologist, ethicist, diplomat}; extended set E+ adds performance coach and village helper (reported). Role permutation among role holders (5,000), one-sided.
- **N51a (construct):** mean Jev correction rate c_j of E exceeds that of other role holders (p < 0.05). [0.45]
- **N51b (friction):** mean received field ν_j (ordered logit, DQ2 labels) of E exceeds that of other role holders (p < 0.05). [0.4]
- **N51c (negative pairs, calibrated):** among agent pairs significantly negative after agent fields (BH 0.1 on DQ2 hard labels), the number involving an E agent exceeds its expectation under the calibrated agent-field null (200 simulations; p < 0.05). [0.35] Not independent of H37's post hoc: DQ2 and H37 labels overlap in #51 (sign κ 0.75 on shared pairs).
- **N51d (immune by role):** directed reads *from* E agents raise loop or blocked-spell escape relative to matched directed reads from other agents (Δ_role > 0, p < 0.05). [0.2; expected underpowered]
- *Against:* E agents correct no more than others (the role is not enacted in chat), or draw no more negativity.

## Result
*Run 2026-10-04 (`analysis/native.py`, `analysis/explore.py`; data `data/processed/H55-norm-enforcer-immunity/G51/native.json`, `results.json`, `posthoc_activity.json`).* 32 agents with ≥ 20 sent and received labelled replies; 22,917 parented agent messages, 580 Jev corrections (2.5%).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| N51a enforcers (E) correct more | E − others: Jev correction rate −0.030 (soft score −0.041; E+ −0.039) | role permutation p_greater 0.90 | **fail** (E correct *less*) |
| N51b E receive more negative stance | ν(E) − ν(others) +0.11 (E+ +0.13) | p 0.36 (0.32) | **fail** (direction as predicted, n.s.) |
| N51c negative pairs concentrate on E | 16 significant negative pairs (agent-field null 0.19, p 0.005); 12 involve E (null 0.015, p 0.005); share 0.75 vs 0.31 of testable pairs | calibrated agent-field null, 200 sims | **pass**; *post hoc:* E agents are in 56% of all labelled replies, and against that reply-weighted share the concentration is p 0.09 |
| N51d immune by role | directed reads from E vs others: loops Δ +0.06 [−0.28, 0.47] (11 matched); blocked Δ +0.05 [−0.09, 0.17] (121 matched) | matched, agent-demeaned | **fail** (null; loops unpowered) |

**Replication numbers here:** P1 ρ(c_j, ν_j) = **−0.60** (32 agents; partial −0.26): agents who correct more receive *more positive* replies. P2 γ = −0.036 [−0.09, +0.015] (510 replies to corrections; p 0.20). P3: 71% of confident received opposes are correction/decline subtypes. Immune contrast, blocked spells (26 treated windows): Δ +0.055 (p 0.68). Loops: 3 of 420 at-risk steps had a correction read.

**Reading.** The assigned norm-enforcers do not issue more corrections in chat than other role holders (the role is enacted some other way, if at all), and their received stance is not significantly worse. The pair-level antagonism H37 saw is reproduced with DQ2's labels and beats the calibrated agent-field null, but it sits largely where the activity is: the four enforcers are in more than half of all replies. Not independent of H37 (overlapping labels).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | negative pairs beat the calibrated agent-field null; role contrasts do not beat role permutation |
| G ground truth | 0 | assigned enforcer roles do not show up as more corrections (N51a) |
| E interventional | 0 | NE38 not used (no enforcer role changes) |

## Notes
- Primary set E = psychologist, ethicist, two diplomats; E+ adds performance coach and village helper (the latter only on 09-04).
