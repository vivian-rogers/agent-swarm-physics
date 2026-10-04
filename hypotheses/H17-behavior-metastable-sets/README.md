# H17: Behavior is a Markov state model with a few metastable sets; its mixing time is a per-period order parameter

**Status:** exploratory round 1 done (2026-10-03): 27 non-holdout goal periods, 13 mixed / 14 failed / 0 supported; core predictions (Markovianity, sets beyond sticky states, order parameter tracking stuckness, regime contrast) mostly failed. **Round 1b (2026-10-04, Jev v3.1 states, real failures):** the soft-state MSM's slowest mode is agent-day scale (hours), its slow set is still acting vs waiting, and neither t2\* nor `p_blocked` orders periods by stuckness (wrong sign); natives NE41, NE43 and #27 failed. Not promoted. Confirmatory script written, not run.
**Fields:** stat mech, dynamics
**Origin:** HH97 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Literature:** none in `literature/` yet for MSM practice. Standard references (not in the folder): Prinz et al., *J. Chem. Phys.* 134, 174105 (2011) (MSM estimation, ITS, CK test)†; Röblitz & Weber, *Adv. Data Anal. Classif.* 7, 147 (2013) (PCCA+)†; Metzner, Schütte & Vanden-Eijnden, *Multiscale Model. Simul.* 7, 1192 (2009) (transition path theory)†; Reuter et al., *J. Chem. Phys.* 149, 174102 (2018) (non-reversible PCCA)†.
**Definitions used** (`physics-models/DEFINITIONS.md`): Regime; Action; Activity time; Agent state (categorical: action class), in H14's coarse 6-state scheme; Entropy production, in H14's variant "entropy production (Markov pair-KL on categorical behavior states)". New named terms proposed for DEFINITIONS.md (owner to add): **"Markov state model (MSM, lag τ)"**, **"implied timescale"**, **"metastable set (PCCA+)"**, **"mixing time (MSM)"**, defined in Observables below.

## Standards (2026-10-04)
**Question served:** Q6 (behavior kinetics: a mixing time as a per-period order parameter).

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | Rivals R3 (schedule drift) and R4 (scaffold timer) named; out-of-span windows dropped (Round 1b). The slow mode is attributed to the agent-day mixture and the wait state. | removed |
| Exogenous field (kickoff/goal/operator) | partly | NE43 drive withdrawal (N2): t2\* swings ×6–7 between ordinary blocks, so no step is detectable. | partly |
| Shared model priors | no | Per-agent MSMs with the agent-mixture rival R2 (N4); no family claim. | n/a |
| Contemporaneous convergence | no | Single-agent dynamics. | n/a |

**Inputs:** round 1b uses Jev v3.1 and real failures (`n_errors`, `turn_outcomes.failed`); action classes come from `actions` + `events_core`, untouched by the fixes. Still old: the output rate counts git-printed commits and pushes, not the DQ4 `work_ledger`.

