# H01: Emergent superagents exist

**Status:** running. **Round 2 (2026-10-04, non-holdout only): no effective superagents found.** Candidate multi-agent units (artifact crews, behavior-synchrony, co-allocation and reply communities; rooms and labs as baselines) are not individuality maxima, carry no measurable Kolchinsky–Wolpert semantic information about their activity environment, show no group-level repair, and are out-persisted by single agents with their own artifacts; their work allocation survives nightly context erasure and memory loss (stigmergic, artifact-held) and their rate is set by the operator's goal. Timing-individuality tests had ≤ 7% validated power, so R4's null is weak. Confirmatory `analysis/confirm_r2.py` (NE30, NE24, holdout units) written and dry-run, **not run**. Round 1 (D3.1.a/D3.2) below, with a 2026-10-04 correction (#38 room kickoffs), H26's note on P9 and a **round 1b re-run on improved data (2026-10-04)**: room order replicates in both embedding models and survives style removal, lab order is style (P2 now supported), the coupling residual is stable but its p < 0.01 criterion instrument-dependent, the merge DiD is partly style; natives: NE42 A-B-A supports channel-borne room order, #12 drafted teams are not units. Level: hypothesis. (Proposed 2026-10-03 by Vivian Rogers.)
**Fields:** info theory, stat mech, thermodynamics, sociophysics
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md); [Sowinski et al. 2023](../../literature/sowinski-2023-semantic-information-resource-gathering-agents.md); [Bartlett et al. 2025](../../literature/bartlett-2025-physics-of-life-information-roadmap.md); [arXiv:2608.16578](../../literature/arxiv-2608.16578-physics-of-agents.md) (not yet read). Further reading: [architecture.md](architecture.md#reading-list-from-the-transcript-citations-to-verify).
**Definitions used:** *superagent*, *ideology*, *semantic information*, *semantic entropy (meaning clusters)*: drafts in `physics-models/DEFINITIONS.md`. Round 2 also uses *semantic information (natural-scramble variant)* (H15) and proposes the named variants *superagent (effective, Kolchinsky–Wolpert)*, *unit macro-state (work ledger)* and *allocation continuity (ΔC)*, defined in "Round 2 formal setup". They are not yet in DEFINITIONS.md; the text is in the round-2 report.

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
| `scheme/build_r2.py` | **round 2** panels: work ledger (strict write events, confirmed flag), attention, 30-min bins, presence, rooms, addressing graph, scramble catalog → `data/processed/H01-emergent-superagents-exist/round2/` |
| `analysis/r2lib.py`, `r2_synthetic.py`, `r2_run.py`, `r2_figures.py`, `r2_period_folders.py`, `confirm_r2.py`, `fix_r1_room_kickoff.py` | **round 2** estimators (individuality, KW kernel/landscape, continuity, event designs; imports H15's `h15lib`), synthetic validation, real-data pipeline (R4–R8, D2.6), figures, period folders, confirmatory script (not run), the #38 correction |
| `figures/r2_summary_obs.pdf`, `r2_synthetic.pdf`, `r2_kw.pdf` | round 2: candidate search and continuity; synthetic validation; KW values and goal-change scramble |
| `goalperiod-subhypotheses/G<NN>/README_round2.md`, `NE34/`, `NE29/`, `NE30/`, `NE24/` | round-2 period cards (README.md verdict lines now show round 2, with round 1 kept on the same line); goal-change and succession tests; confirmatory designs |

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
**Round 2 (2026-10-04)**, scored for the round-2 mapping: candidate units (agents + shared artifacts + channel) with a binary work-ledger macro-state, environment = everything else, KW stored/observed semantic information on a fitted coarse-grained kernel plus natural scrambles; windows = 19 non-holdout units of analysis with a work ledger. 0 = not done or failed, 1 = partial, 2 = passed (`writeup/paper.tex`, "Assessing model faithfulness"). Round 1's scorecard (D3.1.a + D3.2) is kept under its results.
**Rival models:** W_super (group store carries the work), W_ind (individual memory-held plans), W_env (environment-driven); rooms and labs as baseline partitions.
**Locked holdout used for confirmation:** none yet. Planned: `analysis/confirm_r2.py` (NE30 succession, NE24 artifact migration, allocation continuity and memory-loss continuity in every holdout unit with a work ledger); written and dry-run, not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Units, states, viability candidates and scrambles all come from logged fields (strict write events, attention, rooms, addressing, behavior states, H15's catalogs). Departures from KW are listed (erasures and cuts rather than marginal-preserving scrambles; a binary coarse state). V_G's limits are documented (F9). Not invariant: no write verbs before 2025-10; regime I runs on discrete sessions. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Two-step Chapman–Kolmogorov error 0.04–0.18 per unit. The synthetic shows the kernel bootstrap is anti-conservative under hidden state (A1.4). Within-period stationarity assumed, not tested. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Allocation continuity beats its permutation null with leave-target-day-out membership (15/19 units). No candidate beats activity-matched random groups on individuality (crews Stouffer Z +0.06); KW values are null. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The KW signature (positive ΔV, plateau) and group homeostasis (D2.6, R8) are absent. |
| E interventional | predicts the change across a natural experiment | 1 | Goal change (relevance scramble) has the predicted sign (−0.39 ± 0.14, z −2.75) but is bundled with a new field; the continuation boundary does not differ. One-member scrambles (NE41, memory loss, departures) and the #focus cut cost nothing measurable. NE24, the only artifact-store scramble, is held out. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Four synthetic worlds at village and #51 sampling. Night continuity and memory-loss continuity are identifiable, and the KW kernel is unbiased when the kernel is Markov. Timing individuality (power ≤ 7%), R7a in V_adv and R8a are not identifiable. |
| G ground truth | agrees with known structure | 1 | Crews recover the known shared builds (#40's 13-writer universe repo; #30/#33 single shared repos). In NE29 the successor joins a predecessor's crew project. Rooms and labs show no special status. |
| H comparative | beats the named rivals | 1 | W_env is rejected (ΔC 0.47 vs ≈ 0). Memory-loss continuity (+0.03) favors artifact-held over memory-held allocation (W_ind predicted −0.29), but n = 17 and #51's private goals can carry it. Single agents out-persist crews, against W_super. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Continuity holds across regimes I–III (15/19 units) and the R4 null everywhere. Holdout not used. |

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

*Added 2026-10-03 after exploratory round 1, before any holdout use:* the operational confirmatory criteria C1–C6 are in [`NE15/README.md`](goalperiod-subhypotheses/NE15/README.md) and machine-readable in `analysis/confirm_d32.py` (`PREDICTIONS`).

## Results

### Exploratory round 1 (2026-10-03; non-holdout only, holdout asserted absent in every script)
#### Round 1 faithfulness scorecard (D3.1.a + D3.2; moved here 2026-10-04 when round 2's scorecard replaced it above)
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

**Confirmation.** `analysis/confirm_d32.py` (NE15 cut DiD, pooled TWFE, NE12 placebo, transfer to #45–#47) is written and dry-run on non-holdout stand-ins; it refuses to run on the holdout without `--confirm --i-understand-this-uses-the-locked-holdout`. See [`NE15/`](goalperiod-subhypotheses/NE15/README.md).

### Results by goal period

| Folder | Units | Verdict | One line |
| --- | --- | --- | --- |
| [G08](goalperiod-subhypotheses/G08/README.md) | 8 | descriptive | P4: polarization along ĝ 0.27, same as #21 (not as predicted); βJ₀/n 0.49 |
| [G21](goalperiod-subhypotheses/G21/README.md) | 21 | descriptive | P4 contrast fails (0.27); strong day-to-day co-fluctuation (βJ₀/n 0.86) |
| [G35](goalperiod-subhypotheses/G35/README.md) | 35 | mixed | rooms ordered (−0.07), big within-room excess (+0.22) but slope ≈ 0 and field R² 0.15 |
| [G36](goalperiod-subhypotheses/G36/README.md) | 36a, 36b | failed | secondary: no room order (ΔH > 0) |
| [G37](goalperiod-subhypotheses/G37/README.md) | 37 | failed | secondary: weak order, no room excess, cross-room co-fluctuation as large as within |
| [G38](goalperiod-subhypotheses/G38/README.md) | 38a–c | mixed | strongest room order (−0.34 to −0.38) with rooms given different goals (room field); slopes mixed |
| [G39](goalperiod-subhypotheses/G39/README.md) | 39 | mixed | weak room order, strong lab order (−0.25); pre-window of the merge |
| [G40](goalperiod-subhypotheses/G40/README.md) | 40 | supported (P7) | merge DiD +0.18 (perm p = 0.004), confounded with the goal change |
| [G41](goalperiod-subhypotheses/G41/README.md) | 41 | mixed | most coupling-like week: order −0.19, slope +0.08, within +0.16, ρ_within 0.47 vs 0.04 |
| [G42](goalperiod-subhypotheses/G42/README.md) | 42 | mixed | field-dominated: goal-only R² 0.54, little room effect |
| [G44](goalperiod-subhypotheses/G44/README.md) | 44 | mixed | rooms ordered (−0.11) and within +0.24, but per-room goal override |
| [G51](goalperiod-subhypotheses/G51/README.md) | 51a–e | mixed | small positive slopes in the big single room; #focus ordered (−0.07) |
| [G12](goalperiod-subhypotheses/G12/README.md) | 12a | failed (native, 1b) | drafted debate teams are not content units beyond a re-partition null (both models) |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | 39, 40, 41 | supported (native, 1b) | the #39 partition loses its order in the merged week and regains it at the split (both models) |
| [NE32](goalperiod-subhypotheses/NE32/README.md) | 51b | n/a | triplet wrote nothing while isolated |
| [NE15](goalperiod-subhypotheses/NE15/README.md) | holdout | pending | confirmatory test (not run) |

P9 for the remaining 26 non-holdout units (regime I and #33) is in `figures/p9_meanfield.pdf` and `data/processed/H01-emergent-superagents-exist/G##/results.json`; those periods have no period-specific prediction beyond P9 and get no folder.

### Round 1b (improved data, 2026-10-04): D3.1.a / D3.2 re-run
*A re-evaluation of round 1 only. Round 2 (below) used no embeddings and is untouched. P1–P9 and the verdict rules are unchanged. The two native tests (G12, NE42) had their predictions written in their folders at 07:45 UTC, before they were run.*

**What changed.**
- **Goal fields:** the shared goal table (`embeddings/goals.parquet` + `goal_vectors[_gte_modernbert].npy`).
  - Per-room kickoffs agree with H01's own vectors at cos ≥ 0.9999 in every unit except #38, where the two room rows were swapped (cos 0.861 = the two rooms' mutual similarity; 30° per room field).
  - **H01's ĝ moves by < 0.02° in every unit.** The 15–56° kickoff-span differences reported by H32 are not differences in these raw vectors. They must come from a different span or whitening construction (flagged for `infra/README.md`).
- **Two embedding models:** bge-small and gte-modernbert (DQ5), each with H01's own per-regime whitening and k = 40 rulers. The bge path reproduces round 1 bit for bit.
- **Restatements removed:** chat statements carrying the model's own DQ5 self-repeat flag (bge 15,842 / gte 15,677 of 128k chat). A copies-only variant uses `self_repeat_both` (12,596).
- **Style-residualized variant:** `style_resid_period` statement vectors, for the identity claims (P2 labs; P1 rooms vs style).
- **Ledger exposure variant for P6:** messages that entered a call's context, from the DQ1 context ledger.
- **Code and outputs:** `scheme/build_r1b.py`; `analysis/explore.py --r1b TAG` (the old path is unchanged); `analysis/r1b_compare.py`, `r1b_native.py`, `r1b_period_folders.py`, `r1b_estimates.py`. Outputs in `data/processed/H01-emergent-superagents-exist/r1b/<instrument>/`; side by side in `r1b/compare.json`.

**Old vs new (round-1 primary statistics; 1b = shared goals + restatements removed).**

| Statistic (criterion) | Round 1 | 1b bge | 1b gte | bge style-resid | gte style-resid |
| --- | --- | --- | --- | --- | --- |
| P1 rooms vs random: median ΔH (≤ −0.1) · days < 0 · units meeting both | −0.098 · 96% · 5/9 | −0.099 · 96% · 5/9 | **−0.136 · 100% · 6/9** | −0.063 · 93% · 3/9 | −0.092 · 93% · 6/9 |
| P2 labs: median ΔH · lab shrink (≥ 0.5) · room shrink (< 0.5) | −0.073 · 0.13 · 0.33 | −0.064 · 0.18 · 0.23 | −0.106 · **0.65** · 0.38 | **−0.022** · – · – | **−0.026** · – · – |
| P3 room JSD below null q05 (≥ 60%) · goal-change jump (across vs within) | 14% · 0.62 vs 0.37 | 14% · 0.62 vs 0.37 | 15% · 0.66 vs 0.35 | 12% · 0.64 vs 0.38 | 12% · 0.67 vs 0.34 |
| P4 #8 vs #21 polarization along ĝ | 0.267 vs 0.268 | 0.267 vs 0.303 | 0.311 vs 0.315 | – | – |
| P5 units with R² ≥ 0.6 · median R² (rotation null) | 12/16 · 0.76 (0.75) | 12/16 · 0.76 (0.74) | 13/16 · 0.77 (0.80) | 11/16 · 0.65 (0.69) | 10/16 · 0.69 (0.74) |
| P6 RE exposure slope ± SE (p; p < 0.01 needed) · units > 0 | +0.013 ± 0.006 (0.019) · 12/15 | **+0.013 ± 0.004 (0.003)** · 11/15 | +0.015 ± 0.007 (0.038) · 12/15 | +0.010 (0.024) | +0.007 (0.20) |
| P6 rotation / day-shuffle null p · I² | 0.005 / 0.025 · 0.32 | 0.005 / 0.010 · 0.15 | 0.005 / 0.005 · 0.53 | 0.005 / 0.045 | 0.010 / 0.040 |
| P6 within − cross > 0 (two-room units) · agent-perm p < 0.05 | 12/12 · 8 | 12/12 · 8 | 12/12 · 7 | 11/12 · 7 | 10/12 · 7 |
| P7 merge DiD (perm p) | +0.18 (0.004) | +0.17 (0.002) | +0.10 (0.030) | **+0.06 (0.09)** | **+0.01 (0.44)** |
| P9 median βJ₀/n (≥ 0.5 in) | 0.74 (34/41) | 0.75 (35/41) | 0.76 (38/41) | – | – |

Further variants:
- **Goal vectors only** (bge, no dedupe): identical to round 1 except the #38 room-field variant of within − cross. Corrected: 38a +0.319, 38b +0.157, 38c +0.106 (bge restate) against the swapped +0.332 / +0.091 / +0.102. Removing room fields still moves the excess by < 0.03.
- **Copies-only dedupe:** P6 p 0.011 (bge) / 0.030 (gte).
- **Ledger exposure:** P6 +0.011, p 0.014; P7 +0.17.
- Per-unit values are in the G folders.

**Which verdicts change.**
- **P1, "not met" → model-dependent.** gte meets both criteria (−0.136, 6/9 units). bge stays 0.002 short. The direction is unanimous.
  - Statement-level clusters are model-dependent (DQ5: 10-NN overlap 0.26), so neither model is privileged.
  - After style residualization room order shrinks (−0.06 / −0.09) but stays negative on 93% of days.
- **P2 (lab order is style), failed → supported in substance.**
  - With gte, removing the first-day agent field shrinks lab order by 65% and room order by 38%: the criterion is met.
  - In both models, DQ5's period-wise style residualization removes most of the lab (family) order (median −0.022 / −0.026 vs −0.064 / −0.106), while rooms keep most of theirs.
  - Agrees with H13 and DQ5: family "order" in content is writing style.
- **P6, not met → met in one instrument only.** bge with restatements removed gives p 0.003; P6's three criteria (slope, both directions, room) pass. It is not met with gte (p 0.038), copies-only (0.011) or style-residualized vectors (0.02 / 0.20).
  - The coupling residual is a stable +0.01 to +0.015 residual cosine per e-fold of exposure in every instrument, beating rotation and day-shuffle nulls everywhere.
  - Its p < 0.01 criterion is instrument-sensitive: **not robust**.
- **P7 (merge DiD) weakens with gte (+0.10, p 0.03) and disappears after style residualization (+0.01 to +0.06).**
  - Part of the round-1 merge effect is agents' writing style converging when rooms merge.
  - Caveat: the residualization is fit per goal period, so #39 and #40 are residualized separately.
- **P3, P4, P5, P9 unchanged.** P9 stays an uninformative upper bound (H26).

**Native tests (Role: native).**

| Test | Prediction | Outcome (bge / gte) | Verdict (1b) |
| --- | --- | --- | --- |
| [G12](goalperiod-subhypotheses/G12/README.md): #12 drafted teams as known units (10 debates, re-drafted sides) | team excess T > 0 at p < 0.05 in ≥ 3/4 instruments [0.5]; ≥ 6/10 debates > 0 (style bge) [0.55] | T = +0.043 / +0.027 (p 0.13 / 0.16); style-resid +0.037 / +0.023 (p 0.07 / 0.10); 5–7/10 debates > 0 | failed: no team unit beyond the re-partition null |
| [NE42](goalperiod-subhypotheses/NE42/README.md): #39 partition across merge and split | the old partition loses order in #40 and regains it in #41 (ΔH [0.65], within − cross [0.6]) | ΔH −0.036 → +0.010 → −0.205 / −0.078 → −0.019 → −0.266; within − cross +0.11 → −0.03 → +0.22 / +0.08 → −0.05 → +0.25 (perm p 0.01 → 0.7 → 0.0005) | supported (both models; goal-confounded; not blind, H47 seen) |

**Scorecard (round-1 mapping) after 1b.**
- A 1: two models, style-residualized; agent field still unstable.
- B 1, C 1, D 1.
- E 1, strengthened: NE42's A-B-A passes in both models, but it is goal-confounded and not blind.
- F 1: P1 direction, P6 sign and P9 are robust; P1 size, P2, P6's p and P7 are instrument-dependent.
- G 1: rooms recovered; known #12 teams not.
- H 0, I 1.

**Reading.**
- Rooms are content units in both models and after style removal, and the NE42 A-B-A shows that room order follows the channel.
- Labs are not units: their order is style.
- Drafted teams inside one room are not units.
- The coupling residual is small, consistent and only marginally significant.

This supports round 2's conclusion that grouping adds no detectable agency beyond the room channel, with the room as the only grouping that orders content.


## Notes
- **Erratum (coordinator, 2026-10-04): Krakauer labels swapped.** `literature/krakauer-2020-information-theory-of-individuality.md` shows that I(x′;x) is *organismal* A* and I(x′;x|y) is *colonial* A. This card puts the star on I(x′;x|y) and calls it organismal. The formulas and tests are correct, and the tests used self-prediction beyond the environment, which is colonial A; read every "organismal" result here as colonial. ι = A/H(x′) and the z-scores are project choices, not from the paper. Gap: y omits the scheduler, kickoff and prior fields, so colonial A may still contain field-driven persistence.
- **From H32 (2026-10-04):** H01's kickoff field spans differ from the shared `goal_fields` spans by 15–56° (principal angle) in #36, #37, #39, #40 and #42, beyond the #38 swap. Recheck the round-1 room-field results on the shared vectors in the re-evaluation.
- **2026-10-04, round 2 done** (exploratory, non-holdout; local, ≤ 2 threads). Order: formal setup and dated predictions, then synthetic validation (four worlds), then Amendment A1, then real data (R4 first, then R4d, R5, D2.6, R6–R8), then A2 (deduplication), then period folders and the confirmatory script (dry-run only). At Vivian's request (relayed by the coordinator), candidates were identified by coordinated behavior (artifact crews, behavior-state synchrony, co-allocation, reply structure), with rooms and labs as baselines only. A coordination-first search is left to H58. The session stalled once during an API outage. All outputs were checked on disk; only the unfinished steps were rerun.
- **2026-10-04, from H26 (P9's βJ₀/n = 0.74 is drive-confounded).** H26 ran round 1's whole-swarm day-mean fluctuation estimator on two-room synthetic worlds at village sampling. With zero coupling it returns 0.57 from a global drive at the observed cross-room level, 0.67–0.74 when room drives, kickoff relaxation, time of day or operator pulses are added, and 0.83 for a single room of 24. With real coupling (J = 0.2–0.6) it rises only to 0.79–0.83. Day averaging also inflates equal-time gains (g_day = J(2 − J)). So drives alone can produce all of round 1's median 0.74: **P9's "failed" verdict (βJ₀ ≥ 0.5 n in 34/41 units) is not evidence of strong content coupling.** Round 1 had already called it an upper bound that conflates room-local drives with coupling; H26 shows the bound is uninformative. The drive-robust replacement is H26's room-excess gain ρ_ex = (ρ_w − ρ_c)/(1 − ρ_c) (`hypotheses/H26-content-near-critical/analysis/h26lib.py`): ≈ 0.53 day-level / 0.43 at 30 min for content. That agrees with round 1's within- vs cross-room co-fluctuation (ρ_within 0.06–0.66 vs ρ_cross ≈ 0), which is the statistic round 1's interpretation actually rested on. **Round 2 does not use the 0.74 or any whole-swarm day-mean alignment.** R4–R8 are built on the work ledger, and the only collective-level statistics are compared against size- and activity-matched random groups and member-shift surrogates.
- **2026-10-04, correction (#38 per-room kickoff vectors were swapped in round 1).** Found by the shared-pipeline consolidation: in H01's `goals_raw.npy` the #38 room-2 (#best) and room-3 (#rest) kickoff vectors were exchanged (each matches the other room's text at cos 1.000 in the shared table `data/processed/shared/embeddings/goals.parquet` + `goal_vectors.npy`; cause: a `--reuse-goal-emb` reload of vectors saved under a different `group_by` order in `scheme/build.py`). All other kickoff rows match at cos ≥ 0.999. **What used them:** only round 1's room-field robustness variant of P6's room criterion (`within_minus_cross_roomfield_removed`, each room's ĝ_r added to the field subspace). The period-level ĝ (P4, P5, P6, P9) averages the room kickoffs and is unchanged by a label swap; P1–P3 use no goal vectors; round 2 uses no embeddings at all. **Old (swapped) → recomputed with corrected vectors** (`analysis/fix_r1_room_kickoff.py`, same five rarefied draws for both, `round2/fix_r1_room_kickoff.json`): 38a +0.332 (reported) / +0.330 (swapped, redrawn) → +0.330 (corrected); 38b +0.091 / +0.094 → +0.091; 38c +0.102 / +0.100 → +0.097; the room-field-free within − cross values are +0.329, +0.076, +0.118 (unchanged). **No conclusion changes:** removing the room field still moves the within-room excess by < 0.02 in every #38 sub-unit (the two rooms' kickoffs are close, cos 0.86, and cross-room pairs get both room fields either way). `analysis/h01data.py` now reads room kickoffs from the shared table (flag `shared_room_kickoffs=False` reproduces the old vectors). The lexical instrument's #38 room labels cannot be checked the same way (its goal rows were re-derived in a fresh `group_by` order and its labels copied from the bge build), so its #38 room-field variant is flagged unverified.
- 2026-10-04: from H13 round 1: **D1.1.b (families as superagents) not supported**: no family homophily in coupling; rooms carry it. **D9.2 holds only as a style field** (family identity persists across rooms as writing style); D9.2′ (room identity dominates) holds for couplings.
- 2026-10-03: **exploratory round 1 of D3.1.a / D3.2 done** (one of several parallel agents; local compute only, ≤ 4 threads). Synthetic validation first, then Amendments 2 and 3, then real data. Holdout asserted absent in the scheme and in every exploratory loader. Folder convention: per-goal-period `G##/` cards and `NE##/` spanning tests (Vivian, 2026-10-03).
- 2026-10-03: `chat_core.mentions` is not used anywhere in H01 (exposure comes from the shared `exposure` table), so the mentions fix does not affect these results.
- 2026-10-03: the shared embedding agent states (`data/processed/shared/embeddings/agent_day*`, `whitening_<regime>.npz`) could replace this scheme's whitening fit but not its products: H01 needs per-statement whitened vectors (rarefaction, split halves, clusters), k-means rulers, goal fields, exposure pairs and holdout-free files. The shared agent-day vector normalizes raw means before whitening; H01 whitens each statement first.
- 2026-10-03: **next steps.** (1) Sign off and run `analysis/confirm_d32.py --confirm …` (NE15, #voted-out, NE12 placebo; transfer to #45–#47). (2) Separate room fields from room coupling: per-room operator/nudge messages as explicit room-day fields in the P6/P9 designs; blind partition recovery from residual alignment. (3) Event-level coupling: reply-conditioned alignment (does i's next message move toward j's last one?) instead of day-level exposure counts. (4) A stable style field: estimate h_i from many periods with topic regressed out, then retry P2/P5. (5) Mean-field forward predictions (kickoff susceptibility, transverse vs longitudinal fluctuations) per D3-MF. (6) A second neural embedding model when the network is available, for the key results.
- 2026-10-03: recorded as an idea.
- 2026-10-03: terminology settled: "semantic entropy" → Kolchinsky–Wolpert semantic information; meaning-cluster entropy kept as the order parameter.
- 2026-10-03: predictions for D3.1.a and D3.2 written (P1–P9). **NE12 is a placebo, not a cut** (per H05): the D3.2 confirmatory test moves to the actual separations (#voted-out, NE15).
- 2026-10-03: **starting set chosen by Vivian: D3.1.a** (ideology order parameter from mined statements) **and D3.2** (coupling- vs. field-driven order). Both need Phase 2 (embeddings / meaning clusters). D3.2's strongest test (NE12) is held out, so exploration uses #8, #21, #41 and the NE32 isolated triplet.
- 2026-10-03: renamed from "Emergent superagents and the thermodynamics of ideology" to **"Emergent superagents exist"**. Sub-hypothesis set (D1–D10) written. No new swarms, so simulation was replaced by natural experiments. `llm_calls` to be requested eventually. Probes: both mined and fixed. Viability left open, with candidates in D2.

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`), rewritten the same day at Vivian's direction: round 1's framing ("is a room like-minded?") was not useful.*

- **Where round 1 went sideways:** it measured whether rooms are more like-minded than random groups (embedding-cluster entropy), which mostly tracks room instructions and topic. It never tested agency.
- **What the direction is really after:** **effective superagents in Kolchinsky–Wolpert terms, running on a substrate of agents.**
  - An *agent* is a system that uses semantic information about its environment to maintain its own viability.
  - Information is *semantic* when scrambling it (an intervention on the system–environment correlations) lowers viability over a horizon τ. The *viability value* is ΔV; the *amount* of semantic information is S (the least retained mutual information that keeps the same viability); the *efficiency* is η = S/I.
  - A superagent is a coarse-grained unit of the swarm that is an agent in this sense. It is *effective* when its semantic information lives at the group level and is not reducible to its members'.
  - H15 sets the substrate baseline: individual agents' memories carry ≈ 0 semantic information at day scale (η_mem ≈ 0), while their context windows carry a lot at turn scale. If a group-level unit (agents plus shared artifact plus channel) carries day-scale semantic information that no member does, agency has moved up a level.
- **Formal setup.**
  - *System X:* a candidate unit G: a set of agents with their shared artifacts (repos, documents) and their channel (room, threads).
  - *Environment Y:* everything else: other agents, humans, the operator and goal prompt, the web.
  - *Viability V_G:* chosen by the D2.6 homeostasis rule, from group-level candidates: continued advancement of the unit's artifact (the work ledger), persistence of its plan or identity as a cluster, or recovery after shocks.
  - *Interventions:* only natural scrambles exist (no replay): room cuts (NE15), merges (NE42), goal changes (scramble relevance), outages (cut every channel), member turnover (NE27, NE33; NE30 held out), member memory losses and context erasures (NE41), artifact migrations.
- **H01-R1, R2, R3** (superseded by R4–R8; kept for the record): causal emergence of room macro-states; the artifact as the superagent's body; organ-like role specialization.
- **H01-R4. Individuality maxima pick out candidate superagents.** Search over coarse-grainings (rooms, project-centered groups of agents plus repo, families, reply-graph communities) for local maxima of information-theoretic individuality: how much of a unit's future is predicted by its own past rather than by the environment (the organismal vs environmental decomposition of Krakauer, Bertschinger, Olbrich, Flack & Ay 2020†). Prediction: maxima sit at artifact-centered units, not rooms or model families.
- **H01-R5. Superagents have positive group-level semantic information.** For the candidates from R4, natural scrambles of the unit–environment information lower V_G: ΔV_G > 0 at horizons of 1–3 days. Estimate the viability value, S and η for the unit.
- **H01-R6. The agency is effective: it lives above the substrate.** Scrambling one member (memory loss, context erasure, leaving) costs the unit little; scrambling the unit's own channels or artifact costs a lot. Formally, the unit's semantic information exceeds the sum of its members' (group-level synergy in ΔV). With H15's η_mem ≈ 0, this would be exactly an agent running on a substrate of agents whose own day-scale semantic information is negligible.
- **H01-R7. Substrate independence.** The superagent's identity, viability and stored semantic information survive replacement of its members (roster turnover inside a unit). The unit dissolves when its artifact or channel is scrambled, not when its members are swapped: the agent is the pattern, not the parts.
- **H01-R8. The superagent does self-maintenance.** Units repair themselves (broken builds, operator resets, lost members) faster than their members do alone, with a measurable homeostatic response time (D2.6 at the group level). That repair is the superagent using its semantic information to stay viable.
- **Needs:** the work-output ledger (V_G as artifact advancement), the context ledger (who saw what), and the shared outage and period-unit tables. Literature to verify (†): Kolchinsky & Wolpert 2018 (notes in `literature/`); Krakauer et al., "The information theory of individuality", *Theory Biosci.* 2020; Bertschinger et al. 2008, information-theoretic autonomy.

- **Egregore revamp (coordinator, 2026-10-04):** the null for coordination-defined superagents moves the search to the stigmergic layer and to culture. See HH290–HH306 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Egregores and collective information dynamics"), especially HH293 (culture beyond composition), HH290 (remanence), HH296 (autonomy across scales with the round-1b impostors as environment) and HH301 (repos recruit hosts).

## Round 2 formal setup (2026-10-04)
*Written before any R4–R8 statistic was computed on real data. What I had seen (scheme-level counts only, no outcome of any test below): strict write events per non-holdout goal period (#30 onward has a work ledger; #39 and #42 are own-artifact weeks with crews of ≤ 2, #40 one 13-writer crew, #51 has 295 written projects); that `artifact_commands_text.error` is "stderr non-empty", not failure (git push sets it 65% of the time), so failed writes cannot be read from it; that a regime-III forced consolidation recurs every ~14 active minutes per agent (median gap; H15's catalog); the counts of H38 platform stalls (village-off: 1 in #37, 1 in #38, 8 in #51; infra-burst joint silences ~670); rooms and their dates. Code: `analysis/r2lib.py` (estimators), `analysis/r2_synthetic.py` (axis F), `scheme/build_r2.py` (panels), `analysis/r2_run.py` (R4–R8), `analysis/confirm_r2.py` (holdout; not run). Data: `data/processed/H01-emergent-superagents-exist/round2/`.*

**F0. What is being claimed, in Kolchinsky–Wolpert (KW) terms.** A system X with environment Y, a joint p(x₀, y₀), dynamics over a horizon τ, a viability function V of X's state at τ. Stored semantic information is read off interventions on the *correlation* I(X₀;Y₀) that keep the marginals (the coarse-graining p̂ᶠ(x₀, y₀) = p(y₀) p(x₀ | f(y₀)); full scramble p(x₀)p(y₀)): the value ΔV = V[p] − V[p̂^full], the amount S = the least I(p̂ᶠ) over interventions that keep the actual viability, the efficiency η = S/I. Observed semantic information intervenes on the flow instead, replacing p(x_{t+1} | x_t, y_t) by p(x_{t+1} | x_t) so that X no longer reads Y beyond what it already holds (KW Sec. 5; this zeroes the transfer entropy). A unit is an **agent** if it has positive semantic information for its own viability; an **effective superagent** if, in addition, that information is carried by group-level components (shared artifact, channel, the joint configuration of members) rather than by any member's own store. The substrate baseline is H15: a member's long-term memory carries ΔV ≈ 0 at τ = 1–3 days, its context window carries a lot at ~10 turns and is erased every ~14 active minutes.

**F1. Time base and periods.** Active 30-min bins of each day's empirical window (`calendar.win_start` → `win_end`; variants 15 and 60 min); transitions only within a day (the night is treated as an intervention, F5). Units of analysis: round 1's units (goal periods split at catalogued step changes) that are non-holdout, have ≥ 2 days, ≥ 100 strict write events and ≥ 4 write-active agents: expected #30, #31, #33, #35, #36b, #37, #38a–c, #39, #40, #41, #42, #44, #51a–e. Exceptions used: (c) transitions (goal boundaries, NE33, NE42) as objects; (d) partial pooling of kernel and landscape cells within a regime.

**F2. Primitives (work ledger proxy, documented limits in F9).**
- *Project:* H11's map (repo; file → parent repo; site → parent repo when known, else itself; domains and Google placeholders excluded).
- *Write event:* an `artifact_mentions` row by an agent with verb ∈ {git push, git commit, deploy, gh/glab PR/MR create and merge, repo/project create} (H15's V_out list), `how` ∈ {url, output, bare} (strict), deduplicated to one event per (agent, turn, project). *Confirmed* if the command's git output printed a push range or new-commit hash (`artifact_commands_text.out_hashes`); a push without one is *unconfirmed* (a rejection, an auth failure or a no-op; the export does not say which). Variant: lenient `how` (+ cwd, session_cwd).
- *Attention event:* any strict mention of a project by an agent (H11's state rule), deduplicated per (agent, source, turn or message, project).
- *Room:* `rooms_timeline`, the room at the bin midpoint. *Exogenous input:* a human or automated chat message, or a goal kickoff.

**F3. Candidate units G = (A_G, R_G, C_G).** Members A_G fixed within a unit of analysis; shared artifacts R_G = the projects with ≥ 50% of their period writes by members of A_G and ≥ 3 writes (one rule for every coarse-graining, so the coarse-grainings differ only in how members are chosen); channel C_G = the rooms the members occupy. Coarse-grainings searched:
- **K_sub** (the substrate): singletons {i}.
- **K_crew** (artifact-centered): for each project with ≥ 2 writers and ≥ 10 writes, A = its writers with ≥ 2 writes on it; identical member sets merged.
- **K_room:** agents by time-weighted modal room (units with ≥ 2 rooms of ≥ 2 members).
- **K_lab:** agents by lab (≥ 2 members).
- **K_comm:** communities of the period's addressing graph (`chat_mentions_clean`, agent → agent mentions, symmetrized), by greedy modularity; ≥ 2 members.
- **K_vil:** all write-active agents.
- Nulls: random member sets of the same size and similar activity (total writes within ±50%), with R recomputed by the same rule; member-shift surrogates (F7a).

**F4. States.**
- Unit macro-state x_G(b) = 1 if ≥ 1 write event by a member on R_G in bin b. Member micro-state s_i(b) = 1 if member i wrote on R_G (so x_G = OR_i s_i). A fixed binary alphabet for every unit keeps the state space independent of unit size.
- Environment Y: everything not in G: non-member agents and their artifacts, humans and the nudger, the operator and the goal prompt (constant within a period, redrawn at NE34 boundaries), the platform. Members' memories and local workspaces belong to the members (substrate stores). State y_G(b) = (y^w, y^h) ∈ {0,1}²: y^w = 1 if a non-member wrote anything in bin b (the rest of the swarm's work; also a proxy for common drives: time of day, outages, goal phase); y^h = 1 if a human/automated message or a kickoff fell in bin b.

**F5. Viability V_G and the D2.6 rule.**

| code | class | definition (bin b; day d = mean over the day's bins) |
| --- | --- | --- |
| V_adv | functional (D2.3.a), the work-ledger proxy | x_G(b) |
| V_mem | structural (D2.1.a) | fraction of A_G writing on R_G |
| V_foc | identity / plan (D2.2.b) | share of members' attention events that are on R_G |
| V_ord | informational order (KW's −S) | −(Miller–Madow entropy) of members' attention over projects |
| V_rel | reliability | confirmed share of members' push events on R_G |

D2.6 at the group level (regime I/II pooled, regime III separately): shocks = H38 platform stalls (`outages.parquet`, village-off or infra-burst runs, not at a day edge), non-holdout; units with ≥ 2 members and ≥ 20 writes; 10-min sub-bins; D₀ = V(first 10 min after the stall) − mean V(20 min before it), D₃ = V(30–40 min after) − the same mean; δ = median|D₀|, R = 1 − median|D₃|/median|D₀|; placebo = 200 draws of pseudo-stalls of the same durations at random times ≥ 30 min from any stall. Homeostatic iff δ > placebo p95, R > placebo p95 and R ≥ 0.5; V* = the homeostatic candidate with the largest R − median(R_placebo). If none passes, D2.6 is **inconclusive** and V_adv (the work-ledger proxy) is primary; all candidates are reported (D4.4).

**F6. Interventions (natural scrambles) and what each scrambles.** None is KW's marginal-preserving scramble; each is an erasure, cut or redraw, at a time the operators or the scaffold chose.

| intervention | what it scrambles | level | non-holdout availability |
| --- | --- | --- | --- |
| night (village off; every member's context erased; memory, workspace, repos and chat history kept) | all members' session stores | substrate-wide | every day boundary |
| NE41 forced consolidation of member i (41-turn cap, exogenous timing) | member i's session store | one member | ~18.6k events (regime III) |
| memory loss / glitch / newcomer (H15 catalog: ML, MG, MN) | member i's long-term store | one member | 16 / 22 / 20 events, mostly #51 |
| member departure (stops writing R_G) or arrival | one member removed or added | one member | endogenous; many |
| NE32, NE33 batch joins | members added with empty stores | members | #51b, #51e (2 days before the #51 tail) |
| platform stall (H38 village-off, infra burst) | every channel and member, briefly | unit-wide, common to all units | 10 village-off, ~670 infra-burst runs |
| room cut or merge (#focus 08-05; NE42 merge 05-04 / split 05-11) | the unit's channel | unit channel | 3 events; NE42 is goal-confounded |
| goal change (NE34) | the environment state is redrawn independently of the unit's stored state: a full scramble of the unit–goal correlation (marginals change too) | unit–environment | 9 non-holdout boundaries; only #39 → #40 keeps the artifacts relevant (dose) |
| artifact migration (NE24 GitHub → GitLab) | the unit's artifact store | unit store | **holdout only** |

**F7. Estimators.**
- **(a) Individuality (R4).** Following the organismal / environmental decomposition of Krakauer, Bertschinger, Olbrich, Flack & Ay (2020†) and the autonomy measure of Bertschinger, Olbrich, Ay & Jost (2008†): over within-day transitions, the predictive information P_G = I(x_{b+1}; x_b, y_b) = A*_G + I(x_{b+1}; y_b), with **A*_G = I(x_{b+1}; x_b | y_b)** (self-determined: the unit's past predicts its future beyond the environment) and E_G = I(x_{b+1}; y_b | x_b) (environment-determined; the transfer entropy Y → X). Individuality index **ι_G = A*_G / H(x_{b+1})**. Plug-in, bits, Miller–Madow corrected. *Composition excess* z_G = (ι_G − μ)/σ over 300 random activity-matched groups of the same size (group-size bias: the whole village trivially maximizes raw ι; the excess removes it). *Local maximum:* z_G ≥ z_{G′} for every one-member addition or removal G′ (null moments by size and activity decile). *Substrate (coordination) excess:* ι_G minus its mean over 200 member-shift surrogates (each member's s_i series rotated within each day by an independent random offset; x recomputed; y kept): the individuality that comes from how members' activity is arranged in time relative to each other, not from each member's own persistence. Aggregation is not agency: an OR of independent members is smoother than any member, which this surrogate reproduces.
- **(b) KW stored and observed semantic information (R5), model-based, observational.** Per coarse-graining and period: fit the Markov kernel on the 8-state chain z_b = (x_b, y_b) from pooled within-day transitions of its units, factorized K(x′, y′ | x, y) = K_x(x′ | x, y) K_y(y′ | y, x), Dirichlet(½) smoothing, partially pooled toward the regime kernel (pseudo-count 8). Start-of-horizon distribution p₀ = empirical (x_b, y_b) over bins with ≥ τ bins left in the day. V(p₀) = (1/τ) Σ_{h=1..τ} P(x_{b+h} = 1), τ = 4 bins (2 h) primary; rest-of-day and a day-level variant (x₀ = unit-day above its period median, y₀ = environment-day above median, V = V_adv(d+1); only where ≥ 30 unit-day transitions). Stored: **ΔV_st = V(p₀) − V(p₀^X ⊗ p₀^Y)**; the information–viability curve over all 15 partitions f of the y alphabet; **S_st** = min I(p̂ᶠ) over f with V(p̂ᶠ) − V(full scramble) ≥ 0.9 ΔV_st; **η = S_st / I(X₀;Y₀)**; κ = ΔV/I; Pinsker envelope |ΔV| ≤ √(I_nats/2). Observed: **ΔV_obs** = V under K_x minus V under K̂_x(x′ | x, y) = Σ_{y″} p_t(y″ | x) K_x(x′ | x, y″) at every step; TE_{Y→X} = E_G. Identity used as a check: under full scrambling ΔV_st = E_p[(1 − e^{−PMI}) v], so ΔV_st ≠ 0 only if the viability landscape v(x₀, y₀) has an x₀ × y₀ interaction (the unit's state must *match* the environment's for the correlation to matter). Uncertainty: unit-day cluster bootstrap (200). Positivity: the share of the scrambled mass on (x₀, y₀) cells with < 5 transitions is reported. Markov check: two-step Chapman–Kolmogorov error. This is observational KW: it is exactly as good as the coarse-grained kernel, including off-support cells.
- **(c) Natural-scramble estimators (R5–R8).** Unit-day panels with same-day differencing across units (removes the shared field), H15's `kal` counterfactual and unit-pooled placebo pools (`h15lib.event_delta`, `unit_placebo_pool`, `period_test`), DerSimonian–Laird across periods (`h15lib.dl_meta`). Imported from H15, not copied.
- **(d) Synergy contrast (R6).** One-member scrambles: after member i's forced consolidation at t, the change in (i) i's own writes on R_G, (ii) the other members' writes on R_G (spillover), (iii) the unit's advancement, in [t, t + 15 min] against matched placebo times of the same member (mid-segment times with no consolidation of any member within ±15 min). *Buffering ratio* β = ΔV_G(unit) / (π_i ΔV_i), π_i = i's share of the unit's writes: β ≈ 1 additive substrate, β < 1 the others absorb the loss (redundant, homeostatic), β > 1 i is a hub. *All-member scramble (night):* crew continuity C = the fraction of members who wrote on R_G on day d and are active on d + 1 that write on R_G again on d + 1, against a null that permutes the day-(d+1) project sets among the agents active on both days (keeps crew sizes and agents' number of projects); ΔC = C − C_null. *Memory-loss continuity:* the same, for agents with an ML/MG/MN event, against their own non-event days. *Unit-level scrambles:* goal changes, channel cuts, stalls (F6). Effective if one-member costs are small (β ≤ 1, no spillover), the night preserves the unit (ΔC > 0, also after memory loss), and unit-level scrambles cost far more than the sum of one-member scrambles.
- **(e) Substrate independence (R7).** Departure: a member with ≥ 20% of the unit's writes over the previous 2 active days that writes nothing on R_G for the next ≥ 2 active days. ΔV_G over those 2 days by `kal` against unit-pooled placebo days; compared with −π_i. Death: no write on R_G for the rest of the period. Hazard of death within 2 days after a departure vs placebo days; probability that R_G gets any write in days 1–2 of the next period, at new-goal vs continuation boundaries. Ship of Theseus: for crews alive ≥ 6 active days, Jaccard(members writing in the first third of its life, members in the last third) and the trend of V_adv.
- **(f) Self-maintenance (R8).** (i) Response to an unconfirmed push of member i on R_G: hazard ratio of a confirmed write on R_G *by another member* within 30 min after it, relative to the same window after i's confirmed pushes. (ii) Compensation after i's forced consolidation: the other members' write rate in [t, t + 15 min] relative to placebo (from (d)). (iii) Stall recovery: units' V* recovery after platform stalls against the member-shift surrogate (the aggregation baseline), from the D2.6 machinery. A homeostatic response time is the e-folding time of the recovery profile.

**F8. Rival worlds (named, used in the synthetic validation and as interpretations).**
- **W_super:** members with negligible individual memory, coupled through a shared artifact and channel; the artifact holds the state that keeps the unit's work going and the unit senses the environment through its channel. Predicts R4 crew maxima, ΔV_st > 0, one-member scrambles cheap, continuity across nights and memory loss, survival of turnover.
- **W_ind (purely individual agency):** each agent keeps its own plan (persistent personal state) and works independently on whatever project it picked; projects have writers but no shared state. Predicts crew individuality at the random-group level, zero coordination excess, continuity broken by memory loss, β ≈ 1, departures cost exactly their share.
- **W_env (purely environment-driven):** agents carry no state; each bin they work with a probability set by an exogenous field and pick projects by goal-set popularity. Predicts A* ≈ 0 given y, E large, ΔC ≈ 0.

**F9. Limits of the V_G proxy (stated before use).** Write events count *attempts* (a push can be rejected or a no-op; only confirmed pushes are certain); they are not value (a one-line fix and a feature weigh the same); deploys and merges have no confirmation signal; repo resolution through the working directory is excluded in the strict rule (≈ 16% of write mentions; lenient variant reported); work that never touches git (documents, outreach, forms, videos in #42) is invisible; regime I before 2025-10 has essentially no write verbs. Agent narration is not used. The shared work-output ledger would replace this.

## Round 2 predictions (dated 2026-10-04, written before any real-data run of R4–R8)
*Operational criteria are fixed here; the synthetic validation (axis F) may add a dated amendment before real data, as in round 1. My priors are stated separately from the card's predictions.*

| | Card's prediction (operational) | Falsified if | My prior |
| --- | --- | --- | --- |
| **R4** individuality maxima | (a) In ≥ 2/3 of eligible units of analysis with ≥ 2 crews and ≥ 2 units of a rival coarse-graining, the median composition excess z of K_crew is higher than that of K_room, K_lab and K_comm (each where defined). (b) Pooled, ≥ 50% of crews are local maxima, more than for rooms, labs and communities. (c) Crews' composition excess is > 0: Stouffer-combined over units of analysis p < 0.01. | K_room or K_lab has the highest median z in ≥ 1/2 of units of analysis; or crews' median z ≤ 0 in ≥ 1/2 | (c) passes, small; (a) passes against rooms and labs but not reliably against communities; (b) fails (one-member changes barely move ι at this sampling) |
| **R5** group semantic information | (a) For crews (and any other coarse-graining R4 selects), ΔV_st > 0 with bootstrap 95% CI above 0 in ≥ 1/2 of eligible units, and ΔV_st(crew) > ΔV_st(singleton) in ≥ 2/3. (b) ΔV_obs > 0 (CI above 0) in ≥ 1/2. (c) Goal change as a full scramble of the unit–goal correlation: units' V_adv on days 1–2 of the next period is below their last 2 days (meta z ≤ −2), less so at the continuation boundary #39 → #40. (d) Channel cuts and stalls lower V_G (pooled ΔV ≤ −0.25 SD, z ≤ −2). | (a) CI includes 0 in > 1/2 of units, or ΔV_st(crew) ≤ ΔV_st(singleton) in ≥ 1/2; (c) meta z > −2 | (a)/(b) fail: \|ΔV\| < 0.02 with CIs on 0, because a binary activity environment gives little for the unit's state to match; Pinsker caps it anyway. (c) passes strongly, but it measures dependence on the operator's field (environmental determination), not autonomy. (d) underpowered. |
| **R6** effective agency | (a) One-member scramble is cheap: after a member's forced consolidation, other members' writes on R_G are within ±10% of placebo and β ≤ 1 (pooled CI). (b) The night (all members' session stores erased) preserves crews: ΔC ≥ 0.2 in ≥ 2/3 of eligible units. (c) Continuity survives memory loss: pooled difference vs the agent's non-event days > −0.2. (d) Crews' substrate (coordination) excess > 0 in ≥ 2/3 of units. (e) \|ΔV_G\| for unit-level scrambles (R5c/d) exceeds the summed one-member costs. | (a) spillover < −10% with CI below; (b) ΔC < 0.2 in ≥ 1/2; (d) excess ≤ 0 in ≥ 1/2 | (a) holds (β ≈ 1, no spillover: members don't notice each other's erasures at 15 min); (b) holds (ΔC large); (c) holds but n is tiny and #51's private goals can carry it; (d) fails or is small; (e) holds only because goal changes are huge |
| **R7** substrate independence | (a) After a departure, ΔV_G ≥ −π_i (pooled) and the death hazard within 2 days is inside the placebo 95% band. (b) Crews alive ≥ 6 active days turn over (median Jaccard first vs last third < 0.5) without a downward V_adv trend. (c) Deaths follow environment scrambles, not member swaps: P(R_G written in days 1–2 of the next period) ≥ 0.5 at the continuation boundary and ≤ 0.2 at new-goal boundaries, while the post-departure death hazard is not above placebo. | (a) ΔV_G < −π_i with CI below, or hazard above the band | (a) holds; (b) holds in #51 (long-lived infrastructure repos), few crews elsewhere; (c) holds |
| **R8** self-maintenance | (a) Another member's confirmed write on R_G is ≥ 1.2× more likely within 30 min after a member's unconfirmed push than after its confirmed push, in ≥ 2/3 of units with ≥ 10 unconfirmed crew pushes. (b) Others compensate after a member's forced consolidation (their write rate rises vs placebo). (c) Units recover V* after stalls faster than the member-shift baseline. D2.6: a homeostatic V exists at the group level. | (a) ratio ≤ 1 in ≥ 1/2; (b) compensation ≤ 0; (c) no faster than baseline | (a) fails or is untestable (unconfirmed ≠ failed); (b) fails; (c) fails; D2.6 inconclusive |

**Overall prior (2026-10-04).** The village has artifact-centered units that persist through members' memory loss and every night's context erasure, so the information that keeps them going lives outside the members (repos, chat, the prompt). But I expect their viability to be overwhelmingly set by the operator's goal (environmentally determined, in Krakauer et al.'s sense), with no detectable KW semantic information about anything else and no group-level repair beyond aggregation. If so, "effective superagent" would be the wrong name: these are **scaffolded collectives**, stigmergic work units held together by artifacts and driven by the prompt.

### Amendment A1 (2026-10-04, after the synthetic validation, before any real-data run of R4–R8)
*What I had seen: only synthetic results (`analysis/r2_synthetic.py`, `round2/synthetic.json`; 30 village-sized and 8 #51-sized replicates per world) and the real scheme's unit and coarse-graining counts (crews per unit 2–31, sizes 2–13). No real-data R4–R8 statistic.*

**Synthetic validation (axis F), the headline.** Four worlds. W_super (shared artifact + channel carry the work; no member memory). W_supersync (same, plus channel activation in timing). W_ind (personal plans in memory). W_env (exogenous drive, popularity choice).

| test | W_super | W_supersync | W_ind | W_env | reading |
| --- | --- | --- | --- | --- | --- |
| R4c crews' composition z (median; Stouffer p < 0.01 per replicate) | −0.13 (0%) | −0.18 (7%) | −0.23 (3%) | −0.29 (0%) | **no power**: timing individuality of a binary activity state does not see a group store that sets *which* artifact members work on |
| R4a crews rank first vs decoy rooms/labs | 27% | 38% | 17% | 10% | decoys win ~1/3 by chance; uninformative at village sampling (63% in #51-sized W_super) |
| iota_alloc vs member rotation (Stouffer p < 0.01) | 7% | 23% (40% long) | 3% | 13% (25% long) | weak power for timing coupling, inflated by common drives |
| R5 KW kernel on a known Markov chain (planted ΔV_st 0.014) | mean 0.013, 27% > 2 sd (village); unbiased, 100% (long) | | | additive kernel: 0.000, 1% | the estimator is right when the kernel is Markov |
| R5 ΔV_st in the agent worlds (long-run coarse-grained truth) | ≈ 0 (\|ΔV\| ≤ 0.0005) even with planted sensing | | | | the binary activity state does not carry the planted environmental information; bootstrap CIs exclude 0 in 3–13% (village) and up to 37–50% (W_env long) of null replicates → **anti-conservative under hidden state** |
| R6a self dip after a member's forced erasure | −50%, detected 100% | −58% | −50% | −44% | validated |
| R6a spillover to others (rotation null, p < 0.05) | 0% | 7% | 13% | **27%** | effect ≈ 0 everywhere; the rotation null is anti-conservative under common drives |
| **R6b night continuity ΔC (≥ 0.2)** | 0.45 (97%) | 0.39 (93%) | 0.55 (100%) | 0.01 (0%) | **separates stateful worlds from the environment-driven one** |
| **R6c continuity after memory loss (event − base)** | −0.02 | 0.00 | **−0.29** (−0.19 long) | +0.01 | **separates artifact-held from memory-held allocation** (n ≈ 70–110 events) |
| R7a departure, V_adv relative to −share | +0.03 | +0.08 | +0.10 | +0.06 | uninformative in V_adv (an OR loses less than the write share); use writes per bin (V_cnt), whose independence expectation is exactly −share |
| R8a others' attempts after unconfirmed / confirmed push (planted repair ×4 in W_super) | 0.98 | 1.00 | 0.97 | 0.99 | **not identifiable**; the confirmed-write version is 0.13–0.24 in every world (common platform state) |

**Consequences (fixed now).**
- **A1.1 R4 (timing individuality)** is run and scored exactly as pre-registered. If it fails, the verdict is "not identifiable at village sampling", not "refuted"; a pass would be suspect, because the validated power is ≤ 7%.
- **A1.2 Allocation individuality (added, R4d).** For every coarse-graining: night continuity ΔC (F7d), with unit membership and R_G recomputed **leaving out the target day d + 1**, so that a unit is never defined by the writes it is scored on. Prediction R4d: ΔC of the artifact- and coordination-based coarse-grainings (crews, co-allocation communities) exceeds that of rooms and labs in ≥ 2/3 of units where both exist. Prior: passes; it shows that allocation persists in units held together by artifacts, which is necessary for agency but not sufficient. Singletons (the substrate) are reported alongside.
- **A1.3 Coordination-based candidate units (added at Vivian's request, relayed 2026-10-04): superagents are identified by coordinated behavior; rooms and labs are only baseline partitions.** Two coarse-grainings are added to F3:
  - **K_sync** (behavior-state synchrony): communities, by greedy modularity, of the graph of positive pairwise correlations between agents' 5-min "working" indicators (shared `states_min`, lump4 = work, inside the agent's daily span), after subtracting the cross-agent mean at each 5-min step. This makes the synchrony drive-robust, per H26.
  - **K_coalloc** (co-adoption / joint work): communities of the graph whose weights are the Jaccard overlap of two agents' sets of (project, day) strict writes.

  With K_crew (joint work on one artifact) and K_comm (reply structure), these are the candidate units. A dedicated coordination-first search, combining behavior-state, co-adoption and reply channels, is left to **H58** ("effective superagents are coordinated agents plus their artifacts").
- **A1.4 R5:** ΔV_st and ΔV_obs count as positive only if the CI excludes 0 **and** the value is ≥ 0.005 (the practical floor). Positive values in long units are flagged as possibly non-Markov artifacts (Chapman–Kolmogorov error reported).
- **A1.5 R6a:** a spillover claim needs a Stouffer \|Z\| ≥ 3 across units, and the per-unit rotation p-values are descriptive. The β ratio is reported.
- **A1.6 R7a** is scored on V_cnt (writes per bin on R_G, relative change + departed share; 0 under independence, > 0 if others compensate), with V_adv reported.
- **A1.7 R8a** is run and reported; its verdict is "not identifiable" unless the ratio is ≥ 1.2 in ≥ 2/3 of eligible units.
- **A1.8 Consolidation events are edge-trimmed** for real and rotated times alike (a bug found in the synthetic smoke test: rotated events in a day's first minutes inflated the null).
- **A1.9 Substrate comparator for R5:** each crew member as the system, with x = its writes on the crew's R_G and y = (anyone else wrote, message), pooled per unit. This replaces "all singletons" so that crew and substrate see the same artifacts.

## Round 2 results (2026-10-04; exploratory, non-holdout only)
**Labeled exploratory.** Scheme: `scheme/build_r2.py` → `data/processed/H01-emergent-superagents-exist/round2/`: 69,920 write events (58,032 strict) and 223,559 attention events in 19 units of analysis (#30, #31, #33, #35, #36b, #37, #38a–c, #39–#42, #44, #51a–e; 1,397 bins). Pipeline: `analysis/r2_run.py` (R4, R4d, R5, D2.6, R6–R8). Numbers: `round2/results.json`, `round2/G<NN>/results.json`, `round2/synthetic.json`, `round2/confirm_dryrun.json`. Figures: `figures/r2_summary_obs.pdf`, `r2_kw.pdf`, `r2_synthetic.pdf`. Holdout asserted absent in every table.

**Headline.** No effective superagent was found.
- **No candidate unit acts more like one agent than random groups do.** Crews (joint work on a shared artifact), behavior-synchrony communities, co-allocation communities, reply communities, rooms and labs all sit at the random-group level of individuality: crews' Stouffer Z +0.06 over 200 crews, and 2–8% of units are local maxima.
- **None carries measurable KW semantic information about its environment.** ΔV_st ≥ 0.005 in 2/19 units and ΔV_obs > 0 in 0/19.
- **None repairs itself beyond what independent members would.**
- **What does persist is allocation.** Agents return to the same artifacts after every night's context erasure (crews' ΔC 0.47, ≥ 0.2 in 15/19 units) and after memory loss (16/17 events). But single agents with their own artifacts out-persist every multi-agent coarse-graining (15/18 units), and crews never turn over their members.
- **The operator's goal sets the rate.** A goal change cuts advancement by 0.39 (z −2.75), whether or not the old artifacts stay relevant.
- **Best reading:** the village's persistent unit is the **agent plus its own artifact**, a stigmergic individual whose day-scale information lives in the repo, not in its memory or context. The prompt drives it, and coordination adds little on top. That is a scaffolded collective, not an effective superagent. The caveat is power: the timing-individuality test had ≤ 7% validated power at village sampling, so R4's null is weak. The strongest negatives are R4d (single agents beat crews) and R8 (no repair beyond aggregation).

**Synthetic validation (axis F):** see Amendment A1. Only night continuity, memory-loss continuity and the KW kernel (when Markov) are identifiable at this sampling.

**Outcome vs prediction**

| | Prediction (locked 2026-10-04; A1) | Outcome | Verdict |
| --- | --- | --- | --- |
| R4a | crews have the highest median composition z in ≥ 2/3 of units | crews first in 5/18 units; a room or lab first in 9/18 (falsifier "≥ 1/2" triggered). iota_alloc variant: 6/19 | **failed** (not identifiable: validated power ≤ 7%, A1.1) |
| R4b | ≥ 50% of crews are local maxima, more than rivals | crews 3.5%, synchrony 1.7%, co-allocation 2.4%, reply 7.5%, rooms 5.6%, labs 1.7% | **failed** |
| R4c | crews' composition z > 0, Stouffer p < 0.01 | Z = +0.06 (p 0.48, 200 crews); unit median ≤ 0 in 14/18 | **failed** |
| R4d (A1) | ΔC(crew, co-allocation) > ΔC(room, lab) in ≥ 2/3 of units | 4/19; single agents have the higher ΔC in 15/18 units (median 0.66 vs crews 0.47) | **failed** (allocation persistence is individual first) |
| R5a | crews' ΔV_st > 0 (CI, ≥ 0.005) in ≥ 1/2 of units and > members' in ≥ 2/3 | 2/19 positive (#36b +0.006, #38c +0.009); 4/19 significantly negative (#37, #38b, #51a, #51b; down to −0.07, units with large I and thin cells); crew > members in 12/19. Day-level landscape −0.010 … +0.011 | **failed** |
| R5b | ΔV_obs > 0 in ≥ 1/2 of units | 0/19; 17/19 slightly negative (−0.0001 … −0.025) | **failed** |
| R5c | goal change lowers V_adv (z ≤ −2); less at the continuation boundary | −0.39 ± 0.14 (z −2.75) over 7 new-goal boundaries; continuation #39 → #40 −0.37 | **supported by the letter**; contrast negligible (`NE34/`) |
| R5d | channel cuts and stalls lower V_G (−0.25 SD, z ≤ −2) | #focus split vs kept crews DiD +0.02 (7 vs 24); after stalls, units write within 30 min in 84% of cases (aggregation baseline 88%) | **failed** (no cost) |
| R6a | one-member scramble cheap: others within ±10%, β ≤ 1 | others +1.8% (median), Stouffer Z +2.44 (< 3, A1.5); β median 0.80. The self-dip positive control is not reproduced at 5-min resolution (median +2%; clear dips only in #51a, #51b, #44, #38b, #51e) | **inconclusive** (positive control failed). Lead: where the self dip is clear (#51a, #51b), others' writes rise +4–9% (z +3.8, +4.4) |
| R6b | crews' ΔC ≥ 0.2 in ≥ 2/3 of units | 15/19 (leave-out), median 0.47; in-sample 16/19 | **supported** (necessary, not sufficient) |
| R6c | continuity after memory loss: event − base > −0.2 | 16/17 unique agent-days (0.94) vs base 0.91 (+0.03); 7 agents, 8 events from one agent; mostly #51 | **supported by the letter**, weak (n, private-goal confound) |
| R6d | crews' coordination (shift) excess > 0 in ≥ 2/3 | 6/18 | **failed** |
| R6e | unit-level scrambles ≫ summed one-member costs | goal change −0.39 vs one-member costs ≈ 0 | holds only because a goal change is a field change, not a store scramble |
| R7a | after a departure, ΔV_cnt ≥ −share; death hazard in placebo band | 10 unique departures: crew write rate +0.15 (median; mean +0.43) vs placebo +0.29; departed share 0.33; no crew died | **supported by the letter** (no compensation beyond placebo) |
| R7b | long-lived crews turn over (Jaccard < 0.5) without decline | median Jaccard 1.0; 0 of 82 crews turn over | **failed**: no Ship of Theseus to observe |
| R7c | R_G written after new goals ≤ 20%, continuation ≥ 50% | 98% at new-goal boundaries, 100% at continuation | **failed**: units slow down, they don't dissolve |
| R8a | others' write after unconfirmed vs confirmed push ≥ 1.2× in ≥ 2/3 | median 1.04; 2/19 | **failed** (not identifiable, A1.7) |
| R8b | others compensate after a member's forced consolidation | +1.8%, not significant (A1.5) | **failed** (lead as in R6a) |
| R8c | units recover after stalls faster than the aggregation baseline | 0.84 vs 0.88 | **failed** |
| D2.6 | a homeostatic group-level V exists | none in either regime group (V_adv, V_cnt, V_mem, V_foc, V_ord, V_rel against 200-draw pseudo-stalls) | **inconclusive** → V_adv by default |

**R4 candidates found.** None qualifies as a superagent candidate by the pre-registered criteria. The per-unit verdict rule gives one "supported" unit, #38a (crews' within-unit Stouffer Z +2.06, first among coarse-grainings, ΔC 0.51 above rooms and labs). That is the expected false-positive count for 19 units at Z > 1.64, so it is not a finding. The units that carry the most persistence are single agents with their own projects (ΔC 0.4–0.9).

**What it means in Kolchinsky–Wolpert terms.**
1. **Where the day-scale information lives.** Every member's context is erased every ~14 active minutes and every night, and memory carries ≈ 0 viability value at day scale (H15). Yet agents return to the same artifacts the next day, and they keep doing so after memory loss. So the information that sets *what to work on* is held outside the member: in the repo (and local workspace), the chat history, or the prompt (in #51, the private goal). This is H15's finding seen from the unit's side.
2. **Relative to a unit boundary that includes the artifact, that information is internal.** It is self-information, not semantic information about the environment. The stored and observed KW quantities for crews about their environment (the rest of the swarm's activity, human and automated messages) are ≈ 0, inside small Pinsker envelopes. The KW "value" appears only for the goal: a full relevance scramble costs 0.39 of the unit's advancement rate (natural-scramble variant). In Krakauer et al.'s terms the units are **environmentally determined**, not organismal.
3. **Effective agency is not found.** One-member scrambles cost the unit nothing measurable, and departures cost no more than placebo. But that is because members are close to independent, not because the group buffers them: there is no coordination excess (R6d), no repair (R8), and single agents persist more than crews (R4d). The "substrate" is not a substrate of negligible agents. An agent plus its own artifact is already the persistent individual, and grouping adds no detectable synergy.

**Round 2 results by goal period** (verdict rule in `analysis/r2_period_folders.py`: agency signature R4 or R5a, plus R6b and R4d; R6b alone does not rescue a unit)

| Folder | Units | Round-2 verdict | One line |
| --- | --- | --- | --- |
| [G30](goalperiod-subhypotheses/G30/README_round2.md) | 30 | failed | 3 crews; no individuality excess; ΔC 0.10 |
| [G31](goalperiod-subhypotheses/G31/README_round2.md) | 31 | failed | 20 crews (farewell week); single agents out-persist crews (0.47 vs 0.12); NE29 succession in `NE29/` |
| [G33](goalperiod-subhypotheses/G33/README_round2.md) | 33 | failed | one shared repo; continuity ≈ 0 over 3 days |
| [G35](goalperiod-subhypotheses/G35/README_round2.md) | 35 | failed | 2 crews (the two RPG forks); ΔC 0.34 |
| [G36](goalperiod-subhypotheses/G36/README_round2.md) | 36b | mixed | ΔV_st +0.006 (CI > 0) but crews below rooms; ΔC 0.20 |
| [G37](goalperiod-subhypotheses/G37/README_round2.md) | 37 | failed | ΔV_st −0.04 (thin cells); ΔC 0.26 |
| [G38](goalperiod-subhypotheses/G38/README_round2.md) | 38a, 38b, 38c | mixed | 38a supported by the rule (chance level, see above); 38c ΔV_st +0.009; 38b failed |
| [G39](goalperiod-subhypotheses/G39/README_round2.md) | 39 | mixed | own-artifact week; crews ΔC 0.65 > rooms 0.37, no agency signature |
| [G40](goalperiod-subhypotheses/G40/README_round2.md) | 40 | mixed | the shared universe repo (13 writers); ΔC 0.37 > labs 0.20, no agency signature |
| [G41](goalperiod-subhypotheses/G41/README_round2.md) | 41 | failed | 16 crews; all coarse-grainings at the null |
| [G42](goalperiod-subhypotheses/G42/README_round2.md) | 42 | failed | ΔC 0.65, single agents 0.82 |
| [G44](goalperiod-subhypotheses/G44/README_round2.md) | 44 | failed | forced-consolidation dips propagate to others (−19%, z −3.7: the one significantly negative spillover) |
| [G51](goalperiod-subhypotheses/G51/README_round2.md) | 51a–51e | mixed | 51e mixed, others failed; #focus cut costs nothing; ΔC 0.43–0.69, single agents 0.73–0.90 |
| [NE34](goalperiod-subhypotheses/NE34/README.md) | 8 goal boundaries | supported (R5c by the letter) | −0.39 advancement at new goals; artifacts still written (98%) |
| [NE29](goalperiod-subhypotheses/NE29/README.md) | #31 | mixed | successor joins a predecessor crew's project; crews lose more than the predecessor's share (farewell week) |
| [NE30](goalperiod-subhypotheses/NE30/README.md) | holdout | pending | C1 succession test (not run) |
| [NE24](goalperiod-subhypotheses/NE24/README.md) | holdout | pending | C4 artifact-migration test (not run) |

**Caveats.**
- **Power.** Timing individuality (R4) had ≤ 7% validated power, and the binary activity state is blind to a group store that sets *which* artifact members work on. Its null says that superagents are not visible this way, not that they are absent.
- **The KW quantities are observational** and only as good as the coarse-grained Markov kernel. Bootstrap CIs are anti-conservative under hidden state (A1.4), and the significantly negative ΔV_st units have thin cells. The environment state (binary activity + messages) is one choice. A unit could hold semantic information about variables we didn't encode (who asked for what, which goal sub-task); measuring that needs the content and context ledgers.
- **No replay, only natural scrambles.**
  - Goal changes bundle a new instruction with the scramble.
  - The only artifact-store scramble (NE24) is held out.
  - Departures and memory losses are endogenous.
  - Forced consolidations are exogenous in timing, but the self-dip positive control was not reproduced in 5-min windows, so R6a/R8b are inconclusive.

  What is identifiable without replay: allocation continuity across exogenous nights; continuity after (endogenous) memory loss; the sign of the goal-change effect; the absence of costs from one-member scrambles. Not identifiable: the stored semantic information of the unit's own store, and any counterfactual on the artifact.
- **The work ledger is an attempts proxy** (F9). It cannot see failures (no reliable failure flag), value, or non-git work. That weakens V_G, R8 and D2.6.
- **Crews are defined from the outcome period.** R4d/R6b use leave-target-day-out membership, but R4's composition nulls use in-period membership; rooms and labs need none.
- **Duplicates.** Overlapping crews duplicate events: memory-loss rows (151 → 17 unique) and departures (16 → 10 unique) were deduplicated after the first run (A2, disclosed). Verdicts don't change.
- **#51's private goals** (prompt-held, agent-specific) can carry project continuity, so R6c's support for artifact-held allocation is weakest exactly where most events are.

**Amendment A2 (2026-10-04, after the first real-data run; disclosed).** Overlapping crews counted one memory-loss event several times. The unique-agent-day statistic is now computed in `r2_run.py` and used by `confirm_r2.py` C3; both are reported. No threshold or verdict changed.

**What the ledgers would add.**
- **A shared work-output ledger** would provide:
  - outcome-resolved writes: merged/failed, CI pass/fail, deploy success, diff size;
  - artifact states: open tasks, broken builds.

  That gives (i) a value-weighted V_G, (ii) real failures for the repair test (R8), and (iii) a unit state richer than "advanced or not". The synthetic shows the binary state is exactly what hides a group store.
- **A context ledger** (what each agent had in context at each turn, and from where) would identify the re-acquisition path after an erasure: repo read, chat, memory note, or prompt. That separates artifact-held from prompt-held information (the open rival in #51), defines each member's stored state for the member-level KW synergy contrast, and measures the observed channel artifact → member directly.

**Next steps.** (1) Sign off and run `analysis/confirm_r2.py --confirm …` (NE24 is the one artifact-store scramble; NE30 the cleanest succession). (2) H58: a coordination-first search (behavior states + co-adoption + reply threads + artifacts jointly), with a state that encodes *which* artifact rather than *whether* work happened. (3) Treat the agent + own-artifact pair as the unit: its stored semantic information about the goal and other agents, with the context ledger. (4) Recompute R5 with outcome-resolved writes once the work ledger exists.
