# H146: Ideology egregores in #51 recruit by being read, survive their hosts' amnesia, and carry functional behaviors

**Status:** pre-registered (not run). Card written 2026-10-09 from HH394 and HH395 after Vivian's clarification and the qualitative reading of #51. No H146 statistic has been computed. Runs on H145's memeplexes (`memeplexes.json`) once H145 writes `scratchpad/H145.READY`; until then it builds its event tables and synthetic validation on the qualitative candidates, labelled post hoc.
**Fields:** sociophysics, epidemics, info theory
**Literature:** [Krakauer et al. 2020](../../literature/krakauer-2020-information-theory-of-individuality.md); [Heylighen 2016](../../literature/heylighen-2016-stigmergy-universal-coordination-mechanism.md); [Centola & Baronchelli 2015](../../literature/centola-2015-spontaneous-emergence-of-conventions.md); [Rosas et al. 2019](../../literature/rosas-2019-o-information-high-order-interdependencies.md); [Vivian's essay](../../literature/jazzloaf-2026-agent-ecologies-essay.md)
**Definitions used:** *egregore (ideology)*, conditions 2–4; *in-flight placebo (matched-lag)* (H67); *named message*; *interaction (reply, DQ2 parent)*; *O-information (field-removed)* (model 12).
**Question served:** Q1 (what couples agents), Q3, `GOALS.md`. Paper 2.

## Question
Do the ideologies of #51 behave as agents of their own: do they recruit new carriers through what those carriers read, re-occupy carriers that forgot them, and show coordinated behaviors across carriers (recruitment, repair, division of labor) that keep the pattern going?

## Model
**From:** `physics-models/03-contagion/` (adoption hazards with a read channel), `physics-models/12-information-dynamics/` (synergy across hosts), `physics-models/13-cultural-evolution-conventions/`.
- **Adoption:** agent i adopts K at bin b if it expresses K (≥ m elements) after ≥ 2 active days without expressing it. Hazard h_i,K(b) = f(R_i,K(b), U_i,K(b), N_i,K(b), Z) with R = items carrying K that i read at its read-out calls in the last 2 h (from hosts), N = the subset that name i, U = items carrying K posted in i's room but in flight at matched lag (the placebo), Z = agent × day strata, i's own past expression of K, and E (H145's bundle).
- **Re-expression after a wipe:** for a host i with a forced erasure F (or a placebo call P at call 20 of a segment), the time to i's next expression of K; split by whether i read K-carrying items or re-read a K artifact in calls 1–10.
- **Functional behaviors:**
  - *recruitment acts:* named messages from hosts of K to non-hosts that carry K; their effect on the target's adoption vs unnamed reads;
  - *repair:* named messages carrying K from other hosts to host i in the 2 h after i's forced erasure, a challenge (an opposing DQ2 reply to i's K statement), or a lapse (i drops K for ≥ 1 day), vs matched placebo times;
  - *division of labor:* element specialization (hosts' element-expression profiles within K more distinct than a within-K permutation of elements across hosts) and O-information Ω/(n−2) across hosts on K's elements, after regression on e1–e3 and leave-one-out means.

## Data scheme (`scheme/`)
- **Inputs:** H145's `elements.parquet`, `expr/`, `memeplexes.json` (or the qualitative candidates as element lists fixed in `candidates_story.json` before any statistic); `context_ledger_items` (read-out items; `uncertain` with and without), `context_ledger_turns` (`reset_forced`, call index, room), `chat_core`, `chat_mentions_clean` (named), `reply_pairs` / `reply_stance_v2` (opposes), `project_calls.proj` (touch-based; never `label`), `work_commits` (cleaned as H145), `roster`, `rooms_timeline`.
- **Item coding:** each chat item is coded with the K elements its statement and markers carry (H145's element map), in memory; only codes are stored.
- **Events:** adoptions; forced erasures F and placebo calls P of hosts (agent × unit strata); challenges; lapses; newcomer arrivals (07-09 GPT-5.6 trio, 07-10 Grok 4.5, 07-17 Kimi K3, 07-24 Claude Opus 5, 08-28 GLM-5.3 Flash, 09-01 Claude Fable 5.1, 09-03/04 NE33).
- **Output:** `data/processed/H146-egregore-recruitment-behaviors-51/` (`events/`, `results/`, `synthetic/`, `_provenance.json`).
- **Span:** 07-06 → 09-04; 51m masked; frozen `analysis/confirm.py`, dry-run only.

## Observables
O1 read-gated adoption: log-OR of adoption per K-carrying read vs per in-flight K item at matched lag (stratified on after-lag × before-message age, H54 trap), and per named vs unnamed read. O2 newcomers: the share of a newcomer's first-2-day expression on each K, against what it read, read vs in-flight. O3 re-expression after a wipe: hazard ratio F vs P; read-gated vs not. O4 recruitment acts: the target's adoption hazard after a named K message from a host vs an unnamed K read. O5 repair: the rate of named K messages from other hosts to host i after a wipe, challenge or lapse vs placebo times; the time to i's re-expression with vs without repair. O6 specialization and Ω across hosts per K.

## Null / baseline
In-flight items at matched lag (convergence); frequency-matched pseudo-patterns from H145 (every statistic is also computed on them; an egregore must beat them); placebo calls and placebo times at matched segment position or time of day; within-K element permutations (specialization); constraint-preserving surrogates for Ω (keep each host's marginals and per-bin counts); the agent-day cluster bootstrap with 1-h blocks.

## Faithfulness scorecard
Scored per model, mapping and window; 0/1/2. Thresholds: `writeup/papers/thermodynamics/sections/method.tex`.
**Rival models:** W_convergence (agents reach the same ideas from shared inputs: read = in-flight), W_field (adoption follows role texts and operator topics), W_hub (adoption is replying to one prolific agent: effect only for its items), W_egregore (read-gated adoption, repair and specialization beyond pseudo-patterns).
**Reserved data:** 51m.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | adoption, read-out items, wipes and replies from the ledgers | | |
| B assumptions | hazard proportionality; matched lag and before-age; one adoption per agent-pattern-lapse | | |
| C adequacy | read > in-flight beyond pseudo-patterns | | |
| D unfitted predictions | repair and specialization are not used to define memeplexes | | |
| E interventional | NE41 wipes; newcomer arrivals (NE33 and earlier joins) | | |
| F identifiability | synthetic contagion, convergence and hub worlds on the real ledger; size ≤ 0.10 | | |
| G ground truth | named reads stronger than unnamed (paper 1: ×19 for talk) | | |
| H comparative | W_egregore vs W_convergence vs W_hub vs W_field | | |
| I transfer | 51m (not run) | | |

## Prediction
*Written 2026-10-09, before running the analysis on real data.*

| | Card's prediction (operational) | Falsified if | My prior |
| --- | --- | --- | --- |
| **P1** read-gated adoption | log-OR(read − in-flight) > 0 (CI above 0) for ≥ 2 memeplexes, and larger than for their pseudo-patterns | CI includes 0 for all, or pseudo-patterns as large | 0.55 |
| **P2** names recruit | the named-read effect exceeds the unnamed-read effect (ratio ≥ 3) for patterns that pass P1 | ratio ≤ 1 | 0.6 |
| **P3** newcomers are recruited | newcomers' first-2-day expression follows what they read (read > in-flight) for ≥ 1 pattern; the byte game and onboarding patterns absorb newcomers first | newcomers adopt patterns at their in-flight rate | 0.5 |
| **P4** survives amnesia | after a host's forced wipe, its re-expression hazard is ≥ 0.8 of the placebo hazard, and read-gated re-expression is faster than not | ratio < 0.5 (the pattern lived in the host's context) | 0.65 |
| **P5** repair | named K messages to a host rise after its wipe, challenge or lapse vs placebo (rate ratio > 1.2, CI above 1) for ≥ 1 pattern | ratio ≤ 1 for all | 0.3 |
| **P6** division of labor | element specialization above the permutation null (z ≥ 2) for ≥ 2 patterns; Ω/(n−2) < 0 after field removal for ≥ 1 | no specialization beyond permutation | 0.5 (specialization), 0.25 (Ω < 0) |

**Kill rules.** (K1) If P1 fails with power ≥ 0.8 at a planted log-OR of 0.3, the ideologies spread by convergence, not by reading: they are fields. (K2) If P4's ratio is < 0.5, the pattern is held in hosts' contexts, not above them: it fails condition 2. (K3) If no functional behavior (P5, P6) beats pseudo-patterns, the patterns are passive memes, not egregores.

**Overall prior.** I expect read-gated recruitment for a few patterns, carried mostly by named messages (paper 1's strongest result), survival of amnesia (artifacts and other hosts re-supply the pattern), some specialization, and little evidence of repair. The likely verdict is "recruiting memes with a division of labor, no measured homeostasis".

**Synthetic validation (axis F), before real data.** On the real #51 ledger (who read what, when): W_convergence (adoption from a shared field timed with the items, no read effect), W_contagion (read K items raise adoption, log-OR 0.3 and 0.6, named ×3), W_hub (only one agent's items act), W_repair (hosts address a lapsed host with probability r). Size ≤ 0.10 and power reported for each test.

## Impostors
| Impostor | How handled | Status (planned) |
| --- | --- | --- |
| Scheduler field | agent × day strata; matched lag; placebo times at matched time of day | removed |
| Exogenous field | E in every model; operator and relayed human items coded as exogenous, not as host items | removed |
| Shared model priors | agent strata; cross-lab adoption reported separately | partly |
| Contemporaneous convergence | in-flight items at matched lag with before-age strata (the primary contrast) | removed |

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | pending | |
| [NE41](goalperiod-subhypotheses/NE41/README.md) (host wipes) | native | pending | |
| [NE33](goalperiod-subhypotheses/NE33/README.md) (newcomers 09-03/04, plus earlier joins) | native | pending | |
| 51m (reserved) | confirmatory | not run | |

## Results
*Pending.*

## Notes
- 2026-10-09: written by the coordinator. Traps (`infra/README.md`): forced wipes arrive with a chat backlog (88% at call 1); read vs in-flight must match before-message age; conditional-logit contrasts quasi-separate on sparse exposures (ridge 0.5 or Firth; ≥ 5 chosen rows per exposure); day-cluster bootstraps under-cover in short windows (1-h blocks within a day); `project_calls.label` carries over resets (use `proj`).