**Two layers:** 27 replication folders. Natives: 3 in the card (NE41, NE43, #27), all failed; 2 folders carry `**Role:** native`.

**Confirm script:** `confirm_h17.py` (P9–P9c on #32, #45), written and dry-run, not run. Re-freeze: no; action-class states are hash-locked to H14's builder and unaffected. A Jev-state P9 needs its own pre-registration first (Notes).

## Question
Coarse-grain each agent's behavior-state sequence into a Markov state model. Do a few slow, metastable sets ('attractors' such as coding, debugging loops, existential talk) dominate, as identified by spectral clustering of the transition matrix (PCCA+)? Is the spectral gap, or slowest implied timescale, a per-goal-period order parameter: slowest in stuck periods, fastest in productive ones? Practical payoff: a compact map of where agents get stuck and how fast they move between modes.

## Model
**From:** `physics-models/02-nonequilibrium-ising` and `10-potts` (kinetic Potts as a Markov chain), with Markov-state-model machinery: implied timescales and the Chapman–Kolmogorov test for Markovianity at lag τ, PCCA+ metastable sets, committors between sets. Nonequilibrium: the transition matrix need not satisfy detailed balance, so cycle currents are expected (link to H14).

## Data scheme (`scheme/`)
Shared tables in `data/processed/shared/` (see `infra/README.md`). Use `chat_mentions_clean.parquet`, not `chat_core.mentions` (H17 round 1 uses no mentions).
- **States: H14's builder is imported, not copied** (`hypotheses/H14-behavior-entropy-production/scheme/build_states.py: build(days)`): records = computer-use turns ∪ agent events with mirror turns (regime-III `pause`, `send_message_back_to_chat`, `search_history`, `move_to_room`) and the scaffold-forced `mouse_move` removed; regime-I WAIT and CONSOLIDATE gaps assigned on the minute grid as logged-at-end intervals; declared PAUSE durations carried forward. Coarse states (q = 6): browse, type, shell, chat, idle, consolidate (= consolidate + search + session). Minute grid `coarse_min`: chat > consolidate > majority work class > idle. An agent-day is *present* if it has ≥ 10 records.
- **`scheme/build.py`** calls that builder on non-holdout days and freezes H17's own copies (so a rebuild by H14 cannot change H17's inputs mid-round), and adds **`states_win5.parquet`**: agent × 5-min window (w = minute // 5, the Jev window index), hard state (majority of the window's minutes; ties chat > consolidate > shell > type > browse > idle) and soft state (fraction of the window's minutes in each coarse state).
- **Any categorical state table** (hard labels) or probability-vector table (soft labels) runs through the same pipeline: `analysis/h17lib.py: load_states()`, including the Jev output format (`behavior` + `behavior_probs`). The Jev full run (10 states, taxonomy v2) will replace the coarse states without code changes.
- **Covariates (not used to define states):** `actions.error` (error share) and `artifact_mentions` (source = action, verb ∈ {git commit, git push, deploy}: output events).
- **Output:** `data/processed/H17-behavior-metastable-sets/` (`states_*.parquet`, `synthetic/`, one subfolder per goal period `G<NN>/`), with `_provenance.json`. Holdout days are never read by the scheme; the confirmatory script builds them in memory.

## Candidate goal periods
All non-holdout periods, per goal period; regime I vs III. #32 and #45 (loop-heavy, 🔒 held out) for confirmation.
- **Round 1 (fixed 2026-10-03 before running):** regime III #37, #38, #39, #40, #41, #42, #44 and #51 (non-holdout days 07-06 → 09-04; weekly blocks for O10). Regime II #33, #35 (comparison). Regime I: every non-holdout period with ≥ 6 present agents and ≥ 3 days: #10, #11, #12, #13, #16, #17, #18, #19, #20, #21, #23, #24, #25, #26, #27, #30, #31.
- **Not analysed:** #36 (straddles the 2026-03-24 regime boundary), #2–#8 (≤ 6 agents with ≤ 2 h days, or < 3 days), the holdout.

## Links to other hypotheses
H14 (EP on the same states: irreversibility = cycle currents of the MSM); H16 (traps = metastable sets?); HH47 (free-energy landscape).

## Observables
*Written 2026-10-03, before any real-data run.* Per goal period. The pooled MSM uses every present agent-day of the period; transitions are counted only within an agent-day (sliding-window counts at lag τ, no transitions across days).
- **Time bases.** Primary: the 1-min active-time grid (`coarse_min`, q = 6), lags in active minutes. Secondary: each agent's record sequence (`coarse`, q = 6; fine `act`, q ≤ 11 after H14's < 1% rare merge), lags in records. Jev bridge: 5-min windows (hard; soft composition).
- **O1 implied timescales (ITS).** t_k(τ) = −τ / ln|λ_k(T(τ))|, k = 2…4, for the non-reversible maximum-likelihood T(τ) (row-normalized counts; primary: the village is not at equilibrium, so eigenvalues may be complex and |λ| is used) and its additive reversibilization T_ar = (T + Π⁻¹TᵀΠ)/2 (companion). τ ∈ {1, 2, 3, 5, 7, 10, 15, 20, 30} min (records: {1, 2, 3, 5, 8, 12, 20, 30, 50}). 95% CIs from an agent-day bootstrap (200 replicates).
- **O2 order parameter.** **t2\* ≡ t2(τ_c = 5 min)** on the minute grid, in active minutes, at a fixed lag for every period (no lag choice per period). Companions: spectral gap g = 1 − |λ2(τ_c)|; mixing time t_mix(¼) = smallest k·τ_c with max_i TV(T(τ_c)^k[i,·], π) ≤ ¼; t2 at the plateau lag τ\* (smallest grid τ with |t2(τ_next) − t2(τ)| / t2(τ) < 0.15; "no plateau" if none up to 15 min).
- **O3 metastable sets.** m = argmax over m ∈ {2, 3, 4} of λ_m − λ_{m+1} (eigenvalues of T_ar(τ_c)); PCCA+ memberships χ (Röblitz–Weber inner-simplex start, then maximize the crispness objective); crisp sets = argmax χ; **crispness** = π-weighted mean of max_k χ_ik; **metastability** = trace(T_cg)/m with T_cg = (χᵀΠχ)⁻¹χᵀΠTχ; **timescale separation** t2/t3; set composition. Also the **sticky-only rival R1** fitted to the same data (T_ii = s_i, T_ij = (1 − s_i)ν_j/(1 − ν_i), ν = the frequency of jumps into each state; fitted at the same lag) and the ratio t2\*/t2_R1.
- **O4 Chapman–Kolmogorov test** on the crisp sets at τ_c, k = 1…5: Δ_A(k) = P_est(A → A, kτ_c) − P_pred(A → A, kτ_c), with P_pred from T(τ_c)^k weighted by the empirical start distribution within A at lag kτ_c. **Pass = max over sets and k ≤ 4 of |Δ| < 0.05** (practical tolerance; with ~10⁴–10⁵ transitions, significance alone would reject everything). Bootstrap significance and the full-state CK error (π-weighted mean |T(τ_c)^k − T(kτ_c)|) are reported alongside.
- **O5 committors and transition path theory** between the cores of the m = 2 split (core = the state of maximal membership in each set), on T(τ_c): forward q⁺_i and backward q⁻_i for the other states; nonequilibrium asymmetry **δ_i = q⁺_i − (1 − q⁻_i)** (0 under detailed balance); reactive rate k_AB; mean first-passage times A → B and B → A.
- **O6 currents (link to H14).** MSM plug-in entropy production per step at τ = 1 min, σ = ½ Σ_ij (π_iT_ij − π_jT_ji) ln(π_iT_ij / π_jT_ji) (pairs with both counts > 0); the share that survives lumping into the PCCA+ sets, σ_macro / σ_micro, always on the **m = 3** split (a stationary two-set chain carries no net current, so σ_macro = 0 by construction for m = 2; amended 2026-10-03 before any run); complex eigenvalue pairs of T(1) (|Im λ| > 2 bootstrap SE) and their period 2π/|arg λ|. H14 owns the EP estimators; these are MSM descriptors.
- **O7 agent heterogeneity.** Per-agent MSMs for agents with ≥ 2 present days and ≥ 300 transitions in the period: t2_i(τ_c) with bootstrap SE of ln t2_i; **I²** of ln t2_i across agents (Cochran Q); lab η² (descriptive); pooled vs. per-agent CK error; day-blocked held-out log-likelihood per lagged pair (τ_c) of the pooled, per-agent and shrinkage MSMs (per-agent counts + 10 pseudo-counts per row distributed as the pooled T).
- **O8 adequacy.** Day-blocked folds over PT days (k = min(5, days)): held-out log-likelihood per lagged pair at τ_c and at τ = 1 of M0 (occupancy only), R1 (sticky-only) and M1 (MSM); order 2 vs. order 1 at τ = 1 (Markov-order audit on the minute grid).
- **O9 stuckness covariates** (not part of the state definition): **error share** = fraction of the period's computer-use turns with `actions.error`; **output rate** = distinct (agent, turn) action mentions with verb git commit / git push / deploy per present agent-hour; idle share (descriptive only, because it is mechanically tied to the idle state). Per period and per agent.
- **O10 within-period stationarity.** #51 non-holdout split into calendar weeks: t2\* per week; ratio of the between-week CV (#51) to the between-period CV (regime III). In every period, t2\* on the first vs. second half of each day (rival R3).
- **O11 preprocessing robustness (axis F).** t2 on the record sequence (converted to minutes with the period's median records per present minute; descriptive); on 5-min windows (hard; soft counts; shifted soft estimator, below); with consolidate records removed (decimated minute chain).
- **Soft-state estimators** (for Jev probability vectors; validated synthetically before use): soft counts C(τ) = Σ_t p_t p_{t+τ}ᵀ, row-normalized; and the **shifted estimator**: eigenvalues of C(τ₀)⁻¹C(τ₀ + τ) with τ₀ = 1, which cancels classifier noise that is independent across windows (eigenvalues → λ^τ exactly).

## Null / baseline
*Written 2026-10-03, before any real-data run.*
- **N1 shuffled order within agent-day** (100 surrogates): keeps each agent-day's occupancies, destroys all temporal order. Floor for t2.
- **N2 sojourn-preserving null (primary for "sets")** (100 surrogates): each agent-day is cut into runs (state, length); runs are permuted within the agent-day, with adjacent identical states removed by random swaps (residual merges counted). Keeps occupancies and every state's dwell-time distribution; destroys the order of runs, i.e. the embedded jump chain, any set structure and longer memory. A slow mode that is just one sticky state survives N2; a metastable set of several states does not.
- **N3 semi-Markov reference** (100 surrogates): the empirical embedded jump chain with resampled per-state dwell lengths (each agent-day's real start state and length). Keeps set structure in the jump chain; destroys correlations between successive dwells and longer memory. A reference, not a null: t2\* ≈ N3 means a semi-Markov model with sets suffices.
- **N4 heterogeneity:** pooled vs. per-agent MSMs (O7).
- **N5 detailed balance for currents:** N1 and N2 surrogates are reversible in expectation (exchangeable orders), so σ under them is the estimator floor. H14's detailed-balance surrogate stays primary for EP.
- **N6 synthetic ground truth** (axis F): chains with planted metastable sets at village sampling.
- **Rivals.** **R1 sticky states:** each state is metastable on its own; no multi-state sets (parametric form above; nonparametric form N2). **R2 agent mixture:** slow modes and CK failures come from pooling heterogeneous agents. **R3 schedule drift:** within-day nonstationarity (start-of-day chat, end-of-day idling) mimics slow modes: no ITS plateau, and t2 differs between halves of the day. **R4 scaffold timer:** in regime III, the slowest process is just the declared PAUSE durations (H09 E6: pauses are timers), so the slow "set" is the idle state alone.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 sticky states (parametric; nonparametric = N2 sojourn null); R2 agent mixture; R3 within-day schedule drift; R4 scaffold timer (idle alone).
**Locked holdout used for confirmation:** none yet. `analysis/confirm_h17.py` (P9/P9b/P9c on #32 and #45) is written and dry-run on stand-ins #31/#44; not run.

*Scored 2026-10-03 after exploratory round 1 (action-class states only).*

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | States from `actions` + `events_core` via H14's scheme, assumptions listed. Not invariant: regime-I "consolidate" is session start/stop, the GUI → bash shift changes what browse/shell mean, and minute-grid idle mixes declared pauses, latency gaps and pre-start/post-stop minutes (80% of idle minutes in #37). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 0 | CK fails in 27/27 periods (max \|Δ\| 0.10–0.32). ITS rise ×3.4–6.8 from τ = 1 to 15 min, with a plateau in 1/8 regime-III periods. Order 2 beats order 1 on held-out days in 27/27. Stationarity is fine: first/second half-day t2\* ratio 0.96 (median); #51 weekly CV 0.17. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | MSM beats M0 and R1 on held-out days in 25/27. t2\* is above the sojourn null in every period, but by only ×1.06–1.62, and the primary rule passes in 3/8 regime-III periods. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | Signature missing: t2/t3 ≥ 2 in only 30% of periods. t2\* does not track error share or output (P4b). Regime contrast reversed (P4c). Committors symmetric (P6). Only P7 held: irreversibility sits inside the sets. |
| E interventional | predicts the change across a natural experiment | 0 | NE07 ("don't do nothing"): t2\* *rose* 4.2 → 7.1 min (difference CI [+1.0, +4.9]). NE10: no change. NE17: +1.5 min, n.s. (descriptive). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic: t2 unbiased (median ratio 0.98–1.10, coverage ≈ 0.9); PCCA+ ≥ 90% exact; N2 calibrated (0% false positives, 100% power); block-bootstrap I² calibrated; shifted soft estimator works. But the practical CK has low power (17–27%). Real data: t2\* agrees across minute grid, records and 5-min windows (×1.1–1.4). The slow-set identity is not robust to pooled vs per-agent estimation. |
| G ground truth | agrees with known structure | 1 | Slow splits match known scaffold structure: GUI (browse+type) vs shell tool modes; regime-I in-session vs out-of-session in the early periods; #37's boundary idling. No external "stuck" labels outside the holdout. |
| H comparative | beats the named rivals | 1 | Beats R1 (held-out ΔLL > 0 in 25/27; t2\*/t2_R1 = 0.96–1.59). R3 rejected (no within-day drift). But R2 explains as much of the pooled t2\* as the set structure does: pooled/median-agent t2 = ×1.28 (0.93–1.80). R4 holds within agents (idle alone for 25–92% of regime-III agents). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Per-period verdicts are 13 mixed, 14 failed, 0 supported; holdout not run. |

## Prediction
*Written 2026-10-03, before any real-data run of the MSM pipeline.* What I had seen: H09's E2/E6 results (event-level cycle consolidate → search → talk → pause; regime-III pauses are timers, median 180 s, with re-pause chains), H14's card and scheme including its audit counts (class mix of the minute grid pooled over all non-holdout days: idle 33%, browse 17%, shell 17%, consolidate 15%, chat 10%, type 7%), and period sizes (agents, days, present minutes). No transition counts and no MSM on real data.

- **P1 (synthetic, axis F).** At village sampling (10–27 agents, 3–45 days, 240 or 480 steps/day, non-stationary day starts):
  - (i) t2 at τ = 5 is recovered within ±20% (median) when t2_true ≤ 30 steps and the period has ≥ 100 expected inter-set crossings; it is biased low by > 20% when t2_true ≥ 60 steps on 240-step days (finite days). Bootstrap 95% CI coverage ≥ 85% in the first regime.
  - (ii) PCCA+ recovers the planted partition exactly in ≥ 90% of runs when t2/t3 ≥ 3; the eigen-gap rule picks the planted m in ≥ 80%.
  - (iii) The CK test passes for true Markov chains in ≥ 90% of runs, and fails for a lumped hidden-state (non-Markov) chain in ≥ 80%.
  - (iv) N2 has false-positive rate ≤ 7% for R1 chains (sticky states, no sets) and power ≥ 80% for planted sets with t2/t2_R1 ≥ 1.5.
  - (v) With per-agent t2 spread 4× (log-uniform), I² > 0.5 is detected in ≥ 80% of runs, and the pooled CK error exceeds the per-agent median.
  - (vi) Soft states (Jev-like, q = 10, argmax accuracy ≈ 0.6): argmax and soft-count ITS underestimate t2 by ≥ 30% at τ = 1 window; the shifted estimator is within 20%.
  - *Falsifier:* a failed item makes the matching real-data observable descriptive only.
- **P2 (Markovianity, axis B).** On the minute grid t2(τ) rises with τ at short lags and reaches a plateau (O2 rule) by τ ≤ 15 min in ≥ 50% of regime-III periods, and the CK test passes at τ_c in ≥ 50% of periods. Order 2 beats order 1 at τ = 1 on held-out days in every period (hidden memory at 1 min). Credence ≈ 0.45 that both halves hold.
- **P3 (metastable sets; the core claim).**
  - (a) t2\* exceeds the N1 floor in every period (trivial; p < 0.01).
  - (b) **Primary:** t2\* above the N2 95th percentile *and* t2\*/median(N2) ≥ 1.25 in ≥ 50% of the 8 regime-III non-holdout periods (Holm across periods). Credence 0.5.
  - (c) m ∈ {2, 3} in ≥ 75% of periods, crispness ≥ 0.75, and t2/t3 ≥ 2 in ≥ 50%.
  - (d) In regime III, idle sits in a set of its own (alone or with consolidate) in the m = 2 split in ≥ 50% of periods: the slowest process is active ↔ idle. Credence 0.6. If (b) fails and (d) holds, the slow mode is a sticky idle state (R1/R4), not a set of behaviors.
  - (e) t2\* lies between 5 and 60 active minutes in every regime-III period.
- **P4 (order parameter; the HH97 claim).**
  - (a) Periods differ: I² of ln t2\* across regime-III periods ≥ 0.75, and the between-period CV of t2\* exceeds the between-week CV inside #51. Credence 0.55.
  - (b) Stuckness: across the 8 regime-III periods, Spearman ρ(t2\*, error share) > 0 and ρ(t2\*, output rate) < 0 (descriptive: |ρ| ≥ 0.74 would be needed for p < 0.05). **Testable form:** within periods, per-agent correlations meta-analyzed (Fisher z, weights n − 3) have the same signs with p < 0.025 each. Credence 0.35 (across periods), 0.4 (within-period meta).
  - (c) Regime: regime-I periods have longer t2\* than regime-III periods (session on/off is a two-set process with dwell times of tens of minutes): Mann–Whitney p < 0.05. Credence 0.6.
  - (d) Free-choice periods (#31, #37) are not the fastest in their regime. Descriptive.
- **P5 (heterogeneity, R2).** In ≥ 75% of periods, I² of per-agent ln t2 ≥ 0.5, per-agent or shrinkage MSMs beat the pooled MSM on held-out days for ≥ 60% of agents, and the pooled CK error exceeds the median per-agent CK error. Credence 0.7.
- **P6 (committors; nonequilibrium; not blind).** In regime III, max_i |δ_i| ≥ 0.1 with a bootstrap CI excluding 0 in ≥ 50% of periods. If the m = 2 cores are a work state and idle, chat has q⁺ > 0.5 (it goes on to idle) and 1 − q⁻ < 0.5 (it came from work). Informed by H09 E2 and H14 P5. Credence 0.5.
- **P7 (currents).** σ(τ = 1) above the N2 95th percentile in every period; σ_macro/σ_micro < 0.5 (most irreversibility sits inside the metastable sets, in fast work cycles) in ≥ 50% of periods. Credence 0.5.
- **P8 (adequacy, axes C/H).** The MSM beats M0 and R1 on held-out days at τ_c in every period (ΔLL > 0 in ≥ 4 of 5 folds, or all folds when fewer). Credence 0.85.
- **P9 (confirmation on the locked holdout; written, not run).** On action-class states: t2\* of #32 above the 75th percentile of the regime-I non-holdout periods, and t2\* of #45 above the 75th percentile of the regime-III non-holdout periods. Credence 0.35 each. Its own pre-registration on Jev states will follow when those exist (theory spirals like #45's "temporal bleed" are content, so action classes may not see them).
- **P10 (natural experiments inside periods, axis E; added 2026-10-03, still before any real-data run).** Interventions on waiting should shorten the idle-driven slow mode:
  - **NE07** (12-04, prompt "don't do nothing", targets waiting loops; inside #21): t2\* on 12-04 → 12-05 below t2\* on 12-01 → 12-03, with the agent-day bootstrap 95% CI of the difference excluding 0.
  - **NE10** (02-10, the auto-nudger switched on; inside #30): t2\* on 02-10 → 02-13 below t2\* on 02-09 (one day before: very low power).
  - **NE17** (04-14, outreach approval; inside #38): no prediction (descriptive split).
  - Credence 0.35 each. Within-period scaffold changes not tested: NE11 (02-20, #31), NE18 (04-20, #38), NE32 (07-09, #51), NE33 (09-03/04, last days of the #51 window).
- **P9b, P9c (added 2026-10-03 after the exploratory round, before any holdout use).** The same 75th-percentile comparison for #32 and #45 on (b) t2\* with the leading and trailing idle runs of each agent-day removed, and (c) the median per-agent t2 at τ_c, which avoids the agent-mixture inflation of the pooled t2\* found in round 1. `confirm_h17.py` computes P9, P9b and P9c. Credence 0.3 each: round 1 found that t2\* does not track stuckness covariates.
- **Multiple comparisons and power.** Primaries: P3b (Holm across the 8 regime-III periods), P4a, P4b within-period meta (two tests at α = 0.025), P4c, P5. Everything else is descriptive. With 8 regime-III periods, across-period correlations are descriptive by construction.
- **Amendments from synthetic validation (2026-10-03, after P1 and before any real-data run).**
  - **Per-agent I²** uses standard errors from a within-day block bootstrap (60-min blocks). The agent-day bootstrap (≤ 5 days per agent) gave I² > 0.5 for homogeneous agents in 40% of runs; block SEs gave 0%, with 100% power at a 4× spread.
  - **P5's other two clauses become descriptive.** The pooled-vs-per-agent CK comparison is uninformative at village sizes: per-agent noise dominates, so the pooled error was never larger. The held-out test (own/shrinkage beats pooled for ≥ 60% of agents) is underpowered: 13–36% even at a 4× spread. **P5 = I² ≥ 0.5 alone.**
  - **CK:** the practical criterion keeps its size (≥ 90% pass on Markov chains) but has low power against moderate lumping (17–27% at t2 = 10). The bootstrap-significance criterion has power ≈ 1 but false-fail rates of 7–43%. Both are reported. The verdict rule keeps the pre-registered practical criterion, but a CK pass counts only as weak evidence. The **ITS rise t2(15 min)/t2(1 min)** is added as a Markovianity diagnostic: ≈ 1 for Markov chains, 2.3–4.3 for the lumped chain.
- **Per-period verdict rule** (each `goalperiod-subhypotheses/G<NN>/README.md`): **supported** if the CK test passes at τ_c, t2\* beats N2 (P3b) and the MSM beats R1 (P8); **mixed** if exactly one of CK or P3b fails; **failed** if both fail.

## Results by goal period
Verdict rule (card): supported = CK passes, P3b holds and P8 holds; mixed = exactly one of CK or P3b fails; failed = both fail. Regime-III P3b uses 400 N2 surrogates (200 for #51) with Holm across the 8 periods. CK failed everywhere, so "mixed" means t2\* beat the sojourn null by ≥ 1.25×.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G10](goalperiod-subhypotheses/G10/README.md) | exploratory (regime I) | failed | t2\* 5.3 min [4.5, 6.5]; t2\*/N2 1.23; slow split idle \| browse+type+chat+consolidate; CK 0.20; ITS rise ×5.9; I² 0.69 |
| [G11](goalperiod-subhypotheses/G11/README.md) | exploratory (regime I) | failed | t2\* 4.6 min [4.0, 5.6]; t2\*/N2 1.15; slow split browse+type+shell+consolidate \| chat+idle; CK 0.14; ITS rise ×5.0; I² 0.84 |
| [G12](goalperiod-subhypotheses/G12/README.md) | exploratory (regime I) | mixed | t2\* 4.6 min [4.0, 5.4]; t2\*/N2 1.43; slow split browse+type+shell+consolidate \| chat+idle; CK 0.12; ITS rise ×4.6; I² 0.53 |
| [G13](goalperiod-subhypotheses/G13/README.md) | exploratory (regime I) | failed | t2\* 4.3 min [3.6, 5.4]; t2\*/N2 1.12; slow split chat+idle \| browse+type+shell+consolidate; CK 0.19; ITS rise ×4.8; I² 0.89 |
| [G16](goalperiod-subhypotheses/G16/README.md) | exploratory (regime I) | mixed | t2\* 4.1 min [3.4, 4.8]; t2\*/N2 1.30; slow split shell+chat+idle \| browse+type+consolidate; CK 0.11; ITS rise ×3.7; I² 0.45 |
| [G17](goalperiod-subhypotheses/G17/README.md) | exploratory (regime I) | mixed | t2\* 5.8 min [4.8, 7.2]; t2\*/N2 1.62; slow split browse+type+shell+consolidate \| chat+idle; CK 0.15; ITS rise ×3.4; I² 0.69 |
| [G18](goalperiod-subhypotheses/G18/README.md) | exploratory (regime I) | mixed | t2\* 4.9 min [4.5, 5.5]; t2\*/N2 1.38; slow split browse+type+shell+consolidate \| chat+idle; CK 0.13; ITS rise ×3.6; I² 0.55 |
| [G19](goalperiod-subhypotheses/G19/README.md) | exploratory (regime I) | mixed | t2\* 4.7 min [4.1, 5.4]; t2\*/N2 1.25; slow split browse+type+shell+consolidate \| chat+idle; CK 0.13; ITS rise ×3.5; I² 0.67 |
| [G20](goalperiod-subhypotheses/G20/README.md) | exploratory (regime I) | failed | t2\* 4.7 min [4.1, 5.4]; t2\*/N2 1.16; slow split shell+idle \| browse+type+chat+consolidate; CK 0.16; ITS rise ×3.8; I² 0.78 |
| [G21](goalperiod-subhypotheses/G21/README.md) | exploratory (regime I) | mixed | t2\* 5.5 min [4.6, 6.4]; t2\*/N2 1.36; slow split shell+chat+idle \| browse+type+consolidate; CK 0.16; ITS rise ×3.9; I² 0.91 |
| [G23](goalperiod-subhypotheses/G23/README.md) | exploratory (regime I) | failed | t2\* 5.2 min [4.1, 6.4]; t2\*/N2 1.08; slow split shell \| browse+type+chat+idle+consolidate; CK 0.27; ITS rise ×6.4; I² 0.59 |
| [G24](goalperiod-subhypotheses/G24/README.md) | exploratory (regime I) | failed | t2\* 5.6 min [4.5, 7.1]; t2\*/N2 1.06; slow split shell \| browse+type+chat+idle+consolidate; CK 0.26; ITS rise ×6.1; I² 0.90 |
| [G25](goalperiod-subhypotheses/G25/README.md) | exploratory (regime I) | mixed | t2\* 5.1 min [4.3, 6.1]; t2\*/N2 1.29; slow split shell+idle \| browse+type+chat+consolidate; CK 0.14; ITS rise ×4.5; I² 0.86 |
| [G26](goalperiod-subhypotheses/G26/README.md) | exploratory (regime I) | failed | t2\* 5.1 min [4.3, 5.9]; t2\*/N2 1.23; slow split browse+type+consolidate \| shell+chat+idle; CK 0.12; ITS rise ×3.4; I² 0.89 |
| [G27](goalperiod-subhypotheses/G27/README.md) | exploratory (regime I) | mixed | t2\* 6.2 min [5.5, 6.9]; t2\*/N2 1.26; slow split browse+type \| shell+chat+idle+consolidate; CK 0.19; ITS rise ×4.8; I² 0.92 |
| [G30](goalperiod-subhypotheses/G30/README.md) | exploratory (regime I) | failed | t2\* 6.2 min [5.4, 7.2]; t2\*/N2 1.24; slow split shell+idle+consolidate \| browse+type+chat; CK 0.14; ITS rise ×4.2; I² 0.92 |
| [G31](goalperiod-subhypotheses/G31/README.md) | exploratory (regime I) | mixed | t2\* 6.3 min [5.6, 7.0]; t2\*/N2 1.28; slow split browse+type \| shell+chat+idle+consolidate; CK 0.20; ITS rise ×4.9; I² 0.89 |
| [G33](goalperiod-subhypotheses/G33/README.md) | exploratory (regime II) | mixed | t2\* 6.2 min [5.3, 7.3]; t2\*/N2 1.44; slow split browse+type \| shell+chat+idle+consolidate; CK 0.17; ITS rise ×3.7; I² 0.81 |
| [G35](goalperiod-subhypotheses/G35/README.md) | exploratory (regime II) | failed | t2\* 4.2 min [3.5, 4.9]; t2\*/N2 1.23; slow split shell+idle+consolidate \| browse+type+chat; CK 0.10; ITS rise ×4.3; I² 0.72 |
| [G37](goalperiod-subhypotheses/G37/README.md) | exploratory (regime III) | failed | t2\* 23.5 min [17.2, 30.0]; t2\*/N2 1.19; slow split browse+type+shell+chat+consolidate \| idle; CK 0.18; ITS rise ×4.8; I² 0.87 |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory (regime III) | failed | t2\* 10.1 min [9.0, 11.2]; t2\*/N2 1.16; slow split browse+type+consolidate \| shell+chat+idle; CK 0.17; ITS rise ×6.8; I² 0.78 |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory (regime III) | failed | t2\* 6.6 min [5.6, 7.8]; t2\*/N2 1.25; slow split shell+chat+idle \| browse+type+consolidate; CK 0.16; ITS rise ×5.5; I² 0.90 |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory (regime III) | failed | t2\* 9.2 min [7.8, 10.6]; t2\*/N2 1.16; slow split browse+type \| shell+chat+idle+consolidate; CK 0.32; ITS rise ×6.7; I² 0.90 |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory (regime III) | mixed | t2\* 8.4 min [7.0, 10.4]; t2\*/N2 1.33; slow split browse+type \| shell+chat+idle+consolidate; CK 0.28; ITS rise ×6.0; I² 0.89 |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory (regime III) | mixed | t2\* 5.8 min [5.1, 6.6]; t2\*/N2 1.40; slow split browse+type \| shell+chat+idle+consolidate; CK 0.18; ITS rise ×4.0; I² 0.83 |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory (regime III) | failed | t2\* 7.5 min [6.1, 8.7]; t2\*/N2 1.22; slow split browse+type \| shell+chat+idle+consolidate; CK 0.26; ITS rise ×5.2; I² 0.84 |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory (regime III) | mixed | t2\* 11.7 min [11.2, 12.4]; t2\*/N2 1.26; slow split browse+type+shell+chat+consolidate \| idle; CK 0.21; ITS rise ×5.1; I² 0.99 |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native (round 1b) | failed | forced erasures leave a transient that decays in ≈ 21 min (G51), 0.08 × the MSM's t2\*; none in G38 |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native (round 1b) | failed | t2\*_v3 456 → 63 → 428 min across the steps; ordinary 2-week blocks swing ×6–7 |

*Round 1b (2026-10-04):* every G folder has a `Verdict (1b): descriptive` line (Jev v3 soft-state replication; card D3) and a Round 1b section; G27 also carries the native change-point test (failed, p 0.31).

## Results
*Exploratory round 1, 2026-10-03; non-holdout days only; action-class states (H14 coarse 6-state minute grid). Scripts: `analysis/` (`synthetic.py`, `run_period.py`, `summarize.py`, `write_period_folders.py`, `confirm_h17.py`). Numbers: `data/processed/H17-behavior-metastable-sets/summary.json`, `G<NN>/result.json`, `synthetic/synthetic_rows.json`, `pooled_vs_agent.json`, `confirm/dryrun.json`. Figures: `summary/summary.pdf` (compendium page; observable figure `figures/summary_obs.pdf`), `figures/summary.pdf` (one-page analysis summary), `order_parameter.pdf`, `its_all_periods.pdf`, `agent_heterogeneity.pdf`, `stuckness_covariates.pdf`, `boundary_idle.pdf`, `g51_weekly.pdf`, `synthetic_validation.pdf`; per period `goalperiod-subhypotheses/G<NN>/figures/its_ck.pdf`.*

**Headline.** On action-class states, an MSM is a useful *description* (a few minutes of memory, a clean two-set split), but not a faithful *model*:
- the minute-scale chain is clearly non-Markov, so t2\* is a fixed-lag descriptor, not an intrinsic timescale;
- the slow "sets" are mostly tool modality (GUI vs. shell) and idling, and pooling heterogeneous agents inflates them;
- t2\* is a period-level quantity that differs between periods beyond noise, but it does not order periods by stuckness;
- regime III is *slower* than regime I, the reverse of the prediction.

### Synthetic validation (axis F; P1)
- **(i) Recovery.** Hard-state t2 at τ = 5 is unbiased at every village sampling tested: 12×3 to 27×45 agent-days, t2_true 3–120 steps, 36 to 80k inter-set crossings. Median ratio 0.98–1.10; agent-day bootstrap coverage ≈ 0.91 (0.77–1.0). The predicted downward bias for long t2 on 240-step days did **not** appear: MLE transition counts do not need long trajectories.
- **(ii) Sets.** PCCA+ recovers the planted partition in 90–100% of runs; the eigen-gap rule picks the planted m in 77–100%.
- **(iii) CK test.** The practical criterion (0.05) passes 90–100% of true Markov chains. But it catches a lumped hidden state only 17–27% of the time at t2 = 10 (97–100% at t2 = 30). The bootstrap-significance version has power ≈ 1 with 7–43% false failures. **A CK pass is weak evidence; the ITS rise is the better diagnostic** (≈ 1 for Markov chains vs. 2.3–4.3 for lumping).
- **(iv) N2.** Once the censored first and last runs of each day are kept in place (the first version moved truncated end-of-day runs mid-day and gave false positives), the sojourn null has 0% false positives on sticky-only R1 chains and 100% power on planted sets (t2/N2 = 3.4–7.5).
- **(v) Heterogeneity.** I² from block-bootstrap SEs: 0% false positives, 100% power at a 4× spread. The agent-day-bootstrap version had 40% false positives at 5 days. The pooled-vs-agent CK comparison and the held-out test were uninformative or underpowered, so they were demoted before the real-data run.
- **(vi) Soft states (for Jev).** With q = 10 and argmax accuracy 0.62 (κ ≈ 0.5), argmax labels give t2 at 0.07–0.24 of the truth at a 1-window lag, and soft counts 0.03–0.13. The shifted estimator C(1)⁻¹C(1+τ) gives 0.83–1.33.

### Outcome vs. prediction
| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 synthetic | (i) unbiased, but the predicted finite-day bias is absent; (ii) ✓; (iii) size ✓, power ✗ at moderate non-Markovianity; (iv) ✓ after the censoring fix; (v) ✓ with block SEs; (vi) ✓ | mostly holds; CK demoted to weak evidence |
| P2 Markovianity | plateau by 15 min in 1/8 regime-III periods; CK passes in 0/27 (max \|Δ\| 0.10–0.32); order 2 beats order 1 on held-out days in 27/27; ITS rise ×5.4 (III), ×4.5 (I) | **fails** |
| P3a t2\* > shuffle floor | 27/27 | holds (trivial) |
| P3b sets beyond sticky states (primary) | regime III: t2\*/N2 = 1.16–1.40, Holm p = 0.02 everywhere; ratio ≥ 1.25 in 3/8 (#41, #42, #51; #39 = 1.249) | **fails** (needed ≥ 4/8) |
| P3c m ∈ {2,3}, crisp, separated | m ∈ {2,3} 27/27; crispness ≥ 0.75 27/27; t2/t3 ≥ 2 in 8/27 | **fails** on timescale separation |
| P3d idle in its own set (regime III, pooled) | 2/8 (#37, #51). Within agents, idle is alone for 25–92% of regime-III agents | fails pooled; holds within agents (post hoc) |
| P3e 5 ≤ t2\* ≤ 60 min (III) | 8/8 (5.8–23.5 min) | holds |
| P4a periods differ | I² of ln t2\* across regime III = 0.96; between-period CV 0.55 vs. #51 between-week CV 0.17 | holds as stated, but driven by #37 (CV 0.22 with boundary idle trimmed) |
| P4b tracks stuckness | across III: ρ(t2\*, errors) = −0.43, ρ(t2\*, output) = −0.52 (n = 8, n.s.); within-period meta: ρ(errors) = −0.18 (p = 0.06, wrong sign), ρ(output) = −0.11 (p = 0.24) | **fails** |
| P4c regime I slower | median t2\* I 5.1 min vs. III 8.8 min; Mann–Whitney two-sided p = 2×10⁻⁵, **reversed**; per-agent medians 4.3 vs. 5.9 | **fails (reversed)** |
| P4d free periods not fastest | #31 is the *slowest* of 17 regime-I periods; #37 the slowest of 8 regime-III periods | holds; descriptive (n = 2) |
| P5 agent heterogeneity | I² ≥ 0.5 in 26/27 (median 0.84). Demoted clause: own/shrinkage beats pooled on held-out days for 93% of agents (median). Lab η² significant in 2/27 (chance) | holds |
| P6 committor asymmetry | max \|δ\| ≤ 0.037 in all regime-III periods | **fails**: between cores, the set-level dynamics at τ_c is close to detailed balance |
| P7 currents inside sets | σ(τ = 1) > N2 p95 in 7/8 (26/27 overall); σ_macro/σ_micro (m = 3) = 0.003–0.07 | holds |
| P8 MSM beats R1, M0 | 25/27 (fails #11, #37) | holds in most periods (predicted all) |
| P9/P9b/P9c holdout | not run; dry run on stand-ins works (#31: P9, P9b pass; P9c fails. #44: all fail) | pending |
| P10 NE07 / NE10 | NE07: t2\* 4.2 → 7.1 min, difference CI [+1.0, +4.9], **opposite** (idle share 0.21 → 0.36). NE10: +0.6 [−2.0, +3.0], null. NE17 (descriptive): +1.5 [−0.1, +3.6], idle 0.15 → 0.28 | **fails** |

### What the slow sets are
- **Pooled MSMs.** The commonest m = 2 split is **GUI work (browse + type) vs. shell/chat/idle/consolidate**: 18/27 periods, including 6/8 regime-III periods.
  - Early regime-I periods (#11–#13, #17–#19) split in-session computer work from out-of-session chat/idle.
  - #37 and #51 split idle from everything.
  - Fine action classes on the record sequence give the same picture: {click, scroll, look, type} vs. {shell, chat, consolidate, …}.
- **Agent mixture (R2, post hoc but within the pre-registered O7 comparison).** Pooled t2\* exceeds the median per-agent t2 by ×1.28 (median; 0.93–1.80; > 1 in 85% of periods), about the same size as the beyond-N2 excess (×1.25). Within agents, the slow set is idle alone for 25–92% of regime-III agents (73% in #41, 58% in #51), and GUI | shell for 8–71%.
  - So part of the pooled GUI-vs-shell mode is a difference *between* agents (GUI-heavy vs. shell-heavy), not switching *within* agents.
  - **Round 2 should use per-agent or partially pooled MSMs as primary.**
- **Boundary idling (post hoc).** In #37, 80% of idle minutes are leading or trailing idle runs of agent-days (agents present but not yet acting, or done for the day). Trimming them cuts t2\* from 23.5 to 8.5 min. Elsewhere this barely matters (regime-III median share 23%, trimmed median t2\* 8.5 vs. 8.8 min).
- **Irreversibility** lives inside the sets, in the fast work cycles. MSM σ per minute is 0.006–0.09 nats in regime I (0.07–0.11 in regime II) vs. 0.002–0.02 in regime III, consistent with H09 E2's collapse after perma-computer-use (H14 owns the EP estimates). Committors between the two cores are symmetric (|δ| < 0.04).

### Order parameter?
t2\* is well estimated (agent-day 95% CIs ±5–27%) and stable within a period (half-days ×0.96; #51 weeks 10–17 min, CV 0.17). It differs between periods beyond noise, but:
- the spread among regime-III periods is mostly #37's boundary idling;
- regime III (perma-computer-use) is slower than regime I (5–6 min, set by the session on/off and tool-mode switching);
- it does not follow error share or output, across or within periods;
- the free-choice periods are the slowest of their regime. That fits "undriven = slow mixing", but n = 2.

On action classes, t2\* measures how long agents stay in a tool modality or idle, not whether they are stuck.

### Caveats
- **States.** Six action classes cannot see content-level traps (#45's "temporal bleed" spiral, debugging loops that look like ordinary shell work). The minute-grid idle state mixes declared pauses, LLM latency gaps and pre-start/post-stop minutes.
- **Non-Markov.** t2\* depends on the lag (×4–7 between 1 and 15 min), so it is a fixed-lag descriptor; comparisons are only meaningful at the same τ_c.
- **Pooling.** Pooled MSMs mix agents (R2). The pre-registered primary statistics are pooled, which inflates t2\* and sets.
- **Statistics.** The P3b ratio threshold (1.25) is arbitrary and #39 sits on it. The agent-day bootstrap ignores cross-agent dependence within days. With 8 regime-III periods, across-period correlations are descriptive.
- **NE splits** are confounded with day of week and goal phase, and the before windows are tiny (#30: 1 day; #21: 3 days).
- **Regime contrast** is confounded with goal content, roster size and hours.
- **Not blind.** Before writing predictions I saw H14's scheme audit (class mix) and H09's results; P6 was not blind. The boundary-idle trim, the per-agent-median comparison and the GUI/shell reading are post hoc.

### What the Jev states should add
1. Content-level behavior (meta/existential talk, debug_recover, blocked, idle_monitor), which can test whether slow sets are behaviors rather than tool modalities. This is the only way to see theory spirals.
2. Soft probability vectors, analysed with the **shifted estimator**: argmax labels at κ ≈ 0.5 would underestimate t2 by 4–14× at a 1-window lag, and soft counts are worse.
3. A stuckness covariate (`blocked` probability) that is independent of the state.
4. A per-agent design. 10 states per agent need ≈ 300+ windows, so per-agent Jev MSMs are feasible only in #38 and #51; elsewhere use partial pooling.

The P9-Jev pre-registration must be written in this card before `confirm_h17.py --jev` can run on the holdout.

## Notes
- 2026-10-03: promoted from HH97.
- 2026-10-03: H14's state builder appeared while this round was being set up; H17 imports it (`build(days)`) instead of writing a duplicate, and freezes its own copies of the state tables. Two hypotheses now use it, so it should move to `infra/` (proposed to the coordinator, not done here).
- 2026-10-03: the sojourn null's first version moved censored end-of-day runs mid-day (false positives on R1 chains in synthetic tests); fixed before the real-data run. N3 (semi-Markov) pools excluded censored runs, which dropped the long boundary idle spells and gave N3 ≈ the shuffle floor in #37; fixed to keep first/last runs in place, like N2.
- 2026-10-03: the shifted estimator is for classifier posteriors (independent noise per window). On action-composition vectors it diverges (t2 → 10²–10¹⁵ min) and is reported as n/a.
- 2026-10-03: `confirm_h17.py --confirm` refuses to run if H14's `build_states.py` no longer matches the sha256 recorded in `_provenance.json` (fa38ca6d…), so holdout states are built by the same code as the exploratory ones.
- 2026-10-03: period folders moved to `goalperiod-subhypotheses/G<NN>/` (coordinator); scripts and links updated.
- 2026-10-03: #39's ratio is 1.249 with 400 surrogates and 1.251 with 100; the 400-surrogate value is used (verdict: failed).
- Compute: ≈ 45 min wall of ≤ 2 local processes (synthetic 4 min; 27 periods 13 min, dominated by #51; extra N2 surrogates ≈ 20 min including a restart). Disk: 10 MB in `data/processed/H17-behavior-metastable-sets/`, 1.8 MB in this folder.

## Round 1b (improved data, 2026-10-04)
*Re-evaluation on the improved data (Vivian's priority 2; `infra/data-quality/QUEUE.md`, two-layer design). Holdout untouched; no confirmatory run. Code: `analysis/v3lib.py`, `analysis/synthetic_v3.py`, `analysis/round1b.py`, `analysis/native_r1b.py`; numbers in `data/processed/H17-behavior-metastable-sets/r1b/`.*

### What changed in the inputs
- **Jev behavior states v3.1** (`behavior_states_v3.parquet`, DQ3): every non-holdout agent × 5-min window, 11 states with probability vectors, plus `p_blocked` and assembly flags. This is the second state space the card was waiting for. Inactive windows inside an agent's daily span are kept as an explicit `absent` state ("idle by absence"); windows outside the span are dropped (which also removes round 1's boundary idling by construction).
- **Stuckness covariates:** round 1's error share counted `actions.error`, which is "stderr non-empty" (58% of flagged bash turns are not failures). Replaced by real failures (`n_errors` / `turn_outcomes.failed`), plus `p_blocked`, git-printed commits and pushes (`n_commit_ok`, `n_push_ok`), `longest_run` and `repeated_error_share`.
- **Unchanged:** the action-class states (H14's builder reads `actions` + `events_core`, untouched by the `activity_bins` event-drop bug; `bash_head` is not used in the 6 coarse classes). Round-1 action-class t2\*, CK, N2 and verdicts therefore stand as computed; only their covariate correlations are re-run.

### Synthetic checks of the soft-state tools (axis F; run before any v3 statistic)
`analysis/synthetic_v3.py` (parts 1 and 2; `r1b/synthetic_v3*.json`). Jev-like soft vectors (argmax accuracy 0.6), village sampling.
- **Shifted estimator** C(1)⁻¹C(1+τ): unbiased at ~100k windows (q = 6: ratio 0.94–0.98; q = 12: 0.78–1.03), but biased up ×1.6–2.7 at 3,600 windows (q = 6; a 4-h period) and broken at q = 12 below ~15k windows (λ₂ → 1). A bootstrap bias correction on λ₂ brings q = 12 at 14,400 windows to ×1.13–1.32.
- **Soft CK** (C(k) vs C(1)K(1)^(k−1), set level): passes Markov chains (100%) and lumped (non-Markov) chains alike (97–100%). **No power.**
- **Soft N2** (argmax runs carrying their vectors): false positives on sticky-only chains in 57% (3,600 windows) to 100% (115k) of runs, because label noise splits hidden dwells. **Not a valid R1 null for soft states.**
- **ITS rise** does not separate Markov from lumped chains at these sample sizes.

### Design decisions (written 2026-10-04, after the synthetic checks, before any v3 real-data statistic)
*What I had seen of the v3 data before writing this:* DQ3's documentation (state mix and `p_blocked ≥ 0.5` shares by regime); per-period counts of in-span, absent, post-reset and forced-reset windows; per-period mean `p_blocked` and real-failure share (printed in a structural check; no t2, MSM or correlation computed).
- **D1, state space.** A named 6-state lumping of the Jev states: **work** = execute_task; **inquire** = research_browse + verify_report; **fix** = debug_recover; **talk** = plan_coordinate + communicate_external + social + meta; **wait** = monitor_wait + idle + absent; **maint** = self_maintenance. States below 1% of a period's mass merge into `rare`. The full 12-state MSM (11 Jev + absent) runs only in G51 (≥ 100k windows), as a check.
- **D2, order parameter.** t2\*_v3 = shifted-estimator t2 at τ = 1 window (5 min, the round-1 τ_c), τ₀ = 1 window, with an agent-day bootstrap CI and the λ₂ bias correction (t2\*_bc). **Cross-period comparisons use t2\*_eq**: the median over 50 random sets of agent-days totalling ≈ 3,000 in-span windows, so every period carries the same small-sample bias.
- **D3, verdicts.** By P1's falsifier rule, soft P3b (N2) and the soft CK are reported descriptively. The per-period replication on v3 is therefore **descriptive** in every period (`Verdict (1b)` lines say so); round-1 action-class verdicts stand. Card-level questions (P4b stuckness, P4c regime contrast) are answered with t2\*_eq.
- **D4, covariates** (per period and per agent, labelled windows): real failure share Σ n_errors / Σ n_actions; mean `p_blocked`; output rate = (git-printed commits + pushes) per in-span hour; mean `longest_run`; mean `repeated_error_share`.

### Predictions (round 1b; written 2026-10-04 before running)
- **P4b-1b (primary: does t2\* or `p_blocked` flag stuck periods?).**
  - (i) Across the 8 regime-III periods: ρ(t2\*_eq, mean p_blocked) > 0 and ρ(t2\*_eq, output rate) < 0 (descriptive, n = 8). Across all 27 periods, the regime-stratified Spearman (ranks demeaned within regime) of t2\*_eq on p_blocked has p < 0.05. Credence 0.35 / 0.3.
  - (ii) Within periods, per-agent meta (agents with ≥ 300 transitions and ≥ 2 days): Fisher-z ρ(t2_i, p_blocked_i) > 0 with p < 0.025. Credence 0.35.
  - (iii) Round-1 action-class t2\* against the real failure share: ρ > 0 across regime III (round 1 had ρ = −0.43 against stderr). Credence 0.3.
  - (iv) `p_blocked` itself flags stuck periods: across the 27 periods, ρ(mean p_blocked, real failure share) > 0.4 and ρ(mean p_blocked, output rate) < −0.3. Credence 0.6 (partly mechanical: Jev saw the failures).
- **P4c-1b.** Regime-I t2\*_eq > regime-III t2\*_eq (Mann–Whitney p < 0.05): the round-1 prediction, reversed on action classes. Credence 0.4.
- **P3d-1b.** In the m = 2 PCCA+ split of the soft transition matrix, `wait` sits alone (or with maint) in ≥ 50% of regime-III periods. Credence 0.6.
- **P5-1b.** Per-agent I² of ln t2 ≥ 0.5 wherever ≥ 3 agents qualify. Credence 0.6.
- **P8-1b.** The argmax MSM beats M0 and R1 on held-out days at τ = 1 window in ≥ 75% of periods. Credence 0.7.
- **G51 check.** t2\*_bc on 12 states is within a factor 2 of t2\*_bc on the 6 macro states. Credence 0.6.

### Native tests (layer 2; predictions written 2026-10-04 before running; `analysis/native_r1b.py`)
- **N1, NE41 forced erasures as quasi-random kicks (G51 primary, G38 secondary; axis D/E).** After a forced erasure (`context_ledger_turns.reset_forced`, the 41-turn cap, so the timing is set by the scaffold), the mean macro-state vector in windows k = 1…4 relaxes toward the period mean. **Unfitted MSM prediction:** the TV distance d(k) decays with time constant τ_relax = −5 min / slope(ln d(k) on k) within [0.5, 2] × t2\*_bc of the same period. Control: anchor windows on the same agent-days with no consolidation in the previous window. Events are censored at the next consolidation (forced or voluntary) or the end of the segment. Credence 0.7 that the erasure leaves a measurable transient (d(1) above the control's, bootstrap CI over agent-days); 0.35 for the factor-2 agreement.
- **N2, NE43 drive withdrawal inside #51.** t2\*_v3 on A = 07-24 → 08-04 (bookends and nudges), B = 08-05 → 08-20 (nudges only), C = 08-21 → 09-02 (neither). Prediction: t2\*(C) > t2\*(A), agent-day bootstrap 95% CI of the difference above 0, and mean p_blocked higher in C than in A. Same-length placebo contrast inside 07-06 → 08-04 reported for scale. Credence 0.35.
- **N3, #27 spontaneous rivalry → collaboration (no operator change).** On day-level soft macro-state transition counts, the best single change point (between days 2 and 8 of 10) beats a day-order permutation null (1,000 permutations, p < 0.05), and the talk share is higher after it. Credence 0.3.

### Results (round 1b, run 2026-10-04)
*Numbers: `r1b/G<NN>.json`, `r1b/summary_r1b.json`, `r1b/native_r1b.json`, `r1b/synthetic_v3*.json`. Figure: `figures/r1b_summary.pdf`. Compute: ≈ 25 min of ≤ 2 local processes.*

**Old vs new, regime III** (action-class t2\* from round 1; v3 = 6 macro states, shifted estimator, τ = 5 min; failure shares are per computer-use turn):

| Period | t2\* action classes (r1) | t2\* v3, raw / equal-n (1b) | stderr share (r1 covariate) | real-failure share (1b) | mean p_blocked | m = 2 split (v3) |
| --- | --- | --- | --- | --- | --- | --- |
| G37 | 23.5 | 192 / 192 | 0.063 | 0.028 | 0.26 | wait \| rest |
| G38 | 10.1 | 230 / 231 | 0.058 | 0.030 | 0.25 | wait \| rest |
| G39 | 6.6 | 598 / 258 | 0.085 | 0.024 | 0.20 | inquire+fix+maint \| work+wait |
| G40 | 9.2 | λ₂ ≈ 1 (unidentified) | 0.174 | 0.026 | 0.22 | work \| rest |
| G41 | 8.4 | 122 / 131 | 0.141 | 0.051 | 0.23 | wait \| rest |
| G42 | 5.8 | 220 / 219 | 0.075 | 0.034 | 0.24 | talk+wait \| rest |
| G44 | 7.5 | 38 / 38 | 0.105 | 0.047 | 0.26 | wait \| rest |
| G51 | 11.7 | 268 / 160 (t2\*_bc 263) | 0.058 | 0.027 | 0.25 | wait \| rest |

Regime I: t2\*_eq 16–227 min (median 40) against 4–6 min on action classes. Real failures are 30–85% of the stderr share; the two correlate across periods (ρ = 0.71).

**Outcome vs prediction (round 1b):**

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P4b-1b (i) t2\* tracks stuckness across periods | regime III: ρ(t2\*_eq, p_blocked) = −0.69 (p 0.06), ρ(t2\*_eq, output) = +0.31, ρ(t2\*_eq, real failures) = −0.74 (p 0.04); all 27 periods, regime-stratified ρ(t2\*_eq, p_blocked) = −0.49 (p 0.03) | **failed (wrong sign)** |
| P4b-1b (ii) within periods | per-agent meta ρ(t2_i, p_blocked_i) = −0.28 (p 0.03, 7 periods, 79 agents); real failures −0.18 (p 0.16); output ≈ 0 | **failed (wrong sign)** |
| P4b-1b (iii) action-class t2\* vs real failures | regime III ρ = −0.19 (stderr: −0.43); within-period meta +0.05 (p 0.43; stderr +0.04) | **failed**: the covariate fix does not rescue the order parameter |
| P4b-1b (iv) p_blocked flags stuck periods | all 27: ρ(p_blocked, real failures) = **−0.64** (p 3×10⁻⁴), ρ(p_blocked, output) = −0.78 (p 2×10⁻⁶); regime III: +0.43 (n.s.) and −0.71 (p 0.05) | **mixed**: p_blocked tracks regime (regime I "waiting on others") across all periods; inside regime III it marks low-output periods |
| P4c-1b regime I slower | median t2\*_eq I 40 min vs III 205 min, Mann–Whitney p 0.013 | **failed (reversed again)** |
| P3d-1b wait in its own set | 5/8 regime-III periods (15/27 overall); G51 12-state split {idle, absent} \| rest | **holds** |
| P5-1b I² ≥ 0.5 | 2/7 periods with ≥ 3 eligible agents (G20 0.61, G51 0.62) | **failed** (per-agent v3 MSMs are noisy at ≤ 800 windows) |
| P8-1b argmax MSM beats M0 and R1 | 9/27 | **failed** |
| G51 12 vs 6 states | t2\*_bc 479 vs 263 min (×1.8) | holds |
| N1 NE41 relaxation (native) | G51: forced erasures leave a transient (maint +0.07 in the erasure window, work +0.11 one window later; d(1) above control, CI [0.10, 0.14]) that decays with τ_relax ≈ 21 min, **0.08 × t2\*_bc**; G38: transient (CI [0.05, 0.10]) with no decay | transient holds; **the MSM prediction fails** |
| N2 NE43 (native) | t2\*_bc A 456, B 63, C 428 min; C − A CI unbounded; mean p_blocked C − A −0.02. Placebo (07-06…07-14 vs 07-15…07-23): 465 vs 78 min | **failed**; t2\* swings ×6–7 between ordinary 2-week blocks |
| N3 #27 change point (native) | best split before 01-22 (days 9–10 vs 1–8; LR 31), day-order permutation p 0.31; talk share 0.018 → 0.030 | **failed** |

**Reading.**
1. **On semantic states the slowest mode is hours, not minutes, and it is not stuckness.** Once window-level label noise is cancelled, t2\* sits at roughly a day length (G38: a flat ITS plateau at ≈ 225 min, CI ±7), or the estimator finds nothing slower than ~30 min; across periods it is bimodal. A mode that lives as long as an agent-day is the agent/day mixture (rival R2 with R3), not a metastable behavior.
2. **The slow split is still acting vs waiting.** `wait` (monitor_wait + idle + absence) is a set of its own in 15/27 periods; with 12 states, {idle, absent} against everything. Debugging, meta talk and planning never form sets of their own. Rival R4 (the timer/idle state) wins on semantic states as it did on action classes.
3. **Neither t2\* nor p_blocked is a stuck-period monitor across regimes.** Higher p_blocked goes with *shorter* t2\* within periods. p_blocked is a regime marker (regime I's "waiting on others"); only inside regime III does it line up with low output (ρ −0.71, n = 8).
4. **The MSM does not predict the response to the scaffold's kicks.** Forced erasures (quasi-random in timing) leave a one-window re-orientation signature that is gone in ~20 min, an order of magnitude faster than t2\*. Caveat: the control anchors are mid-segment calls, so both curves carry censoring selection after k ≈ 2.

**Verdict changes.** None for the round-1 per-period verdicts (their inputs did not change). The v3 replication is descriptive in every period (D3; `Verdict (1b)` lines). Card level: the HH97 claim, a mixing time that orders periods by stuckness, is now refuted on both state spaces; H17-R1 (soft Jev MSM recovers slow cognitive modes) is not supported.

**Scorecard (round 1b; round 1 in brackets).** A 1 [1]: v3 states and the absent state are explicit, but `p_blocked` changes meaning across regimes. B 0 [0]: soft CK has no power, and t2\* swings ×6–7 between ordinary 2-week blocks of #51. C 1 [1]: rests on round 1's action-class MSM; on v3 the argmax MSM beats R1 in only 9/27 and soft P3b is not identifiable. D 0 [0]: the unfitted relaxation after forced erasures misses by ×12. E 0 [0]: NE41, NE43 and #27 tested; no predicted change. F 1 [1]: the synthetic checks show the v3 MSM is not identifiable at 4-h-period sizes (stated, not hidden). G 1 [1]: slow sets match known structure (waiting, scaffold). H 1 [1]: R4 and R2/R3 explain the slow modes. I 0 [0].

**Shared-file suggestions** (not made; outside this card's scope): `infra/README.md` known issue: *"Soft-label MSMs need ≥ ~15k windows per period: the shifted estimator C(1)⁻¹C(2) breaks down (λ₂ → 1) below that at q = 12 and is biased ×1.6–2.7 at 3,600 windows (q = 6); a sojourn null on argmax runs of noisy labels gives 57–100% false positives (H17 round 1b)."* `DEFINITIONS.md`: add "Markov state model (soft, shifted estimator)" as a named variant.

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** A Markov state model on action classes recovered tool modes, i.e. the scaffold.
- **What the direction is really after:** What are the metastable cognitive modes (planning, building, debugging, existential talk), and what switches them?
- **H17-R1.** A soft Jev-state MSM recovers slow cognitive modes, and switches are driven by external input.
- **H17-R2.** Debugging is the slowest mode and the main sink of time.
- **H17-R3.** Mode switches synchronize across agents only through shared artifacts (E3).
