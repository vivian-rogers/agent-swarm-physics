# H01: Emergent superagents exist

**Status:** running. Exploratory round 1 of D3.1.a and D3.2 done (2026-10-03, non-holdout only): rooms are reliably more ordered than random groups but miss the pre-registered size; a small, instrument-sensitive coupling residual plus a strong merge effect; the field-dominance and low-coupling predictions (P5 in substance, P9) fail. Confirmatory script `analysis/confirm_d32.py` written and dry-run on non-holdout stand-ins, **not run on the holdout**. Level: hypothesis (C < 2). (Proposed 2026-10-03 by Vivian Rogers.)
**Fields:** info theory, stat mech, thermodynamics, sociophysics
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md); [Sowinski et al. 2023](../../literature/sowinski-2023-semantic-information-resource-gathering-agents.md); [Bartlett et al. 2025](../../literature/bartlett-2025-physics-of-life-information-roadmap.md); [arXiv:2608.16578](../../literature/arxiv-2608.16578-physics-of-agents.md) (not yet read). Further reading: [architecture.md](architecture.md#reading-list-from-the-transcript-citations-to-verify).
**Definitions used:** *superagent*, *ideology*, *semantic information*, *semantic entropy (meaning clusters)*: drafts in `physics-models/DEFINITIONS.md`.

## Files

| File | What |
| --- | --- |
| [subhypotheses.md](subhypotheses.md) | **The full set:** 10 directions (D1–D10) → sub-hypotheses → sub-sub-hypotheses, with rivals marked, tiers, windows and models. Pick from here. |
| [architecture.md](architecture.md) | The machinery: terms, required inputs (boundary, viability, horizon), tiers of causal access, estimators, pitfalls, decisions |
| [../natural-experiments.md](../natural-experiments.md) | Shared catalog of step changes (NE01–NE40) used as quasi-interventions |
| [notes/kolchinsky-qa-transcript.md](notes/kolchinsky-qa-transcript.md) | Background Q&A on semantic information and estimation (pasted; unverified) |
| `scheme/` | `build.py` (statements → whitened vectors, clusters, ĝ, agent-days, rooms, exposure; non-holdout only), `build_lexical.py` (lexical robustness instrument), `h01common.py` |
| `analysis/` | `h01lib.py` (estimators), `h01data.py` (loader), `synthetic.py` (axis F), `explore.py` (P1–P9), `summarize.py`, `figures.py`, `period_cards.py`, `confirm_d32.py` (confirmatory, not run) |
| `figures/` | `summary.pdf` (one page), `synthetic_validation.pdf`, `p1_p2_rooms_labs.pdf`, `p5_p6_coupling.pdf`, `p7_p8_events.pdf`, `p9_meanfield.pdf`, `robustness.pdf` |
| `G08/` … `G51/`, `NE32/`, `NE15/` | per-goal-period results and the spanning tests (NE15 = confirmatory, pending); see "Results by goal period" |

## Question
Do groups of agents form **emergent superagents**: coarse-grained units that act more like one agent than their members do? The main lenses:
- a shared **ideology** as an ordered, low-semantic-entropy state the unit maintains;
- Kolchinsky–Wolpert **semantic information** for which parts of it are load-bearing.

## Directions (details in subhypotheses.md)
1. **D1 Identification:** which groupings act as one agent.
2. **D2 Viability:** what a superagent "staying alive" means.
3. **D3 Ideology as an ordered phase.**
4. **D4 Load-bearing information** (Kolchinsky–Wolpert proper).
5. **D5 Identity through turnover.**
6. **D6 Response to forcing.**
7. **D7 Formation and dissolution.**
8. **D8 Ecology of several superagents.**
9. **D9 Hierarchy and scale.**
10. **D10 Structural thermodynamics of ideology.**

## Access
- **Tier 0:** observational, from the logs.
- **Tier NE:** natural experiments at documented step changes. These replace simulation; we can't run new swarms.
- **Tier 1:** replay of logged agents with scrambled context. Waits on the exact prompts (`llm_calls`), to be requested from AI Digest eventually.

## Model
**From:** `physics-models/04-semantic-information`. Ideology order parameter: models 11 or 10. Groupings: model 10. Dynamics: models 02 and 09.

## Data scheme / Observables / Null
Per sub-hypothesis once chosen. Planned schemes: S1 (observational order parameter), S2 (event studies around natural experiments), S3 (replay). See architecture §5. For D3.1.a / D3.2, S1 is built by `scheme/build.py` (details in its docstring and in Amendment 2 below); observables and nulls are listed under the starting-set predictions.

## Faithfulness scorecard
Scored for D3.1.a + D3.2 (model 11 vector spins, mapping = per-regime whitened bge-small statement vectors, n = 32; windows = non-holdout units of exploratory round 1). 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** D3.2′ field-only (goal ĝ + agent fields h_i + room fields); D3.2 coupling through the room channel (exposure-weighted). Room-specific fields (per-room kickoffs) are the standing confound between them.
**Locked holdout used for confirmation:** NE12 window (placebo), #34 (#voted-out), the NE15 pre-split window, and #45–#47 for transfer. Script: `analysis/confirm_d32.py` (not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Statements, rooms, exposure and fields all defined from shared tables (scheme docstring, Amendment 2). Not invariant: whitening is per regime, the cross-period agent field fails the invariance check in regimes II/III (median cos 0.31), and statements mix two genres (chat 59%, intentions 41% in regime III). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Day 1 reported separately and drift tested: P1 day-1 ΔH −0.086 vs days 2+ −0.101; residual alignment drifts up within some weeks (+0.06/day in #36b, #41, #44). No Markov or update-order audit. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Rooms beat random same-size partitions on 74% of days (mean z −3.3); the exposure slope beats rotation (p = 0.005) and day-shuffle (p = 0.025) nulls. But P5's field R² does not beat its rotation null, the RE slope misses p < 0.01, and P9 fails. No held-out likelihood comparison. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Predicted jump at goal changes appears (whole-swarm JSD across goal boundaries 0.62 vs 0.37 within; 79% above the within-unit 90th percentile). Predicted stability (P3) and the #8 > #21 contrast (P4) fail. Mean-field forward predictions (susceptibility at kickoffs) not tested. |
| E interventional | predicts the change across a natural experiment | 1 | 05-04 merge DiD +0.18 (permutation p = 0.004), robust to every instrument variant (+0.10 to +0.23); the 05-11 split mirror (dry-run stand-in) −0.24. Confounded with goal changes; NE32 not estimable; holdout NEs pending. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic: P6 has correct size and full power for weak coupling but saturates at strong coupling; P1 has correct size but needs strong order to meet −0.1; P9 recovers βJ₀/n with a 10–15% downward bias; P5 R² has a large geometric floor. Robustness: P1 direction survives k, d, weights, seeds and a lexical swap; P1 size and the P6 slope do not (P6 ≈ 0 at d = 16 or with cross-fitted h; +0.012, p = 0.001 at d = 64). |
| G ground truth | agrees with known structure | 1 | Known rooms are recovered as more-ordered groups (9/9 primary units, direction) with a within-room residual excess in 12/12 two-room units; labs (families) are also below random. No blind partition recovery. |
| H comparative | beats the named rivals | 0 | Field-only vs coupling not compared by likelihood; room fields not separated from room coupling (room-ĝ removal changes the within-room excess by < 0.02, but kickoff embeddings are a noisy proxy). |
| I transfer | holds in other same-mode periods, including the holdout | 1 | P1 direction holds in 9/9 primary units; P6 slope heterogeneous (I² 0.32; negative in #35, #38b, #42). Holdout not used. |

## Prediction
*Write one per chosen sub-hypothesis, before running it on real data.*

### Starting set: D3.1.a and D3.2 (written 2026-10-03, before any embedding analysis)

**What I had seen when writing this:** the H02 and H05 round-1 results (pairwise activity couplings at the null floor; weak collective co-activation, mean-field loop gain ≤ 0.36; within-room *talk* coupling > cross-room in 6/6 regime-III windows; NE12 on 02-25 separated no pair). The H04 result (nudges act through the agent's unread context, with a delayed response) arrived while this was being written. I had not seen any embedding, cluster or alignment statistic. The embeddings were still being computed.

**Scheme S1 (observational order parameter)**, built by `scheme/` from the shared tables plus `data/processed/shared/embeddings/`:
- **Statements:** each agent's own chat messages and self-written intentions, grouped per agent per day. Holdout days are masked (`holdout_mask`).
- **Vectors:** bge-small-en-v1.5 embeddings. Within each regime, subtract the regime mean and whiten with PCA to n = 32, fitted on non-holdout days. Agent-day vectors are the normalized means of their statements.
- **Meaning clusters:** k-means with k = 40 per regime, fitted on non-holdout statements. Sensitivity runs use k = 20 and 80.
- **Semantic entropy:** H_G(t) = −Σ_c p ln p over the clusters of group G's statements on day t. Each agent's statements are weighted equally, so verbose agents don't dominate. Rarefy to a fixed number of statements per agent, so groups of different sizes compare fairly.
- **Polarization:** |m_G(t)| of the group's agent-day vectors (model 11).
- **Goal direction ĝ:** the embedding of the goal text and kickoff, centered and whitened like everything else.
- **Agent field h_i:** agent i's mean vector over *other* goal periods (cross-fitted). It stands in for pretraining prior and writing style.

**D3.1.a: an ordered phase exists, as measured on mined statements.**
- **P1, rooms are ordered units.** On non-holdout regime-III days with two or more populated rooms (#35 after the split, #38, #39–#42, #44, #focus), room groups have lower H than random same-size groups of the agents present that day:
  - on ≥ 60% of days;
  - median ΔH ≤ −0.1 nats.

  Null: 1,000 random partitions per day that keep the room sizes.
- **P2, lab "order" is mostly style.** Lab groups are also below random on raw vectors. Removing the agent field h_i shrinks the lab ΔH by ≥ 50% and the room ΔH by < 50%.
- **P3, order is stable.** Within a goal period, a room's cluster distribution changes less from day to day than a random group's (Jensen–Shannon distance below the 5th percentile of the null on ≥ 60% of day pairs). At goal changes it jumps (NE34), which sets up D3.3.a.
- **P4, single-room regime-I weeks (#8, #21).** No partition to test, so this is descriptive only:
  - whole-swarm polarization along ĝ is high in #8 (benchmark design, a strongly fielded week);
  - it is lower in #21 (forecasting, individual-objective).

**D3.2 (coupling-driven order) ⟷ D3.2′ (field-driven order).** My prior is that order is **mostly field-driven, with a small but real coupling residual in regime III**.
- **P5, field dominates.** Across non-holdout pair-days, ĝ and the agent fields (h_i, h_j) together explain ≥ 60% of the variance in pairwise alignment a_ij(t) = cos(v_i(t), v_j(t)). Measured as R² of a_ij on the field-projection terms.
- **P6, a coupling residual exists.** The residual alignment r_ij(t), left after projecting out ĝ and h_i, h_j, increases with same-day exposure E_ij(t) (log count of j's messages that i saw, from `exposure`):
  - with pair and day fixed effects;
  - slope > 0 at p < 0.01 in regime III, in both directions i→j and j→i;
  - in two-room weeks, within-room pairs have a larger residual than cross-room pairs, the content analogue of H05's talk result.

  In regime I everyone is in #general, exposure is nearly uniform and the slope has no leverage there; it is reported but not counted. Given H04, also test exposure lagged by one day: a delayed context channel should couple at least as strongly the next day.
- **P7, the 05-04 merge (#40) as a difference-in-differences.** Pairs that newly became co-located show a rise in residual alignment relative to pairs whose co-location didn't change; GPT-5, left alone in #rest, shows no rise. *Direction only:* #40 was a shared-objective week, so goal type is confounded with the merge.
- **P8, the NE32 triplet (07-09 isolated, merged 07-10; #51, non-holdout).** Descriptive, n = 3:
  - on 07-09 the three GPT-5.6 agents align with ĝ about as strongly as incumbents do (field);
  - their alignment with each other is high despite no exposure (same-family field);
  - their residual alignment with incumbents is below the incumbent–incumbent level on 07-09 and rises on 07-10 and after.
- **P9, the mean-field version (D3-MF.a).** Fit (βJ₀, h) of mean-field O(n), with n = 32, to each period's polarization and its fluctuations.

  Prediction: βJ₀ < 0.5 × the mean-field critical value (βJ₀ = n) in every period, with h carrying the order. This would be the content-level counterpart of H02 and H05's low loop gains.

**Nulls:**
- random same-size groups (P1 to P3);
- per-agent random rotation, which keeps each trajectory but destroys cross-alignment;
- days shuffled within a goal period;
- an embedding-model swap (a second model before any claim is promoted).

**Falsifiers:**
- **D3.1.a fails** if room groups are not more ordered than random groups (ΔH ≥ 0 on most days). Rooms would then not be ideological units.
- **D3.2′ (field) fails** if the field terms explain < 30% of a_ij, or if the exposure slope is large (≥ 0.1 in residual cosine per e-fold of exposure).
- **D3.2 (coupling) fails** if the exposure slope and the within-room > cross-room difference vanish under the rotation null.

**Amendment 1 (2026-10-03, before any analysis; project rule: the goal period is the unit of analysis).**
- **Per-period fits.** P5–P7 are fitted *per goal period*: non-holdout regime-III periods with ≥ 2 days, plus #35 after the split and #focus as sub-periods.
  - **P5 holds** if R² ≥ 0.6 in ≥ 2/3 of periods.
  - **P6 holds** if the exposure slope is positive in ≥ 2/3 of periods *and* the random-effects summary is > 0 at p < 0.01. Heterogeneity across periods (τ², I²) is reported, not averaged away.
  - **P1 and P3** are per day within periods, and are reported per period.
- **Exceptions used, per the project rule:**
  - (a) the whitening basis and k-means clusters are fitted per regime: a shared ruler, so periods are comparable;
  - (b) the agent field h_i is cross-fitted from *other* periods. Invariance check first: h_i estimated from two disjoint sets of other periods must agree (median cos ≥ 0.5 after whitening). If it fails, h_i is estimated within the period from the agent's first day only, and P5/P6 use days 2 onward.
- **Within-period stationarity is checked, not assumed.** Day 1 (just after kickoff) is reported separately, with a drift test across days.

**Amendment 2 (2026-10-03, operational details fixed before any real-data test of P1–P9 was run).**
*What I had seen:* the scheme build outputs (statement and agent-day counts, the unit list, which kickoff messages were found, room membership counts per unit); three generic instrument statistics used to calibrate the synthetic world (regime-III statements per agent-day: 10th/50th/90th percentile 9/36/103; within-agent-day resultant length ≈ 0.63; resultant of an agent's day vectors within a unit ≈ 0.85); and the synthetic validation (`analysis/synthetic.py`). No real-data alignment, entropy, room, exposure-slope or mean-field statistic had been computed. Thresholds and predictions above are unchanged.
- **Units.** Goal periods split at catalogued step changes inside them: #36 at 03-24 (regime boundary; 36a regime II, one day, 36b regime III); #38 at 04-14 (NE17) and 04-20 (NE18); #51 at 07-09 (NE32), 08-05 and 08-25 (#focus, 51c) and 09-03 (NE33). Amendment 1's P5–P7 set is therefore 35, 36b, 37, 38a, 38b, 38c, 39, 40, 41, 42, 44, 51a–51e (16 units).
- **P1.** Eligible agent-day: ≥ 8 statements and a known room (time-weighted modal room over the day's window). "Populated room" = ≥ 2 eligible agents; days with fewer than 2 populated rooms are skipped, so #40 (merged; GPT-5 alone in #rest) has no P1 days. Statistic: size-weighted mean entropy over rooms with ≥ 2 agents, rarefied to 8 statements per agent (20 draws), k = 40; null = 1,000 permutations of agents over rooms keeping room sizes; ΔH = observed − null mean. #36b and #37 (two-room, regime III, not in the card's list) are reported as secondary and not counted.
- **P2.** Labs from `roster.lab`. "Removing the agent field" = projecting each statement off its agent's cross-fitted ĥ_i direction, renormalizing, and re-clustering (k = 40, per regime). Shrinkage = 1 − median ΔH(after) / median ΔH(before) over the P1 days.
- **P3.** Consecutive day pairs within a unit; a room's distribution on each day from its members that day; null = 500 random fixed-membership groups of the room's size from agents eligible on both days.
- **ĝ.** unit(unit(goal text) + unit(kickoff)), the kickoff being the human messages ≥ 250 chars posted within 45 min of the window opening on the period's first day, minus sentences about the previous goal. For #51 units each agent's own assigned goal (`agent_goals`, NE26) is added to its field subspace, since it is part of that agent's goal text. Room-specific kickoffs (#38, #44 differ by room) enter only a robustness variant.
- **h_i.** Mean of the agent's unit agent-day vectors over non-holdout days of other goal periods in the same regime (the whitening basis is per regime). If the agent has none (newcomers in #51; Fable 5 and Sonnet 5 appear only in held-out periods before #51), use the other sub-units of the same goal period; else the agent's first day in the unit, dropping its pairs on that day (Amendment 1's fallback, per agent). If the invariance check fails, Amendment 1's fallback applies to every agent.
- **P5.** For each pair-day, project both agent-day vectors onto the pair's field subspace span{ĝ, ĥ_i, ĥ_j (+ agent goals)}: a_ij = φ_ij (field part) + ρ_ij (residual) exactly. R² of a_ij on [T_g = (v_i·ĝ)(v_j·ĝ), φ_ij − T_g] by OLS per unit (agent-days with ≥ 3 statements). Reported next to two references from the synthetic: the per-agent rotation null, which is *not* ≈ 0 (0.30–0.34 with strong agent fields, because the projection captures the random relative orientation of the agents' own fields), and the split-half reliability of a_ij (noise ceiling). The 0.6 threshold is kept; even the oracle R² with the true fields was 0.56–0.60 in the synthetic world, so P5 is a demanding test.
- **P6 (one method change, motivated by the synthetic design).** Exposure counts co-vary with statement counts, and fewer statements make agent-day vectors noisier, which attenuates alignment. Residual alignment r_ij(t) = cos of the residuals is therefore computed on **rarefied agent-day vectors** (8 statements per agent-day, averaged over 10 draws), so the sampling noise is the same every day; agent-days with < 8 statements are dropped from P6. The full-vector estimator with log-count controls is reported as a variant. "The exposure slope" of Amendment 1 uses x = log(1 + E_i←j + E_j←i) with pair and day fixed effects and pair-clustered SEs; the random-effects (DerSimonian–Laird) summary must be > 0 at two-sided p < 0.01. "Both directions" = the joint regression on log(1 + E_lo←hi) and log(1 + E_hi←lo) (labelled by agent code; "both > 0" does not depend on the labelling), each RE summary > 0 at p < 0.01. Rotation and day-shuffle nulls (200 draws) are applied to each unit's slope and to the RE summary. The one-day lag is tested **jointly** with same-day exposure: in the synthetic, a separate lag regression is biased negative under same-day coupling (pair fixed effects in a 4–5-day panel). The room part: within-room minus cross-room pair-mean residual > 0 in ≥ 2/3 of two-room units, with agent-level room-label permutation and rotation nulls and a room-ĝ_r robustness variant.
- **Synthetic warnings carried into the interpretation (not changing verdict rules).** (i) The exposure slope detects coupling only in the weak, linear-response regime: at strong coupling (J = 0.4) alignment saturates and the slope returns to ≈ 0 while within − cross becomes large. (ii) A room-specific field alone makes within > cross (+0.05 at a_ρ = 0.3, J = 0); a noisy room ĝ removes only part of it. So the room criterion is not specific to coupling. (iii) P1's −0.1 nats threshold is only reached with strong ordering (synthetic coupling J ≥ 0.1); a room field of 0.3 gave ΔH ≈ −0.05 with 79% of days negative; the direction-only part (≥ 60% of days) has a ~30% false-positive rate under the null, so it is never read alone. (iv) The P9 estimator recovers βJ₀/n with a 10–15% downward bias at βJ₀/n ≥ 0.5, so estimates ≥ 0.4 are treated as compatible with the 0.5 threshold.
- **P7.** h_i excludes both #39 and #40 (one agent field on both sides of the boundary); DiD of rarefied residual cosines with pair and day fixed effects; arms "new" (best × rest pairs, GPT-5 excluded) vs "stay"; GPT-5's arm separately; assignment permutation of the #39 room labels.
- **P8.** The triplet's 07-09 vectors use only statements posted while in their isolated rooms; their h_i comes from the other #51 sub-units by the h_i rule (none of 07-09/07-10 enters it).
- **P9.** βJ₀ from the collective enhancement R = 1 + (N̄ − 1)ρ̄ of within-agent day-to-day deviations (cross-agent covariances; split halves for each agent's own signal variance, which removes statement-sampling noise), solved with the mean-field O(32) linear response; βh = x − βJ₀ m with x = A₃₂⁻¹(m), m = mean v·ĝ. Every unit with ≥ 2 days. A common day-varying field inflates R, so βJ₀ is an upper bound on mean-field coupling.
- **Multiplicity.** The verdicts are the card's P1–P9 criteria. Everything else (per-day p-values, variants, nulls) is descriptive. Exploration windows other than these units are descriptive only.

**Amendment 3 (2026-10-03, after the h_i invariance check, before P2 and P5–P8 were run).**
*What I had seen:* only the invariance result. Median cos(h_A, h_B) from disjoint sets of other periods: regime I 0.55 (pass), regime II −0.07 (fail; only three non-holdout periods, so each half is a single period), regime III 0.31 (fail; between-agent baseline −0.02). So agents are distinguishable, but their cross-period mean is not stable enough for the 0.5 rule.
- **Primary (per Amendment 1):** in every regime II/III unit, h_i = the agent's own first day in the unit; P5/P6 use each agent's days after its first day. Day 1 therefore cannot be reported for P5/P6 under the primary rule; it is reported under the cross-fitted variant.
- **P2** removes this first-day h_i and is evaluated on days 2+ only.
- **P7** uses one h_i on both sides of the boundary: the agent's first #39 day (dropped from the DiD).
- **P8** is descriptive and the fallback would put h_i on the isolation day itself (07-09 is the triplet's first day), which destroys the test. P8 keeps Amendment 2's rule (h_i from the other #51 sub-units, never 07-09/07-10) and also reports raw alignments without any h_i.
- **Variant:** P5/P6 are also run with the cross-fitted h_i of Amendment 2, labelled secondary.

**Confirmatory (held out; run only after sign-off).** NE12 itself is a **placebo**: H05 found it separated no pair. The real cuts are #voted-out (03-05/06, inside held-out #34) and the #best/#rest split on 03-16 (NE15, whose pre-split window is held out).

Confirmatory prediction: after the split, the residual alignment of cross-room pairs falls toward the field-only level while within-room pairs hold. At 02-25 nothing changes. This reuses H05's pair-separation machinery.

*Added 2026-10-03 after exploratory round 1, before any holdout use:* the operational confirmatory criteria C1–C6 are in [`NE15/README.md`](NE15/README.md) and machine-readable in `analysis/confirm_d32.py` (`PREDICTIONS`).

## Results

### Exploratory round 1 (2026-10-03; non-holdout only, holdout asserted absent in every script)
**Labeled exploratory.** Scheme: 184,713 statements (128,359 chat messages, 56,354 intentions), 3,186 agent-days, 42 units, in `data/processed/H01-emergent-superagents-exist/` (74 MB incl. the lexical instrument). Code: `scheme/build.py`, `analysis/{synthetic,explore,summarize,figures,period_cards}.py`. Numbers: `explore*.json`, `synthetic_validation.json`, `robustness_summary.json`, `G##/results.json`. One-page summary: `figures/summary.pdf`.

**Headline.** Rooms are reliably more ordered than random groups of the same agents (ΔH < 0 on 96% of 54 days, p < 0.05 on 74%), but the median effect (−0.098 nats; −0.096 ± 0.003 over five rarefaction seeds) just misses the pre-registered −0.1, and the order is largest where rooms were given different instructions (a room field). There is a small coupling residual: the exposure slope is positive in 12/15 units and beats the rotation null (p = 0.005), but its random-effects summary (+0.013 residual cos per e-fold) misses p < 0.01 and it is instrument-sensitive. Merging rooms raises the residual alignment of newly co-located pairs (+0.18, permutation p = 0.004). The predicted "field dominance" is not supported in substance: P5 passes only at the level of its rotation null, and the mean-field coupling bound is large (P9 fails), with day-to-day co-fluctuation concentrated inside rooms.

**Synthetic validation (axis F; `figures/synthetic_validation.pdf`, 24 worlds per setting, village-like N, days and statements).**

| Check | Result |
| --- | --- |
| P6 size (J = 0) | P6 criterion met in 0/24 worlds (rarefied and full-vector); per-unit one-sided p < 0.01 in 2.7% (rarefied) / 0.4% (full). Rotation null rejects 12.5% of units at α = 0.05 with a room field (5.7% without): mildly anti-conservative. |
| P6 power | J = 0.05 / 0.1 / 0.2: RE slope +0.049 / +0.062 / +0.047, criterion met in 100% / 100% / 100% (rarefied; full-vector 92 / 92 / 21%). J = 0.4: slope ≈ 0, 0% (saturation) while within − cross rises to +0.64. |
| Lag | separate lag regression −0.01 under same-day coupling (fixed-effect bias); joint same-day + lag estimate ≈ 0 (correct). |
| Room-field confound | J = 0, room field 0.3: within − cross +0.054 (+0.034 after removing a noisy room ĝ); without a room field +0.001. |
| P5 | R² with estimated fields 0.38, oracle 0.56, rotation null 0.32 (J = 0); 0.19 at J = 0.2. The rotation null is not ≈ 0. |
| P1 size / power | null: day-level p < 0.05 on 3.9% of days, criterion 0/24, direction-only part 29% false positives. Room field 0.3: 79% of days < 0, median −0.046, criterion 0%. Coupling 0.1: median −0.108, 54%; coupling 0.2: 100%. |
| P9 | true βJ₀/n 0 / 0.25 / 0.5 / 0.75 → median estimates −0.08…0.03 / 0.21…0.28 / 0.40…0.47 / 0.63…0.68 (N = 13, T = 5 and N = 20, T = 15); βh within ~10%; a common day field of strength 1.5 adds ≤ 0.05. |

**h_i invariance (Amendment 1(b), run first).** Median cos(h_A, h_B) from disjoint sets of other periods: regime I 0.55 (pass), regime II −0.07 (fail; three periods), regime III 0.31 (fail; between-agent baseline −0.02). So the Amendment 1 fallback (first-day h_i, days 2+) is primary (Amendment 3); the cross-fitted h_i is a reported variant.

**Outcome vs prediction**

| | Prediction (locked) | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 | rooms below random on ≥ 60% of days and median ΔH ≤ −0.1 nats | 96% of 54 days < 0; p < 0.05 on 74%; median −0.098 (seeds −0.093…−0.099); 5/9 units meet both criteria; days 2+ −0.101, day 1 −0.086 | **not met** (size missed by 0.002; direction strong) |
| P2 | labs below random; removing h_i shrinks lab ΔH ≥ 50% and room ΔH < 50% | labs < 0 on 93% of days (median −0.073); shrink: labs 13%, rooms 33% | **failed** (lab order is not removed by h_i) |
| P3 | room JSD day-to-day below the null 5th percentile on ≥ 60% of day pairs; jumps at goal changes | 14% of 95 room-day pairs (median null percentile 0.32). Goal changes: whole-swarm JSD 0.62 across vs 0.37 within | **failed** (stability); jump part as predicted |
| P4 | #8 polarization along ĝ high, #21 lower | #8 0.267 vs #21 0.268 (ranks 11 and 10 of 24 regime-I units; null sd 0.09 / 0.06) | **not as predicted** |
| P5 | ĝ, h_i, h_j explain ≥ 60% of a_ij variance in ≥ 2/3 of units | 12/16 units ≥ 0.6, median R² 0.76; rotation-null median 0.75; reliability 0.95. Cross-fitted h: 2/16, median 0.35 (null 0.24) | **met by the letter, null-level**: not evidence for field dominance |
| P6 | slope > 0 in ≥ 2/3 units and RE > 0 at p < 0.01; both directions; within > cross | 12/15 > 0; RE +0.0131 ± 0.0056 (p = 0.019; rotation-null p = 0.005, day-shuffle p = 0.025; τ² 1e-4, I² 0.32). Directions +0.013 (p = 0.0003) and +0.023 (p = 0.004). Within > cross in 12/12 two-room units (8 with p < 0.05). Joint lag +0.006 (p = 0.03) < same-day +0.011 | **not met** (RE p > 0.01). Falsifiers: D3.2′ "slope ≥ 0.1" not triggered; D3.2 "vanishes under rotation" not triggered |
| P7 | merge: new pairs' residual rises vs stay; GPT-5 no rise (direction only) | DiD +0.178 ± 0.048 (permutation p = 0.004; 40 new vs 51 stay pairs); GPT-5 arms −0.08 (n.s.) | **as predicted** (confounded with a shared-objective goal change) |
| P8 | triplet ≈ incumbents on ĝ; high mutual alignment without exposure; residual with incumbents rises after merge | no statements were written while isolated; descriptive post-merge numbers in `NE32/` | **not estimable as designed** |
| P9 | βJ₀ < 0.5 n in every unit, h carries the order | median βJ₀/n 0.74; ≥ 0.5 in 34/41 units; day-shuffle null R ≈ 1 (p ≤ 0.01 in 40/41) | **failed** (upper bound; see the room split below) |

**Per-period heterogeneity (regime II/III units; full tables in the G folders).**

| unit | P1 median ΔH | P5 R² (rotation null) | P6 slope ± SE | within − cross | P9 βJ₀/n | ρ_within / ρ_cross |
| --- | --- | --- | --- | --- | --- | --- |
| 35 | −0.070 | 0.15 (0.49) | −0.019 ± 0.015 | +0.22 | 0.87 | 0.66 / 0.09 |
| 36b* | +0.031 | 0.71 (0.74) | +0.037 ± 0.020 | +0.08 | 0.82 | 0.31 / 0.15 |
| 37* | −0.024 | 0.50 (0.59) | +0.042 ± 0.110 | +0.01 | 0.76 | 0.30 / 0.26 |
| 38a | −0.336 | 0.35 (0.52) | +0.091 ± 0.067 | +0.33 | 0.74 | 0.37 / 0.04 |
| 38b | −0.382 | 0.96 (0.90) | −0.056 ± 0.060 | +0.08 | 0.55 | 0.16 / 0.05 |
| 38c | −0.376 | 0.92 (0.86) | +0.007 ± 0.038 | +0.12 | 0.48 | 0.13 / 0.03 |
| 39 | −0.037 | 0.75 (0.75) | +0.018 ± 0.020 | +0.09 | 0.66 | 0.17 / 0.08 |
| 40 | no P1 days | 0.77 (0.82) | +0.027 ± 0.042 | +0.13 | 0.89 | 0.26 / 0.12 |
| 41 | −0.190 | 0.50 (0.64) | +0.082 ± 0.032 | +0.16 | 0.82 | 0.47 / 0.04 |
| 42 | −0.038 | 0.86 (0.83) | −0.019 ± 0.022 | +0.03 | 0.87 | 0.19 / 0.14 |
| 44 | −0.110 | 0.80 (0.74) | +0.039 ± 0.070 | +0.24 | 0.74 | 0.34 / −0.01 |
| 51a | – | 0.82 (0.81) | +0.039 ± 0.045 | – | 0.73 | – |
| 51b | – | 0.61 (0.61) | +0.008 ± 0.006 | – | 0.65 | – |
| 51c (#focus) | −0.071 | 0.70 (0.67) | +0.010 ± 0.004 | +0.07 | 0.60 | 0.06 / 0.01 |
| 51d | – | 0.77 (0.78) | +0.038 ± 0.014 | – | 0.44 | – |
| 51e | – | 0.94 (0.92) | (one usable day) | – | 0.35 | – |

\* secondary for P1 (not in the card's list). Partial pooling: the random-effects summaries above are reported next to every per-unit estimate; P1 and P9 are not pooled.

**Robustness (`figures/robustness.pdf`).**

| Variant | P1 median ΔH (days < 0) | P6 RE slope (p) | P5 units ≥ 0.6 (median R², rot) | P7 DiD (perm p) | P9 median βJ₀/n |
| --- | --- | --- | --- | --- | --- |
| primary: bge, d 32, k 40, first-day h | −0.098 (96%) | +0.013 (0.019) | 12/16 (0.76, 0.75) | +0.18 (0.004) | 0.74 |
| cross-fitted h | −0.094 (96%) | +0.004 (0.54) | 2/16 (0.35, 0.24) | +0.10 (0.026) | – |
| k = 20 / k = 80 | −0.095 / −0.108 (98% / 96%) | – | – | – | – |
| per-message weights | −0.095 (94%) | – | – | – | – |
| d = 16 | −0.088 (96%) | +0.002 (0.85) | 13/16 (0.82, 0.85) | +0.23 (0.002) | 0.73 |
| d = 64 | −0.113 (96%) | +0.012 (0.001) | 9/16 (0.67, 0.66) | +0.13 (0.006) | 0.69 |
| lexical tf-idf instrument (embedding-swap stand-in) | −0.077 (89%) | +0.010 (0.22) | 14/16 (0.83, 0.88) | +0.13 (0.008) | 0.76 |

P1's direction survives every variant; its size criterion is met only at k = 80 and d = 64. P6's slope is met only at d = 64. P7 survives everything. P9 fails everywhere.

**What this means.**
1. **D3.1.a (order on mined statements): partly.** Rooms are ordered units in the weak sense (consistently below random partitions) but the effect is small except where rooms had different instructions (#38: −0.34 to −0.38; #44: −0.11) or in #41 (−0.19, same task in both rooms). Room cluster distributions are not more persistent than random groups' (P3), so the order is a daily alignment, not a fixed ideology; the swarm's whole distribution jumps at goal changes.
2. **D3.2 vs D3.2′: neither pure form.** The field prior fails in substance: field R² is at its geometric floor, the goal direction explains little except in #42 (goal-only R² 0.54), and the agent's cross-period style is not stable enough to act as a field. A coupling residual exists but is small: +0.013 residual cos per e-fold of exposure, positive in both directions, larger the same day than the next, and robust to rotation but not to the instrument. The merge DiD is large and robust but confounded with a goal change.
3. **The collective co-fluctuation is local.** Agents in the same room move together from day to day (ρ_within 0.06–0.66 across the nine primary two-room units) much more than agents in different rooms (−0.01 to 0.14), in every one of them. That is what drives P9's large βJ₀. It points to the room as the unit of shared dynamics, through coupling or through room-specific daily drives (operator messages, nudges, room kickoffs); the observational data cannot separate the two. This is the main thing the holdout NE15 test can decide.

**Caveats.**
- Amendments 2 and 3 were made before the affected tests, after seeing only the scheme counts, three generic instrument statistics, the synthetic results and (for Amendment 3) the invariance numbers.
- The primary agent field is the agent's first day (forced by the failed invariance check). It contains day-1 content, not just style, which makes P5 mechanical and weakens P2. The cross-fitted variant gives different P5/P6 numbers; both are shown.
- Room fields confound P1 and the room criterion (per-room kickoffs in #38 and #44, separate RPG forks in #35). Projecting out the room's kickoff direction barely changes the within-room excess, but kickoff embeddings are a noisy proxy (the synthetic removal recovered about a third).
- The exposure slope is identified from day-to-day variation in a pair's chat volume. Days with a shared subtask raise both, which a fixed-effects design cannot exclude, and at strong coupling the slope saturates.
- P9 is an upper bound that conflates room-local drives with coupling; it is reported because it was predicted, not because it identifies J₀.
- Embeddings mix style and topic. The only available swap was lexical (no second neural model is cached and the network was off); it reproduces the qualitative picture with weaker effects.
- Many units, variants and nulls: only the P1–P9 verdicts are counted; per-unit p-values are descriptive.
- Statements are what agents *say* (narration is a claim). The Claude Code agent's chat is included in #35–#37.

**Confirmation.** `analysis/confirm_d32.py` (NE15 cut DiD, pooled TWFE, NE12 placebo, transfer to #45–#47) is written and dry-run on non-holdout stand-ins; it refuses to run on the holdout without `--confirm --i-understand-this-uses-the-locked-holdout`. See [`NE15/`](NE15/README.md).

### Results by goal period

| Folder | Units | Verdict | One line |
| --- | --- | --- | --- |
| [G08](G08/README.md) | 8 | descriptive | P4: polarization along ĝ 0.27, same as #21 (not as predicted); βJ₀/n 0.49 |
| [G21](G21/README.md) | 21 | descriptive | P4 contrast fails (0.27); strong day-to-day co-fluctuation (βJ₀/n 0.86) |
| [G35](G35/README.md) | 35 | mixed | rooms ordered (−0.07), big within-room excess (+0.22) but slope ≈ 0 and field R² 0.15 |
| [G36](G36/README.md) | 36a, 36b | failed | secondary: no room order (ΔH > 0) |
| [G37](G37/README.md) | 37 | failed | secondary: weak order, no room excess, cross-room co-fluctuation as large as within |
| [G38](G38/README.md) | 38a–c | mixed | strongest room order (−0.34 to −0.38) with rooms given different goals (room field); slopes mixed |
| [G39](G39/README.md) | 39 | mixed | weak room order, strong lab order (−0.25); pre-window of the merge |
| [G40](G40/README.md) | 40 | supported (P7) | merge DiD +0.18 (perm p = 0.004), confounded with the goal change |
| [G41](G41/README.md) | 41 | mixed | most coupling-like week: order −0.19, slope +0.08, within +0.16, ρ_within 0.47 vs 0.04 |
| [G42](G42/README.md) | 42 | mixed | field-dominated: goal-only R² 0.54, little room effect |
| [G44](G44/README.md) | 44 | mixed | rooms ordered (−0.11) and within +0.24, but per-room goal override |
| [G51](G51/README.md) | 51a–e | mixed | small positive slopes in the big single room; #focus ordered (−0.07) |
| [NE32](NE32/README.md) | 51b | n/a | triplet wrote nothing while isolated |
| [NE15](NE15/README.md) | holdout | pending | confirmatory test (not run) |

P9 for the remaining 26 non-holdout units (regime I and #33) is in `figures/p9_meanfield.pdf` and `data/processed/H01-emergent-superagents-exist/G##/results.json`; those periods have no period-specific prediction beyond P9 and get no folder.

## Notes
- 2026-10-03: **exploratory round 1 of D3.1.a / D3.2 done** (one of several parallel agents; local compute only, ≤ 4 threads). Synthetic validation first, then Amendments 2 and 3, then real data. Holdout asserted absent in the scheme and in every exploratory loader. Folder convention: per-goal-period `G##/` cards and `NE##/` spanning tests (Vivian, 2026-10-03).
- 2026-10-03: `chat_core.mentions` is not used anywhere in H01 (exposure comes from the shared `exposure` table), so the mentions fix does not affect these results.
- 2026-10-03: the shared embedding agent states (`data/processed/shared/embeddings/agent_day*`, `whitening_<regime>.npz`) could replace this scheme's whitening fit but not its products: H01 needs per-statement whitened vectors (rarefaction, split halves, clusters), k-means rulers, goal fields, exposure pairs and holdout-free files. The shared agent-day vector normalizes raw means before whitening; H01 whitens each statement first.
- 2026-10-03: **next steps.** (1) Sign off and run `analysis/confirm_d32.py --confirm …` (NE15, #voted-out, NE12 placebo; transfer to #45–#47). (2) Separate room fields from room coupling: per-room operator/nudge messages as explicit room-day fields in the P6/P9 designs; blind partition recovery from residual alignment. (3) Event-level coupling: reply-conditioned alignment (does i's next message move toward j's last one?) instead of day-level exposure counts. (4) A stable style field: estimate h_i from many periods with topic regressed out, then retry P2/P5. (5) Mean-field forward predictions (kickoff susceptibility, transverse vs longitudinal fluctuations) per D3-MF. (6) A second neural embedding model when the network is available, for the key results.
- 2026-10-03: recorded as an idea.
- 2026-10-03: terminology settled: "semantic entropy" → Kolchinsky–Wolpert semantic information; meaning-cluster entropy kept as the order parameter.
- 2026-10-03: predictions for D3.1.a and D3.2 written (P1–P9). **NE12 is a placebo, not a cut** (per H05): the D3.2 confirmatory test moves to the actual separations (#voted-out, NE15).
- 2026-10-03: **starting set chosen by Vivian: D3.1.a** (ideology order parameter from mined statements) **and D3.2** (coupling- vs. field-driven order). Both need Phase 2 (embeddings / meaning clusters). D3.2's strongest test (NE12) is held out, so exploration uses #8, #21, #41 and the NE32 isolated triplet.
- 2026-10-03: renamed from "Emergent superagents and the thermodynamics of ideology" to **"Emergent superagents exist"**. Sub-hypothesis set (D1–D10) written. No new swarms, so simulation was replaced by natural experiments. `llm_calls` to be requested eventually. Probes: both mined and fixed. Viability left open, with candidates in D2.
