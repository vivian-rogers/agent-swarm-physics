# H37: Conflict lives in stance, not topic: stance spins are antiferromagnetic

**Status:** exploratory round 1 **done (2026-10-04): detector validated on assigned conflict; the generalization failed.** Zero-shot stance labels see the #12 debate teams that topic embeddings cannot (AUC 0.74 vs 0.48; teams recovered exactly in 7/10 debates), but find no stance antagonism between rival or opposed roles in #51 or between voting blocs in #26. Observables, nulls and predictions written 2026-10-04 01:35 UTC, before any stance label of an analysed pair was looked at or any outcome statistic computed. `analysis/confirm_g34.py` (#34 saboteurs) written and dry-run, **not run**.
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH125 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`); leads from H22 (51a Prankster pairs), H21 (#12 stance tilt, HH127), H11 G26 (votes).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population; Regime; Agent state, variant categorical (debate team, #51 role, #26 vote set). Two named variants of **Interaction**, proposed for the shared file: *interaction (addressed reply, 30 min)* and *interaction (adjacent reply, 5 min)* (defined under Data scheme). New terms defined below and proposed for the shared file: *stance spin*, *stance coupling*, *frustration index (ground-state)*. H22's *balance index τ₃* and its double-centred version τ₃(dc) are used exactly as H22 defined them (`../H22-private-goals-spin-glass/README.md`, O4 and Amendment 1).

## Question
H22 found that in #51 rivals co-move in *topic* (content embeddings), so topic coupling cannot see conflict. Does conflict appear in *stance*, the sign of how one agent's reply treats another's message (agree / support vs oppose / undermine)? If so, a signed reply graph built from stance labels should carry negative couplings where conflict is (debate opponents in #12; opposed or rival roles in #51; electoral rivals in #26), and its frustration and balance should say whether conflict is factional (two camps) or diffuse. Practical aim (usefulness-first batch): a conflict and faction detector an operator can compute from chat logs with a cheap zero-shot labeller, with measured accuracy, and a saboteur-detection design for #34 (holdout, D8.3).

## Model
**From:** `physics-models/01-inverse-ising` (signed couplings, frustration, Mattis/balanced states) and `physics-models/10-potts` (communities as Potts ground states; q-faction generalization).

### The magnet dictionary (H37 variant)
| Magnet | Village | Dataset fields |
| --- | --- | --- |
| bond variable s_e ∈ [−1, 1] | the stance of one reply e: agent j's message B toward agent i's earlier message A | Jev probabilities: s_e = p(agree) + p(support) − p(oppose) − p(undermine); hard version σ_e ∈ {+1, 0, −1} |
| coupling J_ij | how i and j treat each other on average | mean of s_e over replies in both directions (n_ij ≥ 3) |
| agent fields a_j, b_i | j's agreeableness as a replier; how i is treated by everyone | two-way fixed effects (speaker, target), removed by double-centring |
| faction spin ξ_i ∈ {±1} (Potts σ_i ∈ 1..q) | which camp i is in | ground state of H(ξ) = −Σ_{i<j} J_ij ξ_i ξ_j (signed Potts for q > 2) |
| frustration | antagonisms that no two-camp split explains | unsatisfied |J| weight in the ground state |
| balance (Mattis) | conflict is factional: friends within camps, enemies across | τ₃ ≈ 0.5 (heterogeneous balanced) to 1 (uniform), τ₃(dc) ≈ 0.45 for factions, ≈ 0 for random signs |

**Generative model** (used for the synthetic validation and as the reading of the estimators): for reply e from j to i, a latent stance y_e = μ + a_j + b_i + Δ ξ_i ξ_j + ε_e, ε logistic; the observed class is − / 0 / + by two cut points (ordered logit). Then label noise through Jev's measured confusion matrix. Δ > 0 is a balanced (Mattis) antiferromagnet across camps; random-sign pair terms J_ij in place of Δ ξ_i ξ_j give a frustrated (SK-like) graph; Δ = 0 with heterogeneous a, b is the "agent field" null.

**Why stance is a bond, not a site variable.** In H21/H22 the spin was an agent's content vector, and conflict had to show up as anti-alignment of positions. Here the spin is the sign of an interaction itself, so the coupling is measured directly rather than inferred from co-movement. That removes H22's main confound (rivals share a niche and so co-move) but adds two others: agents' general agreeableness (an agent field on bonds) and LLM politeness (a uniform positive field).

## Data scheme (`scheme/`)
Shared tables only (`infra/README.md`): `chat_core`, `chat_mentions_clean` (o1-bug-free, `mentions_roster`), `chat_text` (in memory only, sent to Jev), `roster`, `embeddings/chat_bge_small` + per-regime whitener. H21's verified #12 team labels (`../H21-debate-antiferromagnet/scheme/labels/g12_debates.json`), H22's #51 role coding (`../H22-private-goals-spin-glass/scheme/role_relations.py`) and H11's #26 declared votes (`data/processed/H11-potts-labor-vs-herding/G26/votes.parquet`) are imported, never modified.

1. **`scheme/build_pairs.py`** → `data/processed/H37-stance-spins/pairs/G<NN>.parquet` (codes only). A reply pair (A → B): B an agent message, A an earlier agent message by a different agent in the same room.
   - **Interaction (addressed reply, 30 min):** B names agent i (`mentions_roster`, i ≠ speaker of B); A = i's latest message in B's room within 30 min before B.
   - **Interaction (adjacent reply, 5 min):** A = the latest message by any other agent in B's room within 5 min before B.
   - A pair found both ways is kept once (kind = both). Also stored: lag, and the **topic cosine** of A and B (bge-small, per-regime whitened, n = 32).
   - Counts (non-holdout): #12 7,002 pairs (2,763 inside debate windows); #26 4,889; #51 68,675 (36,515 mention/both); #40 2,828.
2. **`scheme/label_stance.py`**: Jev (`typesafe/jev-1.13` on OpenRouter; API pattern, model and key loader imported from `infra/behavior_states/label_windows.py`). Jev sees only the two messages (A ≤ 800 chars; B ≤ 1,000 chars around its first mention of A's author) and the two display names. No team, role, vote or period information. Questions: stance (agree / support / neutral / oppose / undermine) and responds (does B engage with A?). Stored: probabilities and codes only. Hard spend cap $2.00 (script cap $1.90, summed over all runs).
   - **What gets labelled:** all pairs of #12, #26 and #40; in #51 the mention/both pairs, capped at 40 per unordered agent pair per H22 unit (51a–51e), sampled at random (seed 20261004): ≈ 15.5k pairs. Adjacent pairs in #51 (20+ agents in a room) are too ambiguous to be worth the spend.
3. **Validation:** a blind sample of 60 pairs (stratified by period and kind) labelled by Claude without seeing Jev's answers; Cohen's κ on the sign (+ / 0 / −) and on the 5 classes, and the confusion matrix that feeds the synthetic noise model.

**Output:** `data/processed/H37-stance-spins/` (`pairs/`, `labels/`, `validation/`, `G<NN>/`, `synthetic/`), `_provenance.json`. No message text is written anywhere.

## Candidate goal periods
| Period | Role | Why |
| --- | --- | --- |
| #12 (2025-09-01 → 09-08, regime I, 7 agents, 1 room) | positive control | 10 debates with verified, re-drafted teams: the rules force cross-team disagreement |
| #51 non-holdout (07-06 → 09-04, regime III, 32 agents, 4 rooms) | main test | private roles, some opposed (Prankster × Ethicist / Psychologist) or rival (same role); H22 found rivals co-move in topic |
| #26 (2026-01-05 → 01-12, regime I, 10 agents, 1 room) | election | approval vote, three-way tie, runoff (H11 G26) |
| #40 (2026-05-04 → 05-08, regime III, 15 agents, 3 rooms) | false-alarm contrast | a shared-objective consensus week with no assigned conflict |
| #34 (🔒 holdout) | confirmation only | hidden saboteurs; `analysis/confirm_g34.py` written, not run |

## Observables
*Written 2026-10-04 01:35 UTC, before any real-data outcome. What I had seen: pair counts per period, kind, #51 role class and unit (sampling design); the #12 debate windows and team line-ups (H21's labels); H11's vote-declaration table structure; and the Jev answers for 4 smoke-test pairs from #40 (all "neutral"; no relation information).*

**O0. Stance labels and their accuracy.** Per pair: soft stance s_e and hard class. Validation: κ (sign and 5-class) against Claude's blind labels on 60 pairs; confusion matrix.

**O1. Relation contrast (reply level, agent-adjusted).** For a period with a relation label r_e per reply (same / opposite team; role class; vote similarity):
- γ̂ from OLS s_e = μ + a_speaker + b_target + γ · 1[r_e = same] + ε over replies with r ∈ {same, opposite} (two-way fixed effects absorb agreeableness and likability).
- Also the raw means s̄(same), s̄(opposite) and the negative share f_neg (hard class oppose or undermine).
- Null: relation-label permutation within the structural unit (N1), 5,000 draws.

**O2. Topic contrast on the same pairs ("beyond topic").** The same γ̂ with the topic cosine as the outcome; AUC of agent-adjusted stance vs agent-adjusted topic cosine for telling same from opposite; and γ̂(stance) with topic cosine as a covariate.

**O3. Signed graph.** J_ij = mean s_e over replies between i and j (both directions; n_ij ≥ 3; missing = 0 in traces).
- Negative-pair share p_neg; pairs significantly negative after removing agent fields (BH-FDR 0.1, per-pair t on double-centred reply residuals).
- **Frustration index (ground-state):** f_gs = fraction of |J| weight unsatisfied by the best two-camp split (exact enumeration for N ≤ 20, else 200-restart descent; `h22lib.gs_frustration`), against the sign-shuffle null; triangle frustration F against the same null.
- **Balance:** τ₃ and τ₃(dc) (H22), cross-fitted on three folds (day folds where a unit has ≥ 6 days, else folds of whole conversations: replies grouped by B's 10-min block), day/block bootstrap CI.

**O4. Faction recovery.** ξ̂ = ground state of the double-centred J. #12: per debate, debaters only, accuracy against the true teams (up to a global flip); chance from all balanced partitions of that debate's line-up. #26: ARI against vote blocs (descriptive). The same on the **topic graph** (mean topic cosine per pair, double-centred).

**O5. #51 role treatment.** `h22lib.treatment_test` on J^stance (pair rule n_ij ≥ 3 replies): T_OP, T_SR, T_SY, T_NC = class mean − U mean, raw and same-lab-adjusted, role permutation among role holders (5,000). The same on J^topic (mean topic cosine per pair, the same replies). Pooled over non-holdout #51 (roles per agent = majority role over its present days), and per counted H22 unit (51b, 51c, 51d) as robustness.

**O6. Operator-facing detector metrics** (computed identically in every period): conflict level f_neg; count of significantly negative pairs (O3); faction score = best-split satisfied weight vs the sign-shuffle null; per-agent "received" and "given" residual stance z-scores (saboteur / scapegoat flags at z < −2).

**O7 (HH127, secondary).** #12: γ̂ in the post-verdict window vs during the debate.

**Multiplicity.** Seven primary tests (P1, P2, P3, P6, P7, P10, P12 below); Holm across them for the headline. Everything else is descriptive.

## Null / baseline
*Written 2026-10-04 01:35 UTC, before any real-data run.*
- **N1 relation permutation:** team labels re-drawn within each debate (sizes and judge fixed); #51 roles permuted among role holders (multiplicities fixed); #26 vote sets permuted among voters.
- **N2 sign shuffle:** magnitudes kept, signs permuted across pairs (frustration, faction score).
- **N3 agent fields:** two-way fixed effects (speaker agreeableness, target likability) or double-centring. Conflict must survive them: an argumentative agent is not a faction.
- **N4 topic:** stance must separate relations where topic cosine does not, and survive topic cosine as a covariate.
- **N5 label noise:** the synthetic runs give the detection floor and the false-positive rate at Jev's measured accuracy.
- **N6 family:** same-lab residualization (as H22); family style is the dominant content field (H13).
- **Uniform politeness field:** LLM replies lean positive, which shifts every J up (ferromagnetic τ₃). Absolute negativity (s̄ < 0) and relative negativity (after double-centring) are reported separately.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** topic coupling (H22: conflict invisible, rivals co-move); agent fields only (agreeable vs argumentative agents, no pair structure); uniform politeness field (everyone agrees); frustrated random antagonism (SK-like signs) vs balanced factions (Mattis).
**Locked holdout used for confirmation:** none yet. `analysis/confirm_g34.py` targets #34 (written, dry-run on #33 and #26 stand-ins, not run). #34 is already targeted by the unrun confirm scripts of H01, H05, H07, H12, H19 and H21: H37's observable (Jev stance labels on reply pairs) is a different modality that nobody has computed on #34, and H37 shares H21's saboteur ground-truth rule (a label, not an observable). Disclosure needed in H21's card and LOG.md (see the round-1 report).
**Overall A–I:** A1 B1 C1 D1 E1 F1 G1 H1 I0 (not promoted).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Reply pairs from clean mentions and adjacency; stance from a zero-shot labeller validated against blind labels (κ_sign 0.67 random sample; 0.37 enriched; 0.56 population-reweighted). Jev's negative calls are only 30% precise. Invariance across model families of writing style (e.g. procedural "I will wait" messages) not checked. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Assumption audit found that agent fields are not additive on ordinal labels, which makes the sign-shuffle faction null and the per-pair FDR anti-conservative (S6); replaced by a parametric ordered-logit agent-field null (Amendment 2; size 0.04 at #40's structure). Reply independence assumed within pairs; stationarity within debates assumed. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | #12: beats within-debate team permutation, agent fields and topic (p = 0.0002). #51: negative pairs beat the calibrated agent-field null (10 vs 0.33, p = 0.005), camps do not. #26 and #40: nothing beyond the nulls. No held-out days. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Per-debate team recovery from the stance graph (unfitted): 0.89, exact in 7/10; balance below the sign-shuffle null; post-verdict relaxation predicted (P5). Role-class predictions in #51 (P6, P7, P9) and the ballot prediction in #26 (P10) failed. |
| E interventional | predicts the change across a natural experiment | 1 | The verdict is a dated switch inside #12: the predicted drop of the team contrast after it is observed (γ̂ 0.42 → 0.03). No village-level NE tested. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic at the real reply graphs with measured label noise (S1–S6): team contrast detectable from Δ ≈ 0.5 logit; camps recovered with accuracy 0.91–1.0 at ±0.5 logit; τ₃(dc) separates camps from random signs at #51 size but is unstable on real residual graphs. Robust to pair construction, relevance filter and hard vs soft labels. One labeller, one validation rater. |
| G ground truth | agrees with known structure | 1 | #12 verified teams recovered (2 for this period). Assigned rivalries and oppositions in #51 and ballots in #26 are not visible in stance (0 for those). |
| H comparative | beats the named rivals | 1 | Beats the topic-coupling rival and the agent-field rival in #12. In #51 the homophily rival wins: rivals are friendlier in stance as well as closer in topic. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Does not transfer from the debate to roles (#51) or the election (#26); #34 not run. |

## Prediction
*Written 2026-10-04 01:35 UTC (2026-10-03 PT), before running the analysis on real data. Credences in brackets.*

**#12, positive control** (replies with B inside a debate's speech window [first speech, verdict) and both authors among that debate's debaters):
- **P1 (assigned conflict is negative in stance):** s̄(opposite) < 0 < s̄(same), and γ̂ > 0 with N1 p < 0.01. *Against:* γ̂ ≤ 0 or p > 0.05, i.e. the labeller cannot see forced disagreement. [0.85]
- **P2 (beyond topic):** AUC_stance(same vs opposite) ≥ 0.65 while AUC_topic ∈ [0.40, 0.60]; γ̂(stance) keeps p < 0.01 with topic cosine as covariate. *Against:* topic separates the teams as well as stance does. [0.7]
- **P3 (faction recovery):** the ground state of each debate's double-centred stance graph recovers the teams with mean accuracy ≥ 0.80 over debates, above random balanced partitions (p < 0.05); the topic graph does not (p > 0.05). [0.55]
- **P4 (balance, descriptive):** pooled debate graphs have f_gs below the sign-shuffle null. [0.6]
- **P5 (HH127, descriptive):** γ̂(post-verdict) < γ̂(debate). [0.6; a sign flip 0.3]

**#51, unassigned conflict:**
- **P6 (opposed objectives):** T_OP(stance) < 0, role-permutation p_less < 0.05, same-lab-adjusted. [0.3; 2 role pairs, low power]
- **P7 (rivals: stance vs topic dissociation):** T_SR(stance) < 0 with p_less < 0.05, while T_SR(topic) on the same pairs is ≥ 0 (H22's direction). *Against:* T_SR(stance) ≥ 0, i.e. rivals are not antagonistic in stance either. [0.2]
- **P8 (descriptive prior):** the graph is ferromagnetic overall: f_neg < 0.10 of replies, raw τ₃ > 0.5. [0.8]
- **P9 (descriptive):** significantly negative pairs (O3) are enriched in OP ∪ SR ∪ NC pairs (odds ratio ≥ 2, Fisher p < 0.05). [0.2]

**#26, election:**
- **P10 (stance tracks votes):** J^stance correlates with voters' vote-set similarity (Jaccard of their declared candidate sets; Mantel test with agent permutation, r > 0, p < 0.05), and more strongly than J^topic does. [0.3]
- **P11 (descriptive):** pairs of rival candidates (each named by ≥ 2 distinct voters in first-person declarations) have lower stance than other pairs (N1 p < 0.05). [0.25]

**#40, false-alarm contrast:**
- **P12 (no false alarm):** f_neg(#40) ≤ ½ f_neg(#12 opposite-team pairs); at most one significantly negative pair (FDR 0.1); faction score not significant (p > 0.05). [0.7]

**Hypothesis-level verdict rule:**
- **Supported (exploratory):** P1 and P2 pass (stance sees assigned conflict beyond topic), *and* at least one of P6, P7, P10 passes (stance finds conflict nobody assigned).
- **Detector validated, generalization not shown:** P1 and P2 pass, none of P6, P7, P10.
- **Failed:** P1 fails: zero-shot stance cannot even see forced debate disagreement.

**My credence before data:** supported 0.25; detector validated only 0.5; failed 0.15; other 0.1.

### Amendment 1 (2026-10-04 01:39 UTC, before any outcome statistic; from reading the 60 blind validation pairs, before Jev labelled them)
1. **Debater-adjacent pairs for #12.** In the 20 debate-window validation pairs the adjacent "reply" of a speech is usually the judge's call to speak, and most debate-window messages are procedural ("I will wait for …"). Added `scheme/build_debate_pairs.py`: for each message B by a debater inside a debate window, A = the latest message by a *different debater of the same debate* (judge and bench excluded; teams not used) within 10 min. 883 such pairs already existed; 207 are new (`pairs/G12_debater.parquet`). P1–P3 use the union of all #12 pair kinds, as before; a debater-adjacent-only variant is reported as robustness.
2. **Enriched second validation sample.** My random 60 contain only 2 negatives (2 oppose, 15 agree/support, 43 neutral), too few to estimate accuracy on the class the hypothesis is about. After Jev runs, I will label a second blind set of 45 pairs drawn equally from Jev's negative, positive and neutral predictions, shuffled so that I do not know any item's stratum. Per-class precision comes from it directly; recall and κ are reweighted by the strata's population shares. Both sets are reported.
3. **Relevance filter.** Primary analyses use pairs with Jev's responds probability ≥ 0.5 (as written); all-pairs results are reported alongside.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G12](goalperiod-subhypotheses/G12/README.md) | exploratory (positive control) | supported | debate replies: stance same +0.32 vs opposite −0.13, γ̂ 0.42 (p 0.0002); AUC 0.74 (stance) vs 0.48 (topic); team recovery 0.89, exact 7/10 (topic 0.71, chance 0.70); contrast gone after the verdict (γ̂ 0.03) |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | failed | T_SR(stance) +0.085 (p_less 0.81; topic +0.078), T_OP +0.02 (2 pairs, both positive); 10 negative pairs vs 0.33 expected (calibrated p 0.005), none in conflict classes; camps not beyond agent fields (p 0.36); post hoc: 10/13 negative pairs involve norm-enforcing roles |
| [G26](goalperiod-subhypotheses/G26/README.md) | exploratory | failed | stance vs ballot similarity r = 0.01 (p 0.47; power 0.25–0.42 at 1–2 logit); rival-candidate test untestable; no negative pairs, no camps (p 0.91) |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory (contrast) | mixed | no negative pairs, no camps (calibrated p 0.73): no structural false alarm; but 20% of replies labelled "oppose" (task corrections plus label noise), so P12's conflict-level clause fails |

## Results
*Round 1, 2026-10-04. Code: `scheme/` (pairs, labels, samples), `analysis/explore.py` (per period), `analysis/validate.py`, `analysis/synthetic.py`, `analysis/calibrate.py`, `analysis/figures.py`, `analysis/confirm_g34.py`. Data: `data/processed/H37-stance-spins/` (`summary.json`, `G<NN>/results.json`, `validation/`, `synthetic/results.json`, `calibration*.json`). Figures: `figures/summary.pdf` (one-page figure summary), `figures/summary_obs.pdf`, `figures/summary_obsb.pdf`, and `goalperiod-subhypotheses/G*/figures/`.*

**Headline.** Stance labels are a working sensor for *assigned, explicit* conflict and a poor one for anything else in this village.
- In the #12 debates, reply stance separates opponents from teammates (AUC 0.74 after agent effects) while the same reply pairs are equally similar in topic (cosine 0.53 vs 0.54; AUC 0.48). The best two-camp split of each debate's stance graph recovers the drafted teams exactly in 7 of 10 debates; the three misses are the three smallest debates (29–49 replies). The contrast switches off within 10 min of the verdict.
- Where nobody assigned sides, the swarm shows almost no stance conflict. Same-role rivals in #51 are, if anything, friendlier than unrelated pairs (and closer in topic, as H22 found); the Prankster is on good terms with the Ethicist and the Psychologist; #26 voters' stance does not track their ballots.
- The negativity that exists is diffuse: #51 has 10 agent pairs more negative than agent fields predict (0.33 expected), none in a conflict-coded role pair. Post hoc, 10 of 13 involve a norm-enforcing role: governance friction, not rivalry.
- In the HH125 terms: stance couplings are antiferromagnetic exactly where a protocol forces opposition, and nowhere else. "Conflict lives in stance" holds for debates; in the rest of the village there is little conflict to live anywhere.

### Outcome vs prediction
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 #12 opponents negative, teammates positive, γ̂ > 0 (p < 0.01) | +0.32 vs −0.13; γ̂ 0.42, p 0.0002 (Holm 0.0006) | **pass** |
| P2 #12 beyond topic: AUC_stance ≥ 0.65, AUC_topic in [0.40, 0.60], survives topic covariate | 0.74 vs 0.48; p 0.0002 with covariate | **pass** |
| P3 #12 camp recovery ≥ 0.80 (p < 0.05), topic graph not | 0.89 (p < 10⁻⁴), exact 7/10; topic 0.71 (p 0.46) | **pass** |
| P4 #12 balance (descriptive) | unsatisfied weight 0.08 vs sign-shuffle 0.14 (p 0.0015) | pass |
| P5 #12 contrast drops after the verdict (descriptive) | γ̂ 0.42 → 0.03; opponents' stance −0.13 → +0.36 | pass (relaxation; no flip, so HH127's remanence is not seen in stance) |
| P6 #51 T_OP(stance) < 0 | +0.02 (p_less 0.55; 2 pairs) | fail |
| P7 #51 T_SR(stance) < 0 while topic ≥ 0 | stance +0.085 (p_less 0.81), topic +0.078 | fail (homophily rival) |
| P8 #51 ferromagnetic overall (descriptive) | f_neg 0.091, τ₃ 0.75 | pass |
| P9 #51 negative pairs enriched in conflict classes | 0 of 13 (Fisher p 1) | fail |
| P10 #26 stance tracks ballots | r 0.01 (p 0.47) | fail (low power) |
| P11 #26 rival candidates lower (descriptive) | untestable: every agent was a candidate | n/a |
| P12 #40 no false alarm | no negative pairs, no camps; f_neg 0.20 > ½ × 0.26 | mixed (fails on f_neg) |

**Verdict by the card's rule:** P1 and P2 pass; none of P6, P7, P10 pass → **detector validated, generalization not shown.** Holm-adjusted primary p: P1 0.0006, P2 0.0006, P3 0.0003, P6 1, P7 1, P10 1.

### Label validation (O0)
- Blind Claude labels, written before seeing Jev's answers: a random 60 (stratified by period) and an enriched 45 (15 each from Jev's −/0/+ calls, strata hidden while labelling).
- Random 60: κ_sign 0.67 (agreement 0.83), 5-class κ 0.58; responds κ 0.47. Enriched 45: κ_sign 0.37.
- Precision of Jev's calls: negative 0.30 (6/20), neutral 0.96, positive 0.65. Jev labels 8.9% of replies negative; the blind labels put the true rate near 5%. Many Jev "opposes" are task corrections, polite declines or status contradictions.
- Population-reweighted P(Jev | true): recall 0.56 (−), 0.73 (0), 0.89 (+); κ_sign 0.56. This matrix is the synthetic noise model. The label-noise floor (Jev "negative" rate with no true negatives) is ≈ 0.065.

### Synthetic validation (axis F; real reply graphs, measured label noise)
- **S1 (#12):** the team contrast test has size 0.005 and power 0.90 at Δ = 0.5 logit (0.28 at 0.25; 1.0 at 1.0); camp recovery 0.79 / 0.88 at Δ = 0.5 / 1.0 (chance 0.70). The real #12 values (γ̂ 0.42, recovery 0.89) correspond to Δ ≈ 1 logit or more.
- **S2 (#51 roles):** with Jev noise, power for T_SR is 0.53 at a pair term of −1 logit and 0.95 at −2; T_OP (2 pairs) 0.05 / 0.40. So P7's failure excludes strong rival antagonism (≥ 1–2 logit), not weak; and the observed T_SR is positive.
- **S3 (balance):** τ₃(dc) separates two-camp from random-sign couplings at #51 size (0.74 vs 0.0; 25% misclassification of random signs at Δ = 0.5 with Jev noise). On real residual graphs it was unstable (#51 CI −0.9 to 29; negative at #26's N = 10), so it is reported, not used.
- **S4 (#26 ballots):** Mantel power 0.25 / 0.42 / 0.83 at 1 / 2 / 4 logit.
- **S5 (saboteur design):** per-agent-day suspicion AUC 0.81 if saboteurs receive −1 logit stance, 0.81 if they give −1 logit (combined score 0.71 for one channel only, 0.89 for both); null 0.50.
- **S6 (detector false alarms):** with the sign-shuffle null, the camp test fires in 10% (#12, #26), 28% (#40) and **100%** (#51) of agent-field-only simulations; ≥ 1 "significant" negative pair in 0–63%. Both nulls are invalid on residual stance graphs → Amendment 2.

### Amendment 2 (2026-10-04, post hoc, after S6 and after the first real-data run; disclosed)
The detector's camp and negative-pair statistics are compared with a **parametric agent-field null**: an ordered logit with speaker and target effects fitted to each period's hard labels, simulated 200 times on the real reply structure (`analysis/calibrate.py`). Its own size and power at #40's structure: size 0.04 (camps) and 0.00 (pairs); power 1.0 for two camps at ±0.5 logit; 0.12 / 0.08 for three isolated antagonistic pairs at −1 logit. At #51's structure: size 0.04 (camps) and 0.00 (pairs); power 1.0 for camps at ±0.5 logit; 0.08 / 0.08 for three isolated antagonistic pairs (`calibration_check.json`; 25 null and 12 camp datasets, 40 bootstrap replicates each). Calibrated results: #12 whole period camps p 0.01, 2 negative pairs vs 0.03 expected; #26 p 0.91, 0 pairs; #40 p 0.73, 0 pairs; #51 camps p 0.36, 10 pairs vs 0.33 (p 0.005). The pre-registered sign-shuffle values are kept in the G folders.

### Operator-facing detector (round-1 spec)
1. **Reply pairs** from chat logs: addressed replies (B names A's author within 30 min) plus adjacent replies (5 min; exclude moderator or judge calls where known).
2. **Stance** with a zero-shot labeller (Jev stance-v1; $0.037 per 1,000 pairs; 30k pairs labelled for $1.12). Keep pairs the labeller says respond (p ≥ 0.5); soft stance s = p(agree) + p(support) − p(oppose) − p(undermine).
3. **Agent fields**: fit an ordered logit with speaker and target effects; work with residual pair stance J_ij.
4. **Alarms**, each against the parametric agent-field null (alarm above its 95th percentile):
   - *antagonistic pairs*: pairs whose residual stance is significantly negative; report the count against the null count;
   - *factions*: the ground-state two-camp split of the residual graph and its satisfied-weight score; report the split;
   - *scapegoat / aggressor*: agents with received or given residual stance z < −2.
5. **Never alarm on the raw negative share alone**: subtract the label-noise floor (≈ 0.065) and read it as correction friction unless the structural alarms agree.

**Measured accuracy.** On ground truth (#12): per-reply team relation AUC 0.74; per-debate camp recovery 0.89, exact for every debate with ≥ 82 replies (7/7). Synthetic, at real reply graphs with measured label noise: camp power ≈ 1.0 at ±0.5 logit with calibrated size 0.04; camp accuracy 0.91–1.0. Real cooperative weeks (#26, #40): no structural false alarm. Weak spots: Jev's negative calls (precision 0.30) and isolated antagonistic pairs (power ≈ 0.1 for three −1-logit pairs at #40's and #51's sizes).

### Caveats
1. **One labeller, one rater.** κ is moderate, and my blind labels define "truth"; a second human or model rater is needed. Jev over-calls "oppose" on corrections.
2. **Debate speeches address teams, not people.** Many debate rebuttals name no opponent and follow the judge's call, so the reply graph undersamples the real exchange (Amendment 1 partly fixes this).
3. **Small graphs.** N = 7–14 outside #51; balance indices are unstable there, and the per-pair tests needed calibration.
4. **Power.** #51's role tests rest on 6 rival and 2 opposed pairs; #26 has 10 agents. Failures exclude strong effects only.
5. **Post hoc.** The governance-friction reading of #51's negative pairs (OR 4.4, p 0.016) and Amendment 2 came after the data.
6. **Topic baseline** is one embedding model (bge-small, whitened); H21 used masked text for #12.
7. No message text was stored; only codes and probabilities. Agent narration was not used as ground truth (labels are about how B treats A, not what B claims).

## Confirmatory test (#34, written 2026-10-04, not run)
*`analysis/confirm_g34.py`; refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`; dry-run on non-holdout stand-ins (#33 label rule; #26 detection with seeded stand-in saboteurs: null AUC 0.50, planted −0.1 / −0.3 soft stance → AUC 0.77 / 0.96).*
- **Pairs and labels:** the same two constructions and Jev prompt on #34 (≈ 9k pairs, own cap $0.50).
- **Ground truth:** H21's self-identification rule (agent's own intentions or chat; ambiguous days dropped); untestable if < 4 saboteur agent-days.
- **C1 (primary):** suspicion from *received* stance (agent-day target effect, z within day) has AUC ≥ 0.60 with within-day permutation p < 0.05. Credence 0.25.
- **C2:** suspicion from *given* stance, AUC > 0.5, p < 0.05. Credence 0.15. **C3:** combined AUC ≥ 0.60. Credence 0.25. **C4 (descriptive):** saboteurs in the daily minority camp.
- **Decision:** supported if C1 passes; failed if AUC < 0.55 or p > 0.20; else mixed.
- **Reuse policy:** different modality from every earlier #34 script; commit before running; disclose in H21's card and LOG.md.

