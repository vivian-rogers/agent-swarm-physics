# H26: The swarm is near-critical in what it says but subcritical in when it acts

**Status:** round 1 done (2026-10-04): **failed as posed (R2 wins).** Content does carry a real room-level loop gain: drive-removed day-level median 0.53 [0.34, 0.66], room-permutation null beaten in 6/10 two-room units. But activity shows comparable room-excess gains at the same resolution, and its whole-swarm co-fluctuation is larger (global). H01's 0.74 is reproduced by drives alone in the synthetic, and the HH108 "gap" compared day means with 1-min spins. `analysis/confirm.py` written and dry-run, not run. Not promoted. **Round 1b (improved data, 2026-10-04): unresolved.** On the fixed activity table activity's room gain collapses (w30 0.44 → 0.12; cross-room ρ 0.50 → 0.10: round 1's activity co-movement was the event-drop artifact), so content now exceeds activity at 30 min in both models (Δg +0.41 [0.13, …]); talk matches content and content stays ≈ 0.5, not near-critical. NE42 native: the room excess is channel-borne. Promoted 2026-10-04 by Vivian from HH108; predictions written 2026-10-04 ~01:40 UTC, before any H26 real-data statistic.
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH108 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used:** Agent; Population N(t) (active variant: agents with data in the window); Regime (III only, plus #35 in II as a descriptive extra); Driving / external field (goal, kickoffs, human and `automated` messages); Interaction (broadcast, room rule); Agent state, *vector (for model 11)* in H01's named variant *whitened statement mean* (n = 32, H01's regime bases) but **unnormalized** (see "Agent state (vector), linear statement mean" below); H01's *goal field ĝ*. **New named variants proposed for `physics-models/DEFINITIONS.md`** (not edited here; outside H26's scope): *agent state (vector), linear statement mean*; *loop gain (equal-time, room excess)*; *exogenous drive direction*. The loop-gain functional is H19's *loop gain (equal-time)*, g = 1 − 1/VR.

## Standards (2026-10-04)
**Question served:** Q3 (content is not near-critical) and Q2 (the activity room gain was an artifact).

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | Time-shuffle N1 and the DQ8 trim variant (Round 1b): activity cross-room ρ falls from 0.79 to −0.05. | removed |
| Exogenous field (kickoff/goal/operator) | yes | Drive-removal ladder with exogenous-message directions and shared goal fields; P5 operator inputs; G12 shows half the debate gain is the motion field. Room-task drives are not separated from coupling (NE42 reading). | partly |
| Shared model priors | partly | Not handled: no `style_resid` vectors. Close with `style_resid` (§1). | open |
| Contemporaneous convergence | yes | Not handled: the room excess is equal-time co-fluctuation. Close with the in-flight placebo or ledger reads (§1). | open |

**Inputs:** round 1b uses `activity_bins_fixed`, the DQ8 trim, both embedding models, shared goal fields and DQ5 restatement flags. Still old: no `style_resid`; rooms use the broadcast rule, not ledger reads.

**Two layers:** 10 replication folders. Natives: 2 (NE42 supported, G12 supported in bge and mixed in gte).

**Confirm script:** `confirm.py` (#46, #47; #45 content only), written and dry-run, not run. Re-freeze: yes; it reads `activity_bins`, and C2/C3 were set from round-1 activity numbers that round 1b withdrew (round-1b synthesis, decision 2).

## Question
H01's content-level βJ₀/n (median 0.74, an upper bound) sits far above every activity loop gain (≤ 0.4). If that survives proper multi-direction field removal (the H24 lesson), ideas can cascade even when activity can't. *Check:* drive-removed content loop gain vs activity gain in the same windows; idea-cascade sizes (HH122).

Practical aim (usefulness-first batch): produce a number or rule an operator of an LLM agent swarm could compute from logs and act on.

## Model
**From:** `physics-models/11-vector-spins` (soft-spin / mean-field O(n) version) and `01-inverse-ising` (Curie–Weiss fluctuation relation). One estimand for every channel, the H19 equal-time loop gain:

  **g = 1 − 1/VR,  VR = 1 + (N_r − 1) ρ,  ρ = Σ_pairs tr C_ab / Σ_pairs √(S_a S_b)**

- C_ab: cross-agent covariance of field-removed deviations (summed over pair-windows; trace over the 32 content dimensions, or the scalar for activity and talk).
- S_a: agent a's *signal* variance from split halves (random halves of its statements, or of its minutes), so sampling noise does not dilute ρ.
- N_r: mean number of agents with data per room-window.

In a mean-field soft-spin swarm (each agent pulled toward its room mean with gain J), g = J at equal time. For windows longer than the collective relaxation time, VR → 1/(1 − J)², so a time-averaged state shows g_avg = J(2 − J) (derived below the observables). **Two channels can only be compared at the same resolution.** H01's 0.74 is a day-mean content statistic. H19's activity gains (0.06–0.4) are 1-min spins inside 30-min blocks. Part of the "gap" could be pure time-averaging.

**Variant used here (H26):** the swarm is a set of rooms. Within a room, agents are coupled with mean-field gain J. Across rooms, there is no direct coupling. Drives come in four kinds:
- a global day and time-of-day drive (common to all rooms);
- static goal and kickoff fields, multi-directional;
- measured exogenous room inputs (human and `automated` messages);
- possibly unmeasured room-specific drives.

**Rivals:**
- **R1, drives only:** J = 0; all co-fluctuation is common drive. H01's own caveat; H24's leakage.
- **R2, channel-blind coupling:** content and activity have the same gain at matched resolution and removal. The HH108 "gap" is then a resolution and removal artifact.
- **R3, H26:** g_content ≥ 0.5 after drive removal, above activity by > 0.15.

## Data scheme (`scheme/`)
`scheme/build.py` → `data/processed/H26-content-near-critical/` (≤ 200 MB), `_provenance.json`. Non-holdout only, asserted.
- **Units:** H01's analysis units (goal period split at step changes; `data/processed/H01-emergent-superagents-exist/units.json`) for regime III (#36b, #37, #38a–c, #39, #40, #41, #42, #44, #51a–e), plus #35 (regime II, descriptive).
- **Statements:** H01's statements and their 64-d whitened vectors (first 32 used, unit-normalized per statement), so the F0 baseline reproduces H01 exactly.
  - Each statement is tagged with its 30-min window of the day's activity window (`calendar.win_start`) and the agent's room at that time (`rooms_timeline`).
  - **Self-repeat dedupe** (infra Known issues, H12 rule): drop a chat statement whose raw bge cosine to an earlier chat statement by the same agent on the same PT day exceeds 0.95. Intentions are kept.
- **Activity and talk:** `activity_bins` 1-min states.
  - Active = state ∈ {act, talk}; talk = state talk.
  - Per agent-window: the fraction of the window's minutes, plus three random half-partitions of the minutes for split halves.
  - Agents on the day's roster with ≥ 1 event that day.
- **Exogenous drive directions:** embeddings of every human and `automated` chat message, whitened in the same basis, keyed by room and window.
- **Static field directions per unit:**
  - goal; kickoff; each room's kickoff; #51's private agent goals (H01's `goals_raw.npy`);
  - the top-3 principal directions of the unit's first-hour statements (H24's suggestion).
- **Outage proxy:** windows where ≥ 50% of minutes have no active agent in the whole village. H38's `outages.parquet` did not exist on 2026-10-04 01:40 UTC; this stand-in can be swapped for it.

## Candidate goal periods
Regime III, #51 (non-holdout part); #35 descriptive. G folders: G35, G36, G37, G38, G39, G40, G41, G42, G44, G51.

## Observables
*Written 2026-10-04 ~01:40 UTC, before any real-data H26 statistic.*

For each unit, channel ch ∈ {content c, activity a, talk k} and resolution r ∈ {day, w30 (30-min windows)}:

- **O1. Field-removal ladder** (nested; the same days, agents and windows for every channel):
  - **L0 (H01-like):**
    - day: deviation from the agent's unit mean;
    - w30: deviation from the agent-day mean (removes every day-level drive *and* day-level coupling).
  - **L1 (+ static multi-direction field; content only):** project deviations onto the complement of the static field subspace (goal, kickoff, room kickoffs, agent goals, 3 first-hour PCs; 5–9 directions).
  - **L2 (+ fitted room drive along measured inputs):**
    - content: per window, project out the span of the human and `automated` message directions of that window and the previous one (w30), or of that day (day). That is a per-room-day drive along those directions with free amplitude.
    - scalars: regress out those message counts (one pooled slope per unit).
    - w30 also removes the unit's time-of-day profile, and drops outage-proxy windows.
  - **L3 (+ global drive, two-room units only):** ρ_ex = ρ_within − ρ_cross, with pair type set per pair-window by room. Cross-room pairs cannot read each other's chat. Their co-fluctuation estimates every global drive: time of day, kickoff relaxation common to the rooms, outages, automated messages, the outside world. **L3 is the primary drive-removed estimate.** In single-room units (#51a, b, d, e), L2 is the best available and is flagged as an upper bound.
  - **L4 (aggressive lower-bound variant):** L3 plus, for each room-day, project out the top-3 directions of that room's day-mean deviations on the *other* days of the unit. This is a fitted per-room daily drive in a stable subspace. It also removes coupling along those directions, so it is a lower bound.
- **O2. Loop gains:** g_raw (L0, whole swarm, H01-like), g_L1, g_L2 per room, g_ex (L3), g_L4. Also H01's own P9 (βJ₀/n via `h01lib.mf_fit`) on the same units, raw and deduped, for continuity.
- **O3. Gap:** Δg_ca = g_c − g_a and Δg_ck = g_c − g_k at the same unit, resolution and ladder level. Reference: H19's 1-min activity and talk gains (`estimates.parquet`).
- **O4. Resolution ratio:** g_c(day) vs g_c(w30), against the time-averaging prediction g_avg = J(2 − J).
- **O5. Measured drive share:** the fraction of room-day (and room-window) mean deviation variance along measured exogenous directions, vs a null of directions from other room-days.
- **O6. Mode-resolved content gain:** the gain in the top collective direction vs the trace gain, and the effective dimension n_eff of the deviations (participation ratio).
- **Uncertainty:** bootstrap over days (pooled sums are additive over days), 400 draws; 95% percentile CIs.

### Time-averaging (derived before the data)
Linear mean-field kinetics with per-step gain J and relaxation φ:
- collective-mode AR coefficient φ + (1 − φ)J;
- individual modes ≈ φ.

Equal-time VR = (1 − φ²)/(1 − (φ + (1 − φ)J)²), which tends to 1/(1 − J) as φ → 1. For long-window means, VR = 1/(1 − J)², so g_avg = J(2 − J).
- An equal-time gain of 0.4 reads as 0.64 in day means.
- 0.3 → 0.51.
- 0.2 → 0.36.

## Null / baseline
- **N1, time-shuffle (anisotropic by construction):**
  - day: permute each agent's day labels within the unit;
  - w30: permute window labels within each agent-day.

  It keeps each agent's real anisotropic fluctuations and destroys all co-fluctuation (drive and coupling). Expected g ≈ 0.
- **N2, room-label permutation** (two-room units): permute agents' room labels within the unit, keeping room sizes. It is the null for ρ_ex: rooms don't matter.
- **N3, drive-only synthetic** (R1): the synthetic world at J = 0 with village-calibrated drives. It gives the false-positive level of each ladder step and the share of H01's 0.74 that drives alone produce.
- **Isotropic Gaussian surrogate:** reported only to show how much too narrow it is (H20 lesson), never for verdicts.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 drives only (J = 0); R2 channel-blind coupling (same gain in every channel at matched resolution).
**Locked holdout used for confirmation:** none run. `analysis/confirm.py` targets #46 and #47 (primary; two rooms; H04 used their activity for a different statistic) and #45 (secondary, content only, because H02's confirmatory run examined #45's activity couplings). Written and dry-run on #41, #42 and #44; not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Content state = linear mean of whitened bge statement vectors (H01 basis), deduped; activity and talk = minute fractions from `activity_bins`; rooms from `rooms_timeline`; drives from goal, kickoff and first-hour directions and human/`automated` message embeddings. All channels use one estimand, g = 1 − 1/VR. Assumptions listed. Not checked across families or regimes; one embedding model. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Time-averaging derived and shown: an equal-time gain 0.4 reads 0.64 in day means, so resolution must match. Within-unit stationarity assumed over 3–19 days. Synthetic: a 5-day window sees about 60% of the stationary gain. No Markov or update-order audit. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Content room excess beats the room-permutation null in 6/10 two-room units (day) and 7/10 (w30). Time-shuffle nulls use real anisotropic vectors; the isotropic surrogate is about 2× too narrow (1.1–2.9×; H20 lesson reproduced). No held-out day likelihood. The H26 claim itself fails its rule. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The signature (content ≥ 0.5 *and* above activity by > 0.15) is absent: 0/10 units supported; median Δg_ca at w30 is +0.03. P5 (operator inputs explain ≤ 10%) passed, but it is a supporting check, not the signature. **Round 1b:** on the fixed activity table the content > activity half of the signature holds at 30 min in both models (Δg +0.41 [0.13, …], 9/10 units); the near-critical half does not (content ≈ 0.5). |
| E interventional | predicts the change across a natural experiment | 1 | No natural experiment used. The #40 merge fails the two-room rule; NE15 is in the holdout. **Round 1b:** NE42 A-B-A native: the #39 partition's content and talk excess collapse in the merged week and return at the split (both models; goal-confounded, not blind). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | H01's P9 returns 0.57 (global drive at the observed cross-room level) to 0.74 at J = 0, and 0.79–0.83 at J = 0.2–0.6: drives saturate it. L3 tracks the realized gain under global drives (0.28 vs 0.29). It reads unmeasured room drives as coupling (0.46–0.49 at J = 0) and is biased toward content in drive-rich worlds (content +0.25, activity −0.1 to −0.2). Robust to dedupe, static and exogenous projections (Δ ≤ 0.06). No embedding swap. |
| G ground truth | agrees with known structure | 1 | Content co-fluctuation sits inside rooms (ρ_cross ≈ 0.05), including #41 where both rooms had identical instructions. Activity co-fluctuation is village-wide (ρ_cross 0.5–0.8), as expected from shared schedule and platform stalls. Measured operator messages explain nothing beyond their null. |
| H comparative | beats the named rivals | 1 | R2 (no robust channel gap at matched resolution) wins by the card's rule at both resolutions. R1 (drives only) cannot be excluded for room-level drives. **Round 1b:** R2 rejected for activity (its round-1 room gain was the event-drop artifact), not for talk. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. Large heterogeneity across periods (content L3 0.13–0.80). |

## Prediction
*Written 2026-10-04 ~01:40 UTC, before running the H26 analysis on real data.*

**What I had seen when writing this:**
- H01's per-unit P9 table: βJ₀/n, and ρ_within and ρ_cross per two-room unit (e.g. #41 0.47 / 0.04, #38b 0.16 / 0.05, #51c 0.06 / 0.01).
- H19's per-period 1-min activity and talk gains (regime III: activity 0.11–0.36, talk 0.02–0.16).
- The LOG summaries of H12, H13, H20 and H24.
- One count on real data: human messages per room-day (median 0–1) and `automated` messages (median 1–5) in the candidate periods.

From H01's ρ table one can guess the L3 day-level content gain on H01's instrument: g_ex ≈ 0.17–0.76, median ≈ 0.4. My predictions use that, so **P2 is not blind**. No H26 estimator had been run on any real unit.

- **P1, synthetic (axis F; run first):**
  - **(a)** At J = 0, a global day drive strong enough to give ρ_cross ≈ 0.06 (H01's median), with N ≈ 14 in two rooms and T = 5, makes H01's P9 return βJ₀/n ≥ 0.3. Drives alone produce at least 40% of 0.74 [0.7]. Adding room-specific drives that give ρ_ex ≈ 0.15 reproduces ≈ 0.74 at J = 0 [0.7].
  - **(b)** L3 at J = 0 with global and measured drives only: median |g_ex| ≤ 0.1 [0.7]. For planted day-level gains of 0.25–0.6, L3 recovers within ±0.12 (median) [0.6], in content and in the scalar channel alike (no channel bias) [0.7].
  - **(c)** Unmeasured room-specific drives bias L3 upward one-for-one (a property, stated for honesty). L4 removes them only when their subspace is stable across days.
- **P2, headline, day level:** the drive-removed content gain (L3) has a median over two-room units of 0.25–0.5 [0.6], down from H01's 0.74. It is ≥ 0.5 in at least half of the two-room units [0.3]. L4 halves it again [0.5].
- **P3, gap at matched resolution and removal:**
  - day: Δg_ca > 0.15 in ≥ 2/3 of the two-room units [0.45];
  - w30: same [0.45];
  - talk: Δg_ck > 0.15 in ≥ 2/3 at w30 [0.5].
- **P4, resolution:** the median content g_ex is lower at w30 than at day level by ≥ 0.1 [0.6]. The day-level content gain exceeds the w30 gain mapped through g_avg = J(2 − J) [0.5]: there are slow room drives or slow coupling beyond time-averaging.
- **P5, measured drives are small:** human and `automated` message directions explain ≤ 10% of room-day mean-deviation variance (above their null) [0.75]. Measured operator inputs cannot carry the room excess. Whatever remains is coupling or unmeasured room drives.
- **P6, #51 (single room, L2 upper bound):** g_c ≥ g_a at day level in most #51 sub-units [0.55].

**Verdict rules (per two-room unit, day level, L3):**
- **supported:** g_ex,c ≥ 0.5, Δg_ca > 0.15 with the bootstrap 95% CI excluding 0, and N2 room-permutation p < 0.05.
- **failed:** g_ex,c < 0.5 and Δg_ca ≤ 0.15.
- **mixed:** otherwise.

Single-room units are descriptive (upper bound).

**Hypothesis-level outcome:**
- **H26 survives:** ≥ half of two-room units supported, and median g_ex,c ≥ 0.5.
- **Gap real but content not near-critical:** median Δg_ca > 0.15 (CI excludes 0) with median g_ex,c < 0.5.
- **Failed (R2 wins):** median Δg_ca ≤ 0.15, or its CI includes 0, at both resolutions.

The w30 comparison is reported in full but is secondary. Everything else (L4, mode-resolved, per-unit p-values) is descriptive. Multiplicity: about 12 two-room units × 2 resolutions × 3 channels; only the rules above count.

### Amendment 1
*2026-10-04 ~02:00 UTC: after the synthetic validation and the scheme build, before any real-data H26 statistic.*

**What I had seen:**
- the synthetic results (below);
- scheme counts: 96,621 statements; 2,755 self-repeats (4.8% of chat; 11% in #38a, 23% in #38b); 1,418 exogenous messages (255 human); static subspace rank 5–9 per unit;
- some calendar days span up to 25–34 windows (village-off gaps; the outage proxy drops those windows).

Predictions and verdict rules above are unchanged except where stated.

- **(a) Resolutions.**
  - "w30" now means equal-time 30-min windows, with deviations from the agent's *unit* mean.
  - The pre-registered within-day version is kept as **wd** (descriptive).
  - Reason: within-day deviations high-pass away slow collective modes. In the synthetic, the within-day truth is 0.04 when the population day-level gain is 0.45, so wd cannot see coupling.
  - P3 and P4 use the new w30.
- **(b) No time-of-day removal at L2.** An estimated common profile biases within-room and cross-room covariances alike: pooled, by −Var_total/n; cross-fitted, by +Var(m̂). Sampling noise dominates a 30-min content state. Time of day is a global drive, so L3 removes it.
- **(c) L3 normalization.** ρ_ex = (ρ_w − ρ_c)/(1 − ρ_c), so the global-drive share leaves the signal variance too. Otherwise strong common drives dilute it (synthetic activity at w30). The pre-registered form ρ_w − ρ_c is reported as `g_ex_raw`.
- **(d) L4 at day resolution** with fewer than 8 days removes k = 1 direction. With k = 3, four other days' room means are nearly spanned.
- **(e) L1 in #51.** Private goals enter as their top-2 principal directions. Agent-specific static fields are removed by the agent mean and create no co-fluctuation.
- **(f) Exogenous directions at w30** cover windows t−3…t (2 h), not t−1…t. Synthetic responses persist about 6 windows.
- **(g) Power and bias, from the synthetic.** These are reading rules, not new verdict rules.
  - At T = 5 days, a scalar channel's day-level L3 gain has an IQR of about 0.9 across replicates; content's is about 0.2. Per-unit "supported" verdicts at day level will therefore almost never meet the CI rule. The decisive evidence is the pooled median and sign counts, and w30.
  - Content L3 tracks the realized 5-day gain under global drives (0.28 vs 0.29).
  - Content L3 overestimates by about +0.2–0.25 when room-specific measured inputs are strong but measured imperfectly.
  - Content L3 reads unmeasured room drives as coupling (0.46–0.49 at J = 0).
  - Activity L3 runs about 0.1 below the realized gain in drive-rich worlds.
  - A 5-day window sees about 60% of the stationary gain (J = 0.4: realized 0.28 vs population 0.45).
- **(h) Additional descriptive outputs:** g_ex at L0 (cross-room contrast with no projections) for every channel, so the scalar L2 regression cannot drive the gap.

### Amendment 2
*2026-10-04 ~02:15 UTC: after a functional test of `explore.py` on #37 only, the smallest unit (3 days). I saw its day and w30 gains. No other unit had been run.*

- **(a) Outage windows** (≥ 50% of minutes with no active agent in the village) are dropped at every resolution, not only w30. On #37, a day with a 513-min village-off gap drove day-level activity to ρ_c ≈ 0.95.
- **(b) No exogenous-count regression for day-level scalars.** Two slopes fitted on D × R room-day cells over-fit: on #37, ρ_c flipped from +0.95 to −0.27. Day-level activity and talk L2 = L0. The w30 regression is kept.
- **(c) Day-level L4** is computed only for units with ≥ 8 days (#38a, #51b, #51c). With fewer days it acts room by room on one or two other days and can *raise* g_ex (#37: 0.15 → 0.45).

#37's verdict is flagged as seen during debugging.

## Results by goal period
Day level. Two-room units: L3 room excess. One-room units: L2 (upper bound). g clipped at −1. Δg_ca = content − activity (joint day bootstrap).

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G35](goalperiod-subhypotheses/G35/README.md) | exploratory (regime II, descriptive extra) | mixed | content 0.80 [0.72, 0.84], N2 p 0.01. Activity 0.55, Δg +0.25 [−0.02, …]. w30: content 0.78 vs activity 0.66. |
| [G36](goalperiod-subhypotheses/G36/README.md) | exploratory | mixed | content 0.53 [0.34, 0.65], N2 p 0.01. Activity day noisy. w30: activity 0.61 > content 0.40. |
| [G37](goalperiod-subhypotheses/G37/README.md) | exploratory (seen while debugging) | failed | content 0.15 (ρ_w 0.23 ≈ ρ_c 0.20: global). w30: content 0.35, activity 0.29, talk 0.67. |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory | mixed | content 0.65 / 0.55 / 0.40 (38a/b/c; N2 p ≤ 0.03). At w30 activity ties (38a) or exceeds (38c) content; talk > content in all three. |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory | mixed | content 0.45. Activity room excess negative (cross-room > within). Talk w30 0.80 > content 0.29. |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory (not two-room by rule) | descriptive | whole-room L2: content 0.75 < activity 0.90 ≈ talk 0.89. |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory | mixed | best case: content 0.77 [0.72, 0.80], N2 p 0.005, identical room instructions. Activity's room excess negative, but its whole-swarm ρ_w 0.83 vs content 0.45. |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory | failed | content 0.13 (global co-fluctuation). Activity w30 0.60 > content 0.28. |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory | mixed | content 0.76. w30: activity 0.81, talk 0.78 > content 0.72 (Δg −0.09 [−0.16, 0.14]). |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | mixed | single room: activity 0.92–0.95 ≫ content 0.25–0.65 (Δg −0.27 to −0.50). #focus (51c): content 0.54, N2 p 0.18. |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native (1b) | supported | #39 partition as pseudo-rooms: content and talk excess collapse in the merged week and return at the split |
| [G12](goalperiod-subhypotheses/G12/README.md) | native (1b) | supported (bge) / mixed (gte) | debate motion on: g 0.72 vs off 0.66; removing the motion direction halves it |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only, holdout asserted in every loader)
**Labeled exploratory.**
- **Scheme:** 96,621 statements (2,755 self-repeats removed), 25,857 agent-windows of minute activity, 1,418 exogenous messages (255 human), 16 H01 units; 15 MB in `data/processed/H26-content-near-critical/`.
- **Code:** `scheme/build.py`; `analysis/{h26lib,synthetic,explore,summarize,figures,write_period_folders,write_period_results,confirm}.py`.
- **Numbers:** `synthetic/synthetic_summary.json`, `G##/<unit>.json`, `summary.json`, `summary_units.json`.
- **Figures:** `figures/summary.pdf` (one-page figure summary), `figures/ladder.pdf`, `figures/summary_obs.pdf`, `figures/synthetic_validation.pdf`, `G##/figures/G##_ladder.pdf`.

**Headline.**
- **Content carries a genuine room-level loop gain.** Drive-removed (L3) day-level median 0.53 [0.34, 0.66] over the 10 regime-III two-room units; ≥ 0.5 in 6/10; room-permutation null beaten in 6/10 (7/10 at w30). Dedupe, multi-direction static fields and measured operator inputs change it by ≤ 0.06.
- **"Subcritical in when it acts" fails.** At the same resolution and with the same drive removal, activity's room-excess gain is comparable:
  - pre-registered estimator: w30 median 0.44 vs content 0.43; median gap Δg_ca +0.03;
  - day-level gap +0.32, but its CI [−0.08, 1.48] includes 0, and day-level activity is unpowered;
  - robust pooled estimator: activity 0.54 vs content 0.52 (day), 0.47 vs 0.43 (w30);
  - talk exceeds content at w30 (median Δg_ck −0.09).
- **The channels differ in where co-fluctuation lives, not how strong it is.** Activity co-moves across the whole village: cross-room correlation ρ_c 0.79 at day level and 0.50 at w30. Content co-moves inside rooms: ρ_c ≈ 0.05.
- **Where HH108's gap came from.** H01's 0.74 is a whole-swarm, day-mean statistic with no removal of global drives. H19's ≤ 0.4 is from 1-min spins with 30-min detrending. On H01's footing, activity would read 0.91 (L0, day).

**Synthetic validation (axis F; `figures/synthetic_validation.pdf`; 24 two-room worlds per scenario, N = 14 in 7 + 7, T = 5 days, 8 windows/day; 12 one-room worlds, N = 24, T = 15).**

| Check | Result |
| --- | --- |
| How much of H01's 0.74 drives alone produce (J = 0) | Global day drive at the observed cross-room level (ρ_c ≈ 0.08): **0.57** [0.42, 0.61]. + room drives (ρ_ex ≈ 0.15): 0.67–0.71. + kickoff relaxation, time of day, operator pulses: **0.74**. One room (N 24, T 15), global drive only: **0.83**. With coupling J = 0.2–0.6: 0.79–0.83. H01's estimator is saturated by drives and nearly blind to J. |
| L3 under global drives (J = 0) | content −0.01 (day), +0.02 (w30); room-permutation size 0/8 at 0.05 (conservative) |
| L3 recovery (vs the realized 5-day latent gain) | content-only coupling: 0.28 vs realized 0.29. With strong operator pulses measured at cos 0.8: +0.25 too high. Unmeasured room drives at J = 0: 0.46–0.49 (cannot be separated from coupling). Activity: about 0.1–0.2 too low in drive-rich worlds. |
| Noise | IQR of day-level L3 over replicates: content 0.1–0.4, activity 0.7–1.3; w30 activity 0.25–0.9 |
| Finite window | 5-day windows see ~60% of the stationary gain (J = 0.4: 0.28 vs 0.45) |
| Bootstrap coverage | 0.6–0.9 (day) for content; per-unit CIs under-cover |

**Outcome vs prediction**

| | Prediction (locked) | Outcome | Verdict |
| --- | --- | --- | --- |
| P1a | drives alone give H01 βJ₀/n ≥ 0.3 [0.7]; adding room drives reproduces ≈ 0.74 [0.7] | 0.57 (global only); 0.67–0.74 with room or other drives; 0.83 in one room | **passed** |
| P1b | L3 at J = 0 with global and measured drives \|g\| ≤ 0.1 [0.7]; recovery ±0.12 [0.6]; no channel bias [0.7] | global only −0.01 ✓. Imperfectly measured room inputs +0.33 ✗. Content-only coupling 0.28 vs 0.29 ✓. Activity biased low ✗ | **partial** |
| P2 | L3 content day median 0.25–0.5 [0.6]; ≥ 0.5 in ≥ half the units [0.3]; L4 halves it [0.5] | median 0.53 [0.34, 0.66] (just above the range); 6/10 ≥ 0.5; L4 (w30) 0.36 vs L3 0.43 | **failed** (higher than predicted); second part happened; third failed |
| P3 | Δg_ca > 0.15 in ≥ 2/3 of units: day [0.45], w30 [0.45]; Δg_ck at w30 [0.5] | day 6/10 (CI > 0 in 1/10); w30 4/10; talk 2/10. Medians +0.32, +0.03, −0.09 | **failed** |
| P4 | content w30 below day by ≥ 0.1 [0.6]; day above the J(2 − J) map of w30 [0.5] | 0.43 vs 0.53 (Δ 0.10); map of 0.43 = 0.68 > 0.53 | met (barely); **failed** |
| P5 | measured operator inputs explain ≤ 10% of room-day variance [0.75] | excess share −0.16 to +0.01 (day), −0.01 to +0.05 (w30), all units | **passed** |
| P6 | #51: g_c ≥ g_a at day level in most sub-units [0.55] | reverse in 4/4 single-room sub-units (0.25–0.65 vs 0.92–0.95) | **failed** |
| Card rule | survives / gap real but subcritical / failed (R2) | 0/10 supported (8 mixed, 2 failed); day Δg CI includes 0; w30 median Δg +0.03 | **failed (R2)** |

**What this means.**
1. **There is no channel gap at matched resolution.** HH108 compared a day-mean, drive-inclusive content statistic with 1-min, block-detrended activity statistics. Time-averaging alone inflates a gain (an equal-time 0.4 reads 0.64 in day means). Drives inflate H01's estimator to 0.57–0.74 even without coupling. Once resolution and drive removal match, content's room excess (≈ 0.45–0.55) sits next to activity's (≈ 0.45–0.55), and talk is at least as high.
2. **The channels differ in where they co-move.** Activity is driven village-wide: the schedule, platform stalls and the shared clock. Content co-moves inside rooms, and none of it is explained by measured operator messages.
   - That room-local content co-movement is either coupling (conversation and shared artifacts) or unmeasured room-specific drive (task structure). The synthetic shows L3 cannot tell these apart.
   - #41, with identical instructions in both rooms, is the strongest case for coupling: content 0.77 [0.72, 0.80].
3. **"Near-critical" is too strong for any channel.** A room-excess gain of ~0.5 means collective room fluctuations are about twice the independent-agent level (VR ≈ 2). It is not a divergence. The 5-day window probably understates the stationary gain (synthetic: about 60%).

**Post hoc, cross-hypothesis (H25; not pre-registered; `analysis/posthoc_nscaling.py`, `posthoc_nscaling.json`).** H25 reported that its whole-swarm content dial (median g 0.70) is swarm size times a constant per-pair correlation, a shared-field signature. I asked whether each H26 channel's per-pair correlation is flat in room size (shared field: g rises with N) or falls like 1/(N − 1) (coupling normalized by partners: g flat). The fit is log ρ_w = c + α log(N_r − 1) across the 16 units, within-room ρ at L2, bootstrap over units.
- **Content falls steeply:** α = −1.43 [−1.95, −0.88] (day), −1.04 [−1.47, −0.65] (w30). The room gain stays near 0.5 from rooms of 7 to rooms of 30, which is the coupling-like signature.
- **Activity and talk are nearly flat:** activity α −0.13 [−0.28, 0.02] (day), −0.60 [−1.21, 0.02] (w30); talk about −0.2. This is shared-field-like, consistent with their village-wide co-movement.
- **Strongly confounded.** Every large-N unit is #51: one room, private roles, 8 h days. The L3 room-excess fits span only N_r 6.5–9.6 and are uninformative (CIs ±2–3).
- **Reconciliation with H25.** H25's statistic is whole-swarm and within-day; it mixes within- and cross-room pairs, and its N range runs across regimes. It reproduces H26's L0 where content co-moves inside rooms (#35: 0.84 vs 0.83) but not where content co-moves across rooms (#37: H25 0.77 vs H26 L3 0.15).
- **Reading.** H26's room-separated content excess does *not* show the shared-field size signature, while the activity and talk channels do. This is a lead for R1/R2, not a result.
- **One more H25 caveat applies here.** Equal-time variance ratios are blind to coupling delayed by minutes.

**Operator-facing conclusion.**
- Don't infer "ideas can cascade while activity can't" from a content alignment number.
- Compare channels only at the same time resolution, and only after removing village-wide co-movement. Compute within-room minus cross-room co-fluctuation of agents' day or 30-min states, normalized by split-half signal variance.
- In the village both content and activity then sit at a room loop gain of ≈ 0.5.
- Content co-moves room by room. Activity co-moves village-wide, so a village-wide activity dip is a platform or schedule event, not a social one.
- Operator broadcasts do not explain room content co-movement, so steering what a room talks about means acting inside the room.

**Caveats.**
- **Unidentifiable room drives.** Room-specific unmeasured drives (separate forks in #35, different instructions in #38, the goal override in #44) read as coupling one-for-one.
- **Estimator bias favours content.** In drive-rich synthetic worlds, content runs high and activity low. If anything, the real activity gain is understated relative to content, which strengthens R2.
- **Noisy activity at day level.** Day-level activity gains are close to unpowered with 3–8 days, and some activity room excesses are strongly negative (cross-room > within). These clip at −1 and dominate per-unit Δg CIs. Medians and w30 carry the comparison.
- **Talk at day level.** ρ > 1 in several units: split-half variances of rare events are unreliable. The pooled estimator gives lower talk gains.
- **One-room units have no cross-room baseline.** L2 values in #40 and #51 are upper bounds for every channel.
- **Instrument.** One embedding model (bge-small); no swap. Statements are claims, not ground truth.
- **Amendments.** Amendment 2 was made after a functional test on #37.
- **Missing inputs.** H34's cascade tables (HH122) did not exist yet, so cascade sizes were not used. H38's outage table did not exist either; a stand-in outage proxy was used. H25's dial arrived after the analysis and is cross-referenced post hoc above.
- **Multiplicity.** About 10 units × 2 resolutions × 3 channels; only the card's rules are counted.

### Confirmatory design (written 2026-10-04 after exploration; not run)
`analysis/confirm.py`, frozen predictions C1–C5:
- **Targets:** #46 and #47 (primary; two rooms; inside the NE21+NE23 window, where H04 computed activity Hawkes n, a different statistic). #45 enters content-only predictions, because H02's confirmatory run examined its activity couplings.
- **C1:** content room excess > 0 with N2 p < 0.05 in ≥ 2 of 3 targets; median in [0.3, 0.75].
- **C2 (R2):** w30 Δg_ca ≤ 0.15 in at least one of #46 and #47.
- **C3:** w30 ρ_c(activity) − ρ_c(content) ≥ 0.2 in both #46 and #47.
- **C4:** exogenous share ≤ 10% in every target.
- **C5:** |g_room(L2) − g_room(L0)| < 0.1 for content (day) in every target.
- **Safeguards:**
  - It refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`.
  - It also refuses unless the script, card, `h26lib.py` and `explore.py` are committed and unmodified (reuse policy item 1).
  - `--dry-run` uses #41, #42 and #44, asserts no holdout day is touched, and reproduces `explore.py` (content day 0.770 vs 0.767; w30 within 0.01).
- **Reuse disclosure:** goes into LOG.md and the H02, H04 and H23 cards when run.

## Round 1b (improved data, 2026-10-04)
*Re-run of the pre-registered pipeline on corrected inputs, plus two period-native tests. P1–P6, the verdict rules and the outcome rule are unchanged. The native predictions were written in the NE42 and G12 folders at 07:45 UTC, before they were run.*

**What changed in the inputs.**
- **Activity:** `activity_bins_fixed` (DQ8). Round 1 had lost about half of all events, and the loss fraction is day-specific, so it acts as a shared day-level field (RE-A1). The outage proxy is recomputed on the fixed table.
  - Active agent-minutes rise 36%, talk minutes 86%.
- **DQ8 trim variant (`bge_fixed_trim`):** activity and talk minutes restricted to each day's all-present window (every present agent between its first and last record). This keeps 69% of agent-minutes and is applied before windows and split halves are formed.
- **Content:**
  - H01's round-1b scheme (`r1b/bge_none`, `r1b/gte_none`): shared goal fields, which fix the #38 room-kickoff swap in L1's static subspace;
  - both embedding models, with exogenous message directions in each model's basis;
  - DQ5's own-model restatement flags (chat only, as in round 1: bge 2,756, gte 2,116 of 96,621 statements). Round 1's rule flagged 2,755.
- **Code:** `scheme/build.py --r1b TAG --h01 … --model … --dedupe … --data-version fixed [--trim]`; `analysis/explore.py` and `summarize.py --r1b TAG` (no flag = round 1); new `analysis/r1b_native.py`, `r1b_compare.py`, `r1b_period_folders.py`, `r1b_estimates.py`.
  - Outputs in `data/processed/H26-content-near-critical/r1b/<TAG>/`; side by side in `r1b/compare.json`.
  - `old_check` (old activity table, shared goal fields, round-1 dedupe rule) reproduces round 1 to ≤ 0.001.

**Old vs new (10 regime-III two-room units; day = day level, w30 = 30-min; L3 room excess, medians).**

| Statistic | Round 1 | 1b bge | 1b gte | 1b bge, activity trimmed |
| --- | --- | --- | --- | --- |
| content g_ex day [95% CI] · units ≥ 0.5 | 0.53 [0.34, 0.66] · 6/10 | 0.52 [0.33, …] · 5/10 | 0.47 [0.25, …] · 4/10 | 0.52 · 5/10 |
| content g_ex w30 | 0.43 | 0.43 | 0.47 | 0.43 |
| **activity g_ex day · w30** | 0.32 · 0.44 | **−0.38 · 0.12** | −0.38 · 0.12 | −0.37 · 0.16 |
| talk g_ex day · w30 | 0.76 · 0.63 | 0.59 · 0.64 | 0.59 · 0.64 | 0.73 · 0.69 |
| **activity cross-room ρ_c day · w30** | 0.79 · 0.50 | **−0.05 · 0.10** | −0.05 · 0.10 | −0.03 · −0.01 |
| content cross-room ρ_c day · w30 | 0.05 · 0.05 | 0.06 · 0.05 | 0.05 · 0.04 | 0.06 · 0.05 |
| Δg_ca day [CI] · units > 0.15 | +0.32 [−0.08, 1.48] · 6/10 | +0.76 [−0.02, …] · 6/10 | +0.42 [−0.03, …] · 6/10 | +0.65 [−0.06, …] · 6/10 |
| **Δg_ca w30 [CI] · units > 0.15** | +0.03 [−0.15, …] · 4/10 | **+0.41 [0.13, …] · 9/10** | **+0.42 [0.14, …] · 9/10** | **+0.22 [0.01, …] · 6/10** |
| Δg_ck w30 (talk) | −0.09 | −0.03 | −0.04 | −0.09 |
| robust pooled estimator day: content / activity / talk | 0.52 / 0.54 / −0.08 | 0.51 / −0.04 / 0.41 | 0.44 / −0.04 / 0.41 | 0.51 / −0.01 / 0.50 |
| N2 room-permutation p < 0.05 (content day · w30) | 6 · 7 | 6 · 6 | 6 · 10 | 6 · 6 |
| measured operator inputs, excess share (P5) | −0.16 to +0.01 | −0.15 to +0.01 | −0.17 to −0.00 | −0.16 to +0.01 |
| H01 P9 replica (median βJ₀/n) | 0.74 | 0.74 | 0.73 | 0.74 |
| per-unit verdicts supported / mixed / failed | 0 / 8 / 2 | 1 / 8 / 1 | 1 / 7 / 2 | 0 / 9 / 1 |
| card outcome | failed (R2) | **unresolved** | **unresolved** | **unresolved** |

**Which verdicts change.**
- **Activity's room gain was largely an artifact of the event-drop bug.**
  - On the fixed table, activity's cross-room correlation collapses: 0.79 → −0.05 at day level, 0.50 → 0.10 at w30. Its room excess falls to −0.38 (day) and 0.12–0.16 (w30).
  - This is the same artifact RE-A1 found for H12's market mode: dropping a day-specific fraction of everyone's events is a shared field.
  - What remains of activity co-movement is the runner's day edge (H50), which the trim removes.
- **Card outcome: failed (R2) → unresolved.**
  - **Against activity, the R2 null fails.** The content–activity gap is now real at 30 min in both models (Δg_ca +0.41 [0.13, …] and +0.42 [0.14, …], 9/10 units > 0.15) and survives the trim (+0.22 [0.01, …]).
  - At day level the median gap is larger (+0.42 to +0.76), but its CI still touches 0 (day-level activity is unpowered).
  - **Against talk, R2 still holds.** Talk's room excess matches or exceeds content's at w30 (Δg_ck −0.03 to −0.09).
  - **Content is still not near-critical:** median g_ex,c is 0.47–0.52, at or below the 0.5 bar.
  - The "gap real but content not near-critical" branch needs the day-level CI to exclude 0, and it misses by 0.02–0.06. So the honest reading is between that branch and R2: **ideas co-move inside rooms about as strongly as talk does, much more than activity, and well below criticality.**
- **P3 (gap at matched resolution): failed → half held.**
  - w30 Δg_ca > 0.15 in 9/10 units (≥ 2/3 required) in both models.
  - Day level: 6/10.
  - Talk Δg_ck: 2/10 → 1–2/10 (still fails).
- **P6 (#51 g_c ≥ g_a) still fails** (1/4 sub-units at day level), although #51 activity drops from 0.92–0.95 to 0.13–0.86.
- **P2, P4, P5 unchanged** (content inputs differ only through dedupe and goal fields). P1 (synthetic) is not re-run.
- **Per unit:**
  - 38b mixed → supported (both models; activity's day excess is now negative);
  - 35 (regime II extra) mixed → supported;
  - 37 failed → mixed;
  - 36b mixed → failed with gte;
  - with the trim, 38b returns to mixed.

**Native tests (Role: native).**

| Test | Prediction | Outcome (bge / gte) | Verdict (1b) |
| --- | --- | --- | --- |
| [NE42](goalperiod-subhypotheses/NE42/README.md): #39 partition as pseudo-rooms in #39 → #40 → #41 | content w30 g_ex < 0.15 in #40, ≥ 0.3 in #39 and #41 [0.55]; activity change < 0.2 [0.5]; talk collapses [0.45] | content w30: 0.36 → **ρ_w 0.21 < ρ_c 0.29 (g −1)** → 0.71 / 0.41 → (ρ_w 0.23 < ρ_c 0.34) → 0.74. Talk: 0.80 → (−0.03 < 0.12) → 0.74. Activity: ρ_w < ρ_c in #39 already (undefined change) | **supported** for content and talk (both models); activity uninformative |
| [G12](goalperiod-subhypotheses/G12/README.md): #12 motion field on vs off (10-min slots) | g_on > g_off [0.6]; removing each debate's motion direction halves g_on [0.5] | g_on 0.72 [0.68, 0.75] vs g_off 0.66 [0.63, 0.68]; after removal 0.34 [−0.01, 0.48] / 0.73 vs 0.67 → 0.37 [0.07, 0.51] | supported (bge) / mixed (gte; 0.37 vs the 0.365 bar) |

**Reading of the natives.**
- When the channel between the old rooms opens, their content excess does not just vanish: cross-partition pairs co-move *more* than within-partition pairs, and the excess returns at the split. **The room excess is channel-borne (coupling or a room-task drive the merge removes; #40's shared objective confounds).**
- In a debate, about half of the content gain is the motion's direction (a field). The rest is either co-fluctuation around it, or the removal is incomplete.

**Scorecard after 1b.**
- A 1.
- B 1.
- C 1.
- **D 0 → 1:** the signature's activity half (content > activity at matched resolution) now holds at w30 in both models. The near-critical half does not.
- **E 0 → 1:** the NE42 A-B-A behaves as the coupling/channel reading predicts, but it is goal-confounded and not blind (H47 seen).
- F 1.
- G 1.
- **H 0 → 1:** R2 is rejected for activity, though not for talk.
- I 0.

**Operator-facing update.**
- On correct activity data, what agents *do* barely co-moves room by room. What they *say* and *how much they talk* do (gain ≈ 0.4–0.6), and the room channel carries it.
- Village-wide activity co-movement in round 1 was a data artifact plus the runner's schedule.
- **No channel is near-critical.**

## Round 2 redirects
**What the direction is really after:** whether ideas spread through a swarm more easily than effort does, measured so that channels are comparable. Round 1 says: not at matched resolution; the channels differ in where they co-move, not in how much.
- **H26-R1. Separate room coupling from room drive with the merge and split natural experiments.** Run the room-excess estimator across NE15 (holdout) and the #40 merge: coupling predicts the content room excess follows the channel cut; a room-task drive predicts it follows the task.
- **H26-R2. Lagged, exposure-conditioned content gain.** Does agent i's next-window content move toward what its room-mates posted in the previous window, beyond what other rooms posted? This is a directed (Granger-style) loop gain that common drives cannot fake.
- **H26-R3. Idea-cascade sizes (HH122) from H34.** Compare the cascade-size distribution and branching ratio with the room-excess content gain per period.
- **H26-R4. Instrument checks: embedding swap, style control, H38 outages.** Repeat the content channel with a second embedding model and after H13's style residualization; re-estimate activity with H38's outage table.

## Notes
- 2026-10-04: promoted from HH108 by Vivian (usefulness-first batch); wave 2.
- 2026-10-04 01:40 UTC: model, observables, nulls and predictions written before real-data work. H25 (criticality dial) and H34 (idea cascades) outputs did not exist yet; H38's outage table did not exist yet (stand-in proxy above).
- 2026-10-04 ~02:00 UTC: synthetic validation run (`analysis/synthetic.py`), then Amendment 1, then the scheme build, then the per-period predictions (G folders, ~02:05 UTC), then Amendment 2 (after the #37 functional test), then the full exploration.
- 2026-10-04 ~03:15 UTC: round 1 done. Verdict failed as posed (R2). Confirm script written and dry-run. Proposed shared changes (DEFINITIONS entries, a LOG entry, an infra note on pooled time-of-day profiles) are in the agent report, not made here (edit scope).