## Round 2 redirects
- **What the direction is really after:** a cheap, calibrated sensor for adversarial or factional behaviour in agent swarms, and its detection limits.
- **H37-R1. A second labeller and rater.** Relabel the validation sets with another model and a human; report inter-labeller κ and whether the #12 result survives.
- **H37-R2. Find conflict where it might exist.** Run the calibrated detector on periods with contested decisions or vote-outs (#19, #31, #13) and on the #51 tail (holdout, with pre-registration), testing the governance-friction lead (negative pairs concentrate on norm-enforcing roles).
- **H37-R3. Kinetic stance.** Does a negative reply beget a negative reply (reciprocity, escalation)? A Hawkes or kinetic-Ising model on signed reply events, with the verdict and goal changes as interventions.
- **H37-R4. Run the #34 confirmation** after sign-off, as the saboteur test (D8.3).

## Notes
- **From H55 (2026-10-04):** the #51 norm-enforcer antagonism concentration is largely activity: the four enforcers are in 56% of all replies, and against that share the concentration is only p 0.09. Correctors get warmer, not colder, replies across 27 periods (ρ −0.24).
- **From DQ6 (2026-10-04):** `agent_goals` overwrote Claude Opus 5's first #51 role (game dev, 07-24 → 07-29, then Mathematician at NE38), so this card treated it as roleless for those days. That adds two rival pairs. Use `ground_truth_labels` (`preferred`) in the re-evaluation.
- 2026-10-04: promoted from HH125 by Vivian (usefulness-first batch); wave 2.
- 2026-10-04 01:35 UTC: data scheme, observables, nulls and predictions written before any real-data outcome (pair counts and 4 smoke-test labels from #40 seen; disclosed above).
- 2026-10-04 01:39 UTC: Amendment 1 (debater-adjacent pairs; enriched validation set). 01:40–02:00 UTC: Jev labelled 30,461 pairs ($1.116, 0 errors). 01:53 UTC: per-period predictions in the G folders.
- 2026-10-04: validation (blind labels before Jev answers), synthetic S1–S5, then the real-data run; S6 and Amendment 2 (calibrated null) after the first real-data run; `confirm_g34.py` written and dry-run, not run.
- The rubric changed to a two-page summary during the run; `summary/` follows the two-page version.
