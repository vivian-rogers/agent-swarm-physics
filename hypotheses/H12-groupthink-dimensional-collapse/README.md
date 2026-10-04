# H12: Groupthink is dimensional collapse: few collective modes, shrinking participation ratio at consensus

**Status:** running. Exploratory round 1 done 2026-10-03: HH77 partially supported (one Curie–Weiss-like market mode, partly joint lulls); HH58 refuted in direction (kickoffs expand dimensionality; self-repetition, not consensus, collapses it). Confirmatory script written, not run.
**Plain-language explainer:** [EXPLAINER.md](EXPLAINER.md) (for non-specialists).
**Fields:** stat mech, info theory
**Origin:** HH77 + HH58 (shortlist 2, item 3) (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used:** Population N(t), variant *present population* (H02 rule, below); Regime (whitening is per regime); Agent state, variant *vector* (centered, whitened mean embedding of the agent's statements in a 30-min window); Driving / external field (goal kickoffs). Two new named variants are proposed for `DEFINITIONS.md` (not yet added; H12 may not edit it): **"collective eigenmode (random-matrix)"**, to avoid a clash with the "collective mode" of `statmech-primitives.md` (coordinating / executing / idling / reporting, HH56), and **"effective dimensionality (bias-corrected participation ratio)"**.

## Question
How many collective modes does the swarm have beyond random-matrix noise, and does the effective dimensionality of what agents say collapse after kickoffs and during consensus, then re-expand in free weeks? Practical payoff: a cheap, model-free monitor of whether a swarm is 'thinking alike'.

## Model
**From:** `physics-models/01-inverse-ising` and `physics-models/11-vector-spins` with random-matrix theory: Marchenko–Pastur edges for N×T correlation matrices (activity or talk spins per minute; content time series per window), and the participation ratio PR = (Σλ)²/Σλ² of the swarm's whitened embedding covariance per window. The top mode is compared with H02's Curie–Weiss collective co-activation.
- **Model 01 reading.** For equal-time ±1 spins the susceptibility matrix is χ = C (model 01, "Susceptibility"). Its eigenvalues above the noise edge are the swarm's soft collective modes. A Curie–Weiss swarm (H02-MF) has exactly one, with a uniform eigenvector and eigenvalue ≈ 1 + (N−1)ρ̄ = the variance ratio VR. A block (rooms, families) structure adds one mode per block contrast.
- **Model 11 reading.** For vector spins s_i(t) ∈ ℝ^d, the equal-time overlap matrix Q_ij = ⟨s_i·s_j⟩_t / d is the analogue of C. Its signal eigenvalues are collective directions of co-movement in content. The participation ratio of the swarm's content covariance is the "effective dimensionality" macrostate of `statmech-primitives.md` (HH58).
- **Random-matrix reference.** For N independent series with T effective samples, the eigenvalues of C fill the Marchenko–Pastur bulk with edge λ₊ = (1 + √(N/T))². Autocorrelation shrinks T_eff, and the daily schedule adds a shared field. So the working edge is empirical: the 95th percentile of the top eigenvalue under surrogates that keep each agent's own series and schedule but break same-day alignment.

## Data scheme (`scheme/`)
- **Inputs:** `data/processed/shared/activity_bins.parquet` (pt_date, minute, agent, state), `calendar.parquet`, `roster.parquet`, `rooms_timeline.parquet`, `embeddings/statements.parquet` + `embeddings/chat_bge_small.npy` + `embeddings/intentions_bge_small.npy`, the per-regime whiteners (`common.load_whitener`), goal modes parsed from `hypohypotheses/goal-periods.md`. No raw tables.
- **Transform** (`scheme/build.py`):
  - **Units.** Goal periods, split at H01's catalogued step changes (same split dates, for comparability): #36 at 03-24 (36a regime II, 1 day; 36b regime III), #38 at 04-14 (NE17) and 04-20 (NE18), #51 at 07-09 (NE32), 08-05, 08-25 (#focus) and 09-03 (NE33). Holdout days are dropped with a hard assertion (`calendar.holdout` and `holdout_mask` must agree).
  - **Present population** (activity): agents with an `activity_bins` row on every day of the unit and ≥ 30 active bins (H02's rule).
  - **Statements:** each agent's own chat messages and intentions (the shared instrument). Each statement is whitened with its regime's whitener, d = 32 (64 as a variant), stored as fp16 (no text).
- **Output:** `data/processed/H12-groupthink-dimensional-collapse/`: `units.parquet`, `spins.parquet` (unit, day, minute, agent, state), `stmt_white.parquet` + `stmt_white_d64.npy` (non-holdout statements only), per-unit result tables in `G<NN>/`, synthetic results in `synthetic/`, `_provenance.json`.
- **Regimes covered:** I, II, III. Whitening is per regime (a shared ruler, exception (a) of the unit-of-analysis rule), so dimensionality is only compared within a regime.

## Candidate goal periods
Every non-holdout goal period with N ≥ 10 (#23, #24, #25, #26, #27, #30, #31, #33, #35, #36, #37, #38, #39, #40, #41, #42, #44, #51 head); consensus events #19, #31, #40; kickoffs (NE34); free weeks #11, #16, #31, #37 vs shared-objective weeks.

## Links to other hypotheses
Complements H10 (field response) and H01 D3.1 (order parameter). A monitor version can be run on any swarm log.
- **Not duplicated from H01:** polarization, alignment with ĝ, meaning-cluster entropy, the field-vs-coupling decomposition of pairwise alignment (P5/P6), and the mean-field O(n) fit (P9). H12 measures the *spectrum* (how many directions) rather than the *alignment* (how much along one direction).
- **H02:** the top activity eigenmode is compared with H02's Curie–Weiss βJ₀ and VR, chunk by chunk.
- **H05:** the room mode in talk spins is the spectral counterpart of H05's within-room > cross-room talk coupling. H05's warning that within-day circular shifts manufacture structure is the reason the cross-day surrogate is the primary null here.

## Observables
**(a) Random-matrix arm (HH77)**, per unit:
1. **Activity spins:** s_i(t) = +1 if state ≥ 3 (act or talk) else −1, 1-min bins, present population, standardized per agent over the unit. Equal-time correlation matrix C (N × N), eigenvalues λ₁ ≥ … ≥ λ_N (Σλ = N).
   - **k_cd** = the number of eigenvalues above the cross-day edge (95th percentile of λ₁ over 200 cross-day surrogates). Primary count.
   - k_MP (naive Marchenko–Pastur edge, T = number of bins), k_MP,eff (edge with T_eff = T / τ_B, τ_B = 1 + 2 Σ_{τ=1}^{60} mean_{i<j} ρ_i(τ)ρ_j(τ), Bartlett), k_circ (within-day circular-shift edge; secondary, never decides).
   - λ₁/edge; top-eigenvector sign uniformity (share of agents whose loading has the majority sign) and IPR = Σv⁴; uniform-mode share VR/λ₁, where VR = uᵀCu for u = 1/√N (Rayleigh bound: VR ≤ λ₁, equality iff the top mode is the Curie–Weiss uniform mode).
   - **Lull dependence:** λ₁/edge after dropping bins with ≤ 1 active agent (H02's joint lulls), surrogates filtered identically.
   - **Block-demeaned variant:** each agent's 30-min block means removed before C (H02's N1/MF convention), for the chunk-by-chunk H02 comparison.
2. **Talk spins:** s = +1 if state = 4, same pipeline. Agents with < 10 talk minutes in the unit are dropped from the talk matrix.
3. **Content:** for agent i and 30-min window t (`win30`), x_i(t) = mean over its statements of (w − μ_{i,kind}), where w is the whitened statement vector (d = 32) and μ_{i,kind} is agent i's unit mean for that statement kind (chat or intention). Kind-centering removes the chat/intention composition axis. Windows with no statement → 0. Each agent's series is scaled to unit mean squared norm per dimension. Overlap matrix Q = (1/(T d)) Σ_t Z(t)Z(t)ᵀ. Same counts (k_cd etc.), cross-day surrogates aligned by window index. Content agents: ≥ 1 statement on ≥ 80% of the unit's days and in ≥ 20% of its windows.
4. **What the modes load on** (descriptive): loadings of every signal eigenvector against room (time-weighted modal room in the unit), lab (`roster.lab`) and activity level; label-permutation p-values.

**(b) Dimensionality arm (HH58)**, chat statements, whitened d = 32:
5. **PR30**, per 30-min window: pool the window's chat statements, cap each agent at 8 (random subsample), rarefy to n = 30, compute the bias-corrected participation ratio, and average over 20 draws. Windows with < 30 statements after capping are missing.
   - *Bias correction:* with S the sample covariance (ν = n − 1 degrees of freedom), W = νS; under a Gaussian (Wishart) model E[(tr W)²] = ν²a + 2νb and E[tr W²] = νa + ν(ν+1)b, with a = (tr Σ)² and b = tr Σ². Solve for unbiased â, b̂; PR = â / b̂ (clipped to [1, d]).
   - Co-observables on the same draws: **TV** = tr S (semantic spread; PR is shape, TV is size) and **erank** = exp(entropy of S's normalized eigenvalues).
6. **PRday**, per active day (agent-balanced, the ruler for comparing days and periods): m = 6 agents with ≥ 15 chat statements that day, 15 statements each, bias-corrected PR of the 90 pooled statements, averaged over 50 draws of agents and statements. Days with < 6 eligible agents are missing.
7. **First hour after kickoff**, PR₁ₕ = mean PR30 over windows 0 and 1 of the day (the kickoff always precedes day 1's window; H04).
8. **Between-agent PR** (secondary): PR of the between-agent covariance of agent-day means, made unbiased by split-quarters (tr C_ab · tr C_cd / tr(C_ab C_cd) over random 4-way splits of each agent's statements). Bounded by N − 1.

## Null / baseline
Weakest to strongest; a mode or a collapse is claimed only against the strongest applicable null.
- **Independent stationary noise:** the naive Marchenko–Pastur edge (eigenvalues); PR at n statements drawn from the regime's corpus (dimensionality).
- **Autocorrelation:** the T_eff-corrected MP edge.
- **Schedule (shared time-of-day field) + each agent's own autocorrelation and daily profile:** the **cross-day surrogate**, primary. Each agent's day series is replaced by the same agent's series from another day of the same unit, aligned by minute (or window) of the day's active window. Day assignment is a cyclic offset per agent, balanced across agents. Shorter source days wrap circularly. About 1/D of agent pairs keep their true alignment in a surrogate, so the null is conservative (less power, not more false positives). The within-day circular shift is secondary only: H05 showed it manufactures structure when daily profiles differ.
- **Joint lulls / platform stalls** (H02): the lull-filtered recomputation.
- **Statement count, composition and dominance** (dimensionality): fixed n, chat only, a per-agent cap, agent-balanced PRday.
- **Placebo kickoffs** (NE34): the same first-hour contrast between consecutive days *inside* a unit (no goal change).
- **Same-regime ruler:** periods are compared only within a regime, at fixed n and m.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:**
- R0, independent agents (MP);
- R1, schedule-only (cross-day surrogate: a shared time-of-day field, no same-day co-fluctuation);
- R2, Curie–Weiss single uniform mode (H02-MF);
- R3, sampling artifacts for PR (statement count, chat/intention mix, one dominant agent);
- R4, "consensus formation" (PR high on day 1 and falling through the week), against "field quench" (PR lowest right after the kickoff, then re-expanding). They predict opposite day-1 slopes.

**Locked holdout used for confirmation:** none. `analysis/confirm.py` is written and not run. It refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`; `--dry-run` works on non-holdout stand-ins. The predictions it tests are in Amendment 2.

Scored after exploratory round 1, separately for the two mappings: (a) the random-matrix arm, a collective eigenmode of the activity, talk and content correlation matrices, and (b) the dimensionality arm, bias-corrected PR of chat content.

| Axis | Test | Score (a) RMT | Score (b) PR | Evidence |
| --- | --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | 1 | All variables come from `activity_bins` and whitened `statements` embeddings, and the assumptions are listed. Invariance is limited: whitening is per regime; activity spins change meaning at the 03-24 regime boundary; PR is confounded by self-repetition (post hoc). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | 1 | Units are split at step changes. The cross-day null keeps each agent's schedule and autocorrelation. There is no split-half stationarity test. Joint lulls (≤ 1 active agent) make up 0–42% of bins and are nonstationary. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | 0 | (a) One mode beats MP, T_eff-MP and the cross-day (day-blocked) surrogate in 22/24 units, but survives the lull filter in only 14/24 (9/11 low-lull units). (b) No PR contrast beats its placebo or ruler: P6 p = 0.86, P9 p = 0.58. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | 0 | (a) The Curie–Weiss signature was predicted and found: a single uniform mode, majority-sign share 1.0, VR/λ₁ median 0.97 (predicted ≥ 0.7), ranking like H02's βJ₀ (ρ = 0.73). The auxiliary "MP inflated" claim failed (7/24). (b) P10, the arms' agreement, failed: ρ = +0.36 and +0.15. |
| E interventional | predicts the change across a natural experiment | 0 | 0 | (a) Not tested across an NE. (b) NE34 kickoffs: the predicted collapse is absent. The change is +7% (regime III +44%), and day 1 is *higher*-dimensional in 13/16 periods. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | 1 | Synthetic recovery used village N, T and sparsity. Cross-day false positives are 6–10%; circular shifts give 70% false positives under heterogeneous profiles; one mode at a = 0.25–0.3 is recovered with ≥ 93% probability. The sparse family mode is never recovered. The lull filter loses power when lulls are long (post hoc A5). The bias-corrected PR is validated; naive PR and between-agent PR are biased. Robust to d = 8 and chat-only content. No embedding-model swap or bin-width variation was run. |
| G ground truth | agrees with known structure | 0 | 0 | (a) The room mode was not above the edge (3/10 two-room units), although rooms separate sub-edge talk eigenvectors in 8/10. (b) The named consensus weeks did not decline (only #31). |
| H comparative | beats the named rivals | 1 | 0 | (a) Beats R0 and R1 and agrees with R2 (Curie–Weiss, one uniform mode), but is not separated from joint lulls. (b) R3 (looping/templating) explains the lowest-PR periods; R4 beats the field quench on day 1. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | 0 | Holdout not run. (a) Holds across modes and regimes (22/24), but that is not a holdout test. |

## Prediction
*Written 2026-10-03, before running any H12 statistic on real data.*

**What I had seen when writing this:**
- The round-1 results of H02 (pairwise activity couplings at the noise floor; Curie–Weiss βJ₀ up to 0.55, significant in 13/21 chunks but only 5/21 after removing joint lulls; the forward P(K) fails), H05 (within-room talk coupling > cross-room in 6/6 regime-III windows; circular shifts invalid), H04 (kickoffs change what agents do, not how much) and H01's predictions (no H01 results).
- Sampling-design counts only:
  - N and active days per non-holdout period;
  - median activity and talk fractions per period;
  - statements per agent-window (median 8 / 7 / 3 in regimes I / II / III) and per swarm window (median 68 / 94 / 78, about 58–80% chat);
  - kickoff lead times before day 1's window.
- No eigenvalue, participation ratio, spread or content statistic had been computed on real data.

**Units scored:** the non-holdout units with N ≥ 10 at the period's start: 23, 24, 25, 26, 27, 30, 31 (regime I); 33, 35 (II); 36b, 37, 38a, 38b, 38c, 39, 40, 41, 42, 44, 51a–51e (III). That is 23 units. #19, #11 and #16 (N = 7) enter only P7–P9. 36a (one day) is descriptive.

**(a) Random-matrix arm (HH77): "a few collective modes beyond random-matrix noise".**
- **P1, few activity modes.** k_cd ∈ {1, 2, 3} in ≥ 2/3 of the scored units, and k_cd = 0 in ≤ 1/6. The naive MP count is inflated by autocorrelation: k_MP ≥ k_cd + 1 in ≥ 1/2 of units.
  *Falsifier:* k_cd = 0 in > 1/3 of units (no collective structure beyond the schedule), or k_cd ≥ 4 in > 1/3 (not "a few").
- **P2, the market mode is the Curie–Weiss mode, and it is partly lulls.** In units with k_cd ≥ 1:
  - the top eigenvector has majority-sign share ≥ 0.8 and uniform-mode share VR/λ₁ ≥ 0.7 in ≥ 2/3 of them;
  - median λ₁/edge is higher in regime III than in regime I (H02: III-C strongest);
  - removing joint-lull bins lowers λ₁/edge by ≥ 30% in ≥ 1/2 of units.

  Consistency with H02 (not a new test, same data): across matched chunks, the block-demeaned λ₁ − 1 ranks like H02's βJ₀ (Spearman ≥ 0.6).
  *Falsifier:* a localized top mode (majority-sign share < 0.6 or VR/λ₁ < 0.5 in most units), so the collective co-activation is not mean-field.
- **P3, talk spins and the room mode (axis G).** k_cd(talk) ≤ k_cd(activity) in ≥ 2/3 of units. In two-room units (35, 36b, 37, 38a–c, 39, 41, 42, 44, 51a–e, where ≥ 2 rooms each hold ≥ 3 present agents), some signal talk eigenvector separates the rooms (room-label permutation p < 0.05) in ≥ 1/2 of them.
  *Falsifier:* no room separation in ≥ 1/2 of two-room units, given that H05 found within-room talk coupling.
- **P4, content modes.** At d = 32, kind-centered, 30-min windows: k_cd(content) ≥ 1 in ≥ 1/2 of the scored units, and median λ₁/edge is higher in mode-C units than in mode-I/F units of the same regime.
  A unit counts as **underpowered** (not failed) if the synthetic recovery rate of a single planted mode of loading 0.3 at that regime's sampling is < 0.5 (`analysis/synthetic.py`). Low prior: content is sparse in regime III (median 3 statements per agent-window).
- **P5, a family mode** (HH77 "a family mode"; low prior). In units where ≥ 2 labs each have ≥ 3 present agents, some signal activity or content eigenvector separates labs (permutation p < 0.05) in ≥ 1/3 of such units.

**(b) Dimensionality arm (HH58): "PR drops after kickoffs and during consensus, re-expands in free weeks".**
- **P6, kickoff collapse (NE34; axis E).**
  - *Design.* Usable transitions g−1 → g: both sides non-holdout, same regime, both first hours with a valid PR30. ΔPR_kick = PR₁ₕ(day 1 of g) − PR₁ₕ(last day of g−1). Placebos: the same contrast for consecutive active days inside one unit, from day 1 → 2 onward.
  - *Prediction.* Median ΔPR_kick < 0, with ≥ 2/3 of kickoff contrasts negative; kickoff contrasts below the placebo contrasts (one-sided Mann–Whitney p < 0.05); median relative drop ≥ 10%. Spread TV also drops at kickoffs (same test, co-observable).
  - *Falsifier:* kickoff contrasts indistinguishable from placebos (p ≥ 0.2) or median ≥ 0.
- **P7, re-expansion after the kickoff ("field quench" over R4).**
  - In units of ≥ 3 days, PRday(day 1) < median PRday(days 2+) in ≥ 2/3 of units.
  - Within day 1, PR30 rises from the first hour to the last hour more than on the unit's other days (day-1 slope − mean slope of other days > 0) in ≥ 2/3 of units.
  - *Falsifier:* day 1 higher than later days in ≥ 1/2 of units. That would be R4: consensus forms over the week rather than being imposed at the kickoff.
- **P8, consensus weeks (#19, #31, #40).** Over days 2..D, PR30 declines: the OLS slope of PR30 on day index with time-of-day fixed effects is < 0 in all three. Each slope is also below the median slope of the non-consensus units of the same regime. The chance of three negative slopes is 1/8 under a symmetric null. Low power: 4–9 days per week.
- **P9, free > shared, within regime.**
  - Regime I: mean PRday of each free week (#11, #16, #31) is above the median of the shared-objective weeks (#13, #18, #19, #24, #25, #26, #30), and one-sided exact Mann–Whitney p ≤ 0.05 (3 vs 7; minimum attainable p = 0.008).
  - Regime III (descriptive): #37 ranks above #38, #40 and #44.
  - Individual-objective weeks lie between free and shared (no test).
  - Re-expansion at shared → free kickoffs (#30 → #31, #36b → #37) and individual → free (#10 → #11): ΔPR_kick > 0 (descriptive, n = 3).
  - *Falsifier:* free weeks at or below the shared median.
- **P10, the two arms agree (axis D: neither statistic is fitted to the other).** Across scored units within a regime, the content top-mode strength λ₁/edge correlates negatively with the unit's median PRday (Spearman ρ < 0 in regimes I and III; |ρ| ≥ 0.3 in at least one).

**Multiplicity and power.** Verdicts are P1–P10 by the rules above; per-unit p-values, variants and nulls are descriptive. Ten criteria at about α = 0.05 each give ~0.5 expected false passes. Per-unit k_cd uses a 95% edge, so ~1 unit in 20 shows a spurious mode at k = 0. P8 and the regime-III part of P9 are underpowered by design and are reported as directions.

**Confirmatory (held out; script written, not run).** `analysis/confirm.py` refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`, and `--dry-run` runs on non-holdout stand-ins. Held-out tests:
- P1/P2 on the held-out units with N ≥ 10 (#28, #29, #45, #46, #47, #49, #50);
- P6 on fully held-out transitions (#28 → #29, #45 → #46, #46 → #47, #47 → #48, #48 → #49, #49 → #50), against the same placebo rule inside held-out units;
- P9 with #22 (free, regime I): PRday above the median of the non-holdout regime-I shared weeks.

The exact thresholds are fixed in the script header after the exploratory round. They are written into the card as an amendment *before* any confirmatory run.

**Amendment 1 (2026-10-03, after the synthetic validation, before any real-data H12 statistic).**
*What I had seen:* the synthetic results (`figures/synthetic_validation.pdf`, `data/processed/H12-groupthink-dimensional-collapse/synthetic/summary_*.csv`) and the nuisance calibration taken from non-holdout data. Nothing else: no real-data eigenvalue, PR, spread or overlap. The calibration values:
- median activity fraction 0.55 / 0.66 / 0.44 (regimes I / II / III);
- latent AR(1) coefficient ≈ 0.6–0.7;
- a flat minute-of-window profile except the last decile (≈ 0.85);
- content agents present in 87–100% of windows, with 7.7 / 8.2 / 4.5 statements per present agent-window;
- whitened per-dimension variance 0.49–0.65 within an agent-window and 0.14–0.22 between windows.

Changes and clarifications:
1. **P1′ (strongest null).** The same rule as P1, applied to the lull-filtered count k_lull: bins with ≤ 1 active agent are dropped before C and in every surrogate.
   - *Why.* With platform stalls covering 5% of bins and no collective mode, the cross-day null fires in 94% of synthetic runs. A genuine market mode (a = 0.3) survives the filter in 96–100% of runs (λ₁/edge 1.24 → 1.17).
   - *Verdicts.* HH77's "beyond random-matrix noise and the schedule" verdict is P1; "beyond platform stalls" is P1′. Both are reported.
2. **P2's lull criterion is kept** (λ₁/edge drops by ≥ 30%). In the synthetic, pure stalls drop it by 48% and genuine modes by 6%.
3. **P5 (family mode) becomes descriptive.** A mode loading a third of the agents, nested in the market mode, was never recovered, even at a = 0.5.
4. **P4 power.** Every scored unit is "powered" by the rule. A single content mode with a = 0.3 is recovered with probability:
   - 0.98 in 5-day units (regimes I and III);
   - 0.64 in 3-day units;
   - 0.96 in the 2-day #51 unit;
   - 1.0 in the long #51 units.

   Halving the statement counts drops recovery to 0.58.
5. **False positives.** The cross-day edge gives 6–10% false positives in 5-day units and ~14% in 3-day units (nominal 5%). With 23 units, expect ~2 spurious k ≥ 1 under a global null, so "k = 0 in ≤ 1/6" says little about absence.
6. **PR estimator facts used in interpretation.**
   - Bias-corrected PR is unbiased within 3% for flat spectra. At n = 30 it reads +4–10% high for heavy-tailed spectra. PR30 on clustered windows reads +0–8%.
   - PRday is the mean PR of 6-agent subgroups. It is nearly N-invariant, so comparisons across periods with different N are fair. By design it sits 2–40% below the all-agent mixture PR.
   - Between-agent PR is capped by N − 1. Naive values are inflated by statement noise; split-quarters remove the noise. The finite-N correction recovers low-dimensional spreads but is unstable when PR ≳ N/2. Between-agent PR is therefore descriptive only.
7. **P6 power.** 73% for a true 10% first-hour drop if day-to-day PR variability is ≤ 10%; 13% if it is 20%. The placebo pairs measure that variability. If their sd exceeds 15% of PR, a P6 failure is read as "underpowered for drops < 20%", not as "no drop".
8. **Unit lists by rule.**
   - Two-room units (≥ 2 rooms each holding ≥ 3 present agents) are 35, 36b, 37, 38a, 38b, 38c, 39, 41, 42 and 44. The #51 sub-units have only one such room, so they leave P3.
   - A sequential rank-wise count k_rank is added as a secondary diagnostic. It is not used in verdicts.
9. **Per-period verdict rule (G folders).**
   - Headline checks per period: (i) HH77, k_cd(activity) ∈ {1, 2, 3} with a uniform top mode (majority-sign share ≥ 0.8); (ii) HH58, PRday(day 1) < median PRday(days 2+) (P7a, periods of ≥ 3 days) and, where a usable transition exists, ΔPR_kick < 0 (P6); plus the period's role check (P8 for #19, #31 and #40; P9 for free and shared weeks).
   - **Supported** if all applicable checks hold, **failed** if none do, **mixed** otherwise.
   - For long periods split into sub-units, (i) must hold in ≥ 2/3 of the sub-units.

**Clarifications (2026-10-03, after the per-unit pipeline had run but before any P1–P10 statistic was tabulated or looked at).** The only real-data numbers I had seen were the unit-10 smoke test, a descriptive regime-I period that enters no verdict (activity k_cd = 1, k_lull = 0; PR30 ≈ 10).
- **P4's "mode-I/F" group** is units whose mode is exactly I or F. #51 (mode I/K, private roles) is excluded and reported as a variant.
- **P9's shared-week rule** ("below the free weeks") means below the median of the regime's free weeks, symmetric with the free-week rule.
- **P6 placebo set.** As pre-registered, it includes day 1 → 2 pairs. A variant without them (day 2 → 3 onward) is reported, because under P7 the day 1 → 2 change is expected to be positive, which would make the kickoff contrast look more extreme.
- **P7a** uses the unit that contains the period's first day (the kickoff day).
- **Correction (counting error, no rule change).** There are 24 scored units, not 23: 7 in regime I, 2 in regime II and 15 in regime III, of which 5 are #51 sub-units.

**Amendment 2 (2026-10-03, after exploratory round 1, before any holdout data was read). Confirmatory predictions for `analysis/confirm.py`.**
*What I had seen:* everything in Results below, from non-holdout data only. The script header fixes the same thresholds. These replace the provisional confirmatory plan above, because exploration changed what is worth confirming: the one-mode finding and the reversed kickoff direction.
- **Held-out units** (N ≥ 10, ≥ 2 days): #28, #29, #32a (02-23..24, regime I), #32b (from 02-25, regime II), #34, #45, #46, #47, #49, #50, and the #51 tail (09-07 → 09-21).
- **C1.** k_cd(activity) = 1 in ≥ 2/3 of held-out units.
- **C2.** Among units with k_cd ≥ 1, majority-sign share ≥ 0.8 and VR/λ₁ ≥ 0.85 in ≥ 2/3.
- **C3.** Spearman(joint-lull fraction, relative drop of λ₁/edge after the lull filter) ≥ 0.6. That is, the market mode's lull dependence is set by how much of the period is joint lulls.
- **C4.** k_cd(content) ≥ 1 in ≥ 2/3 of held-out units, and it survives agent-day centering in ≥ 2/3.
- **C5 (kickoff-day expansion, the reversed P7).** PRday(day 1) > median PRday(days 2+) in ≥ 2/3 of held-out periods with ≥ 3 days.
- **C6.** Over the fully held-out transitions (#28 → #29, #45 → #46, #46 → #47, #47 → #48, #48 → #49, #49 → #50), the median relative first-hour PR change is > 0.
- **C7 (original P9 test, kept).** #22's mean PRday is above 14.82, the round-1 median of the non-holdout regime-I shared weeks. Credence ≈ 0.4.
- **C8.** In held-out regime-III days, Spearman(within-agent near-duplicate share, PRday) ≤ −0.5.
- **Reading the results.** Each C is reported pass/fail and nothing is pooled with exploratory units. C1–C4 bear on HH77 as revised. C5, C6 and C8 bear on the replacement of HH58 by "kickoffs expand, loops collapse".

## Results by goal period
Period verdicts follow Amendment 1, item 9: HH77's per-period check, plus P7a, P6 and the period's role check. Most periods are "mixed" for the same reason: the one-mode check holds and the dimensionality checks do not. The three "supported" periods (G16, G27, G33) pass on a single favorable day-1 sign and are no evidence for HH58. The cross-period tests below are the evidence.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G11](G11/README.md) | exploratory · free (P7, P9) | mixed | k act 1 (lull 1), content 1; PRday 13.6; day 1/later 10.5/14.7; kickoff ΔPR +28% |
| [G13](G13/README.md) | exploratory · shared (P9) | mixed | k act 1 (lull 0), content 1; PRday 13.7; day 1/later 16.9/14.6; kickoff ΔPR −2% |
| [G16](G16/README.md) | exploratory · free (P7, P9) | supported | k act 1 (lull 0), content 1; PRday 14.9; day 1/later 15.1/15.3 |
| [G18](G18/README.md) | exploratory · shared (P9) | mixed | k act 1 (lull 0), content 1; PRday 14.7; kickoff ΔPR +36% |
| [G19](G19/README.md) | exploratory · consensus (P7–P9) | mixed | k act 1 (lull 0), content 1; PRday 14.8; day 1/later 16.0/15.0; slope days 2..D +0.16/day; kickoff +1% |
| [G23](G23/README.md) | exploratory · scored | mixed | k act 1 (lull 1), content 1; PRday 12.5; day 1/later 14.1/12.3 |
| [G24](G24/README.md) | exploratory · scored | mixed | k act **0**, content 1; PRday 13.8; day 1/later 14.7/12.4; kickoff +16% |
| [G25](G25/README.md) | exploratory · scored | mixed | k act 1 (lull 0), content 1; PRday 16.1; day 1/later 15.2/16.8; kickoff −7% |
| [G26](G26/README.md) | exploratory · scored | mixed | k act 1 (lull 0; 39% joint lulls), content 1; PRday 14.9; kickoff −23% |
| [G27](G27/README.md) | exploratory · scored | supported | k act 1 (lull 1), content 1; PRday 15.6; day 1/later 15.9/16.1; kickoff −25% |
| [G30](G30/README.md) | exploratory · scored | mixed | k act 1 (lull 1), content 1; PRday 16.3; day 1/later 16.6/16.3 |
| [G31](G31/README.md) | exploratory · free + consensus | mixed | k act 1 (lull 0), content 1; PRday 16.2; day 1/later 16.8/15.8; slope −0.16/day (the only consensus week that declines); kickoff −17% |
| [G33](G33/README.md) | exploratory · scored | supported | k act 1 (lull 1), content 1; PRday 17.7; day 1/later 16.2/18.5 |
| [G35](G35/README.md) | exploratory · scored | mixed | k act 1 (lull 1), content 1; PRday 18.3; day 1/later 20.2/17.4; talk room p (2nd eigvec) 0.01 |
| [G36](G36/README.md) | exploratory · scored (36b) | mixed | k act 1 (lull 1), content 1; PRday 16.8; kickoff +14% |
| [G37](G37/README.md) | exploratory · free, regime III | mixed | k act 1 (lull 0; 42% joint lulls), content 1; PRday 15.8 (rank 2/4 in III); kickoff +42% |
| [G38](G38/README.md) | exploratory · scored (38a–c) | mixed | k act 1,1,1 (lull 1,0,0), content 1,1,2; PRday **9.3**; day 1/later 14.6/8.9; 25% self-repeats |
| [G39](G39/README.md) | exploratory · scored | mixed | k act 1 (lull 0), content 1; PRday **5.7**; 60% self-repeats; kickoff +87% |
| [G40](G40/README.md) | exploratory · shared + consensus | mixed | k act 1 (lull 1), content 1; PRday **9.9**; day 1/later 13.1/9.2; slope +0.17/day; 16% self-repeats |
| [G41](G41/README.md) | exploratory · scored | mixed | k act 1 (lull 1), content 1; PRday 15.4; day 1/later 16.7/15.4; kickoff +45% |
| [G42](G42/README.md) | exploratory · scored | mixed | k act 1 (lull 1), content 1; PRday 16.8; day 1/later 17.4/16.5; kickoff +33% |
| [G44](G44/README.md) | exploratory · scored | mixed | k act 1 (lull 1), content 2; PRday 16.9; day 1/later 18.7/15.8 |
| [G51](G51/README.md) | exploratory · scored (51a–e) | mixed | k act 1,1,1,1,0 (lull 0,1,1,1,0), content 1,1,2,1,1; PRday 15.9; strongest market mode (λ₁/edge 2.1–2.5 in 51b–d) |
| [NE34](NE34/README.md) | exploratory · kickoff event study | failed | 20 transitions: median ΔPR +7% (regime III +44%), 45% negative, p = 0.86 vs 189 placebos |

## Results
*Round 1, 2026-10-03, non-holdout only. Code: `scheme/build.py`, `analysis/{h12lib, synthetic, run_units, evaluate, posthoc, figures, figures_real, write_period_folders, confirm}.py`. Data: `data/processed/H12-groupthink-dimensional-collapse/` (26 MB). One-page summary: `figures/H12_summary.pdf`.*

**Headline.**
- **Spectrum.** The swarm has exactly one collective mode beyond random-matrix noise and the daily schedule. It is a uniform, Curie–Weiss-like "market mode", found in activity (22/24 units), talk (20/24) and content (24/24 units; 3 also have a second content mode). It is partly synchronized lulls: it survives removal of joint-lull minutes in 14/24 units, and in 9/11 units where lulls are rare.
- **Dimensionality.** This half fails in the predicted direction. Kickoffs do not collapse the participation ratio. Day 1 of a goal is *more* diverse than later days (13/16, p = 0.02). Free weeks are not more diverse than shared-objective weeks.
- **The real collapse.** The lowest-dimensional periods (#38–#40) show agents repeating themselves (16–60% of chat statements are near-copies of the same agent's earlier text), not agents echoing each other (≤ 3%).

**Synthetic validation (axis F; `analysis/synthetic.py`, `figures/synthetic_validation.pdf`, `data/processed/.../synthetic/summary_*.csv`).**
- **Nulls with no planted mode** (activity, N = 15, 5 days, calibrated rates, switching and schedule):
  - naive MP finds a false mode in 50–90% of runs (autocorrelation);
  - T_eff-MP in 2–10% under a shared schedule, but 98% under heterogeneous daily profiles;
  - within-day circular shifts in 70% under heterogeneous profiles (confirming H05's warning);
  - the cross-day surrogate in 6–10% (about 14% in 3-day units).

  Platform stalls (5% of bins, 3–10 min each) fool even the cross-day null (94%); the lull filter removes them (0–12%).
- **Recovery.** One planted market mode is recovered with probability 1.0 at latent loading a ≥ 0.25 (0.32 at a = 0.15), and ≥ 93% at a = 0.3 for N = 10–21 and D = 3–19, including 2-day 8-h units. A room mode needs a ≥ 0.35. A sparse family mode (a third of the agents, nested in the market mode) is never recovered, even at a = 0.5.
- **Content.** One mode at a = 0.3 (share of window-level signal variance) is recovered in 98% of 5-day units in regimes I and III, 64% of 3-day units and 96% of the 2-day #51 unit. Halving statement counts drops this to 58%; doubling gives 98%.
- **PR estimators.**
  - The Wishart-corrected PR is unbiased within 3% for flat spectra at n ≥ 15. It reads +4–10% high at n = 30 for heavy-tailed spectra.
  - Naive PR reads 47–87% of truth at n = 30; effective rank is biased both ways.
  - PR30 on clustered windows reads +0–8%.
  - PRday measures 6-agent subgroups and is ~N-invariant, sitting 2–40% below the all-agent PR by design.
  - Between-agent PR is capped by N − 1. At N = 10 a 10-dimensional spread reads 4.7; the finite-N correction recovers it but is unstable at small N.
- **Kickoff test (P6) power.** 73% for a 10% drop when day-to-day sd ≤ 10%; 13% when sd = 20%.
- **Post hoc (A5).** With *long* joint lulls (20–60 min, 10–25% of bins), the lull-filtered test loses power even with a genuine mode: 90% → 25% at D = 5, and 37% → 2.5% at D = 3. The real lull fractions (median ≈ 0.1, up to 0.42) are in that range.

**Outcome vs prediction.**

| Prediction | Rule (card) | Observed | Verdict |
| --- | --- | --- | --- |
| P1 few activity modes | k_cd ∈ {1–3} in ≥ 2/3, k = 0 in ≤ 1/6; MP inflated (k_MP ≥ k_cd + 1) in ≥ 1/2 | k = 1 in 22/24, k = 0 in 2 (#24, 51e), none ≥ 2; MP inflated in only 7/24 | core holds; auxiliary claim fails → **fail** by the full rule |
| P1′ beyond lulls (Am. 1) | same rule after the lull filter | k = 1 in 14/24, k = 0 in 10 | **fail** (power-limited where lulls are long: 9/11 low-lull vs 5/11 high-lull units) |
| P2 Curie–Weiss market mode | uniform, VR/λ₁ ≥ 0.7 in ≥ 2/3; III > I; lull drop ≥ 30% in ≥ 1/2 | uniform in 22/22 (sign share 1.0, VR/λ₁ median 0.97); λ₁/edge median I 1.37 < II 1.46 < III 1.62; lull drop ≥ 30% in 11/24 (median 29%) | 2 of 3 parts → **fail** (by one unit) |
| P2 vs H02 (consistency) | ρ(λ₁_block − 1, βJ₀) ≥ 0.6 | ρ = 0.73 over 21 H02 chunks; ρ(VR_block, VR_H02) = 0.88; VR_block/λ₁_block = 0.90 | consistent |
| P3 talk modes, room mode | k_talk ≤ k_act in ≥ 2/3; a signal talk mode separates rooms in ≥ 1/2 of two-room units | 22/24; room separation by a signal mode in 3/10 (8/10 if sub-edge eigenvectors 2–3 count) | **fail** |
| P4 content modes | k ≥ 1 in ≥ 1/2; C > I/F in each regime | 24/24 (21 one mode, 3 two); C > I/F in regime I (2.24 vs 1.90), not III (1.29 vs 1.33; 1.25 with #51) | core holds; mode contrast fails → **fail** |
| P5 family mode | descriptive (Am. 1) | some signal eigenvector separates labs in 10/24 eligible units | descriptive |
| P6 kickoff collapse (NE34) | median Δ < 0, ≥ 2/3 negative, MW p < 0.05, drop ≥ 10% | median +7%, 9/20 negative, p = 0.86; TV unchanged (p = 0.28); placebo sd 21% | **fail** (wrong sign; regime III +44%, 4/4 up) |
| P7 re-expansion | day 1 < later in ≥ 2/3; day-1 slope up in ≥ 2/3 | day 1 lower in 3/16 (**higher in 13/16**, p = 0.02); slope up in 7/14 | **fail**; R4 direction |
| P8 consensus weeks | slope < 0 in #19, #31, #40 and below the regime median | #19 +0.16 (below the regime-I median +0.19); #31 −0.16 ✓; #40 +0.17 (regime-III median −0.18) | **fail** (1/3) |
| P9 free > shared | each regime-I free week > shared median; exact MW p ≤ 0.05 | free 13.6 / 14.9 / 16.2 vs shared median 14.8; p = 0.58. Regime III: #37 (15.8) ranks 2/4 (#44 16.9; #38 9.3, #40 9.9) | **fail** |
| P10 arms agree | ρ(content λ₁/edge, PRday) < 0 in I and III | ρ = +0.36 (I, n = 7), +0.15 (III, n = 15) | **fail** |

Ten criteria at α ≈ 0.05 would give ~0.5 false passes. No criterion passed in full, so multiplicity is not the issue. The two "core holds" findings (P1 core, P4 core) are robust across every null except lulls.

**(a) Random-matrix arm: what the single mode is.**
- **Shape.** One mode, uniform across agents (sign share 1.00 in 22/22 units; IPR·N ≈ 1.15). It is almost exactly the Curie–Weiss uniform mode (VR/λ₁ = 0.89–0.99).
- **Strength.** It is modest in regime I (λ₁/edge 1.1–1.9) and strongest in the #51 private-role era (2.1–2.5 in 51b–d, N = 24–27, 8-h days). Its strength ranks like H02's Curie–Weiss βJ₀. H12's top mode *is* H02's collective co-activation, now shown to be the only mode beyond the schedule null.
- **Not a schedule artifact.** Every count except naive MP agrees on k = 1 (circular, T_eff-MP and rank-wise counts give 1 in 20–21 units).
- **Partly lulls.** The relative drop of λ₁/edge after removing minutes with ≤ 1 active agent rises almost linearly with the share of such minutes (Spearman 0.97, `figures/rmt_arm.pdf` c). In #37 (42% joint lulls) and #51a (27%) the mode disappears entirely. Where joint lulls are rare (≤ 10% of minutes), the mode survives in 9/11 units. H02's reading ("synchronized lulls, possibly platform stalls") is therefore half right. What the long lulls are (stalls, simultaneous declared pauses, end-of-session quiet) was not checked; #26 is a regime-I period with 39% lulls, so declared pauses cannot be the whole story.
- **Talk.** One mode in 19/24 units, two in 51b, none in 4. It exceeds the activity count only in 51b and in #24, where activity has no mode. Rooms are visible in the talk spectrum (8/10 two-room units have a sub-edge talk eigenvector separating rooms at p < 0.05) but never rise above the edge. This is the spectral counterpart of H05's weak within-room talk coupling.
- **Content.** Every unit has one content mode, uniform in sign: agents' content deviations move together window by window. It survives agent-day centering in 24/24 units (λ₁/edge median 1.38 vs 1.52), so it is within-day co-movement (shared attention shifts), not just a shared drift across days. It holds at d = 8 and for chat only (where 7/24 units show 2 modes). It is stronger in regime I (≈ 2.0) than regime III (≈ 1.3), plausibly because regime I had a single room.
- **Family.** Lab separation of a signal eigenvector appears in 10/24 units (descriptive). Synthetic recovery of a true family mode is ~0, so this is lab-dependent loading on the market mode, not a separate family mode.

**(b) Dimensionality arm: what PR does instead.**
- **Kickoffs.** First-hour PR rises at regime-III kickoffs (+33% to +87%, 4/4) and is unchanged in regime I (median −2%). Day 1 of a goal has higher PRday than the median of later days in 13/16 scored periods (19/25 periods of any N, p = 0.015). The kickoff is a burst of *diverse* proposals, not a collapse onto one direction.
- **Within the week.** There is no consistent decline over days 2..D: the median slope is +0.19/day in regime I and −0.18/day in regime III. Only #31 among the consensus weeks declines.
- **Mode does not set dimensionality.** In regime I, free, shared and individual weeks all sit at PRday 12.5–16.3, except #10 at 10.4.
- **The lowest-PR periods are loops.** In regime III, PRday falls to 5.7–9.9 in #38–#40. Those days have 16–60% of chat statements that are near-copies (cosine > 0.95) of the same agent's earlier text that day. Cross-agent copies are ≤ 3%. Across regime-III days, Spearman(self-repetition, PRday) = −0.75; for cross-agent copies it is −0.24.
- **Robust to removing loops.** Removing self-repeats (12% of chat) leaves P6 null (median +0.1%; regime III +35%), keeps day 1 higher (12/15, p = 0.035) and keeps P9 null (p = 0.58). #38 and #40 PRday rise to ≈ 12 but stay below the other regime-III periods (≈ 16).
- **Spread.** TV (size) tells the same story as PR (shape): no drop at kickoffs.
- **Between-agent PR** (descriptive, capped by N) is 2.4–7.8 (median 3.8), so agents differ along a handful of directions.

**Heterogeneity.**
- The market mode is present in every regime and mode. Its strength varies 2.5-fold across units and tracks regime (III > II > I) and the joint-lull share, not coupling mode. Median λ₁/edge in regime III: C 1.59, I 1.43, I/K 2.12, F 1.78 (n = 1); in regime I: C 1.30, K 1.58, F 1.60 (n = 1).
- Kickoff effects differ by regime (I ≈ 0; III strongly positive).
- PR levels are flat across modes in regime I and bimodal in regime III (loop periods vs the rest).
- Two units have no activity mode: #24 (Christmas week, 0% joint lulls) and 51e (2 days, N = 31).

**Caveats.**
- **Amendments and what I had seen.**
  - Amendment 1 (P1′, P5 descriptive, power notes, per-period verdict rule) was made after the synthetic validation and the nuisance calibration only.
  - The clarifications (P4's I/F group, P9's shared rule, the P6 placebo variant, P7a's unit) were made after the per-unit pipeline had run and after seeing only the unit-10 smoke test (a descriptive period). No P1–P10 statistic had been tabulated.
  - Amendment 2 (confirmatory C1–C8) was written after all of round 1.
  - The NE34 folder was created after the run; its prediction is the card's pre-run P6/P7, copied verbatim.
- **Post hoc analyses decide no verdict.** These are the lull stratification, the long-lull synthetic (A5), agent-day-centered content, the near-duplicate split and the dedup variant.
- **The lull filter has two biases.** It is conservative when lulls are long and D is small, because offset groups in cross-day surrogates keep their own lulls. Its synthetic justification (short stalls) did not match the real lull structure. P1′'s failure is partly a power failure.
- **The cross-day null leaks.** About 1/D of agent pairs keep their real alignment in each surrogate. This is conservative, and it raises the edge for secondary modes when the market mode is strong. Sub-edge structure (rooms, labs) can be real yet undetectable by design.
- **PR measures what agents write, including format.** Self-repetition, templated status posts and chat/intention composition all move it, so it is not a pure "thinking alike" statistic. Whitening is per regime, so PR levels are comparable only within a regime.
- **Short and small units.** 3-day units have ~14% false positives. Regime-I periods #11, #16, #19, #13 and #18 have N = 6–7 and enter only the PR comparisons.
- **The holdout is untouched.** No embedding-model swap was run (bge-small only). Content modes could partly reflect shared vocabulary drift that is not semantic.

## Groupthink monitor (sketch)
Round 1 says *dimensional collapse* is the wrong primary statistic for groupthink: PR rises at kickoffs and falls when agents loop. A practical monitor therefore tracks three cheap statistics.
1. **Collective-mode strength (main signal).**
   - *Statistic:* daily λ₁/edge of the agent × agent content-overlap matrix Q (30-min windows, whitened sentence embeddings, agent-centered and day-centered), with the edge from 100 cross-day surrogates over a trailing 5-day window, plus VR/λ₁ (how uniform the mode is).
   - *Groupthink alarm:* λ₁/edge rising above the swarm's own trailing 95th percentile *while* VR/λ₁ ≥ 0.9, i.e. everyone moving together in content.
   - *Same on activity spins:* report the joint-lull share alongside, so stalls and mass pauses are not read as alignment.
2. **Cross-agent echo rate.** The share of statements with cosine > 0.95 to *another* agent's statement in the last 2 h. This is the direct "saying the same thing" signal; it was ≤ 3% in this village.
3. **Self-repetition rate.** The share with cosine > 0.95 to the *same* agent's earlier statement. This is a loop and trap alarm (16–60% in #38–#40), and it is also the correction any PR-based monitor needs.

PR30 / PRday (bias-corrected, agent-capped, rarefied to a fixed n) is kept as a context gauge, not an alarm.

**How it runs on another swarm's logs.** Input is (agent, timestamp, text) for messages, plus optionally per-minute activity:
1. Embed with any sentence model.
2. Whiten on a reference period, e.g. the first week.
3. Bin into 30-min windows within each day's active span.
4. Compute Q and its cross-day edge per day (O(N²·T·d), seconds for N ≤ 50), plus the two duplicate rates.
5. Alarm on deviations from the swarm's own baseline.

Nothing is fitted, the cost is under a minute per swarm-day on a laptop, and the code is `analysis/h12lib.py` (`overlap_eig`, `spectrum_test`, `pr_rarefied`) plus `posthoc.near_dup_share`. Before trusting it on a new swarm, validate with `analysis/synthetic.py`, calibrated to that swarm's counts.

## Notes
- 2026-10-03: promoted from shortlist 2 (HH77 + HH58 (shortlist 2, item 3)).
- 2026-10-03: Observables, Null and Prediction written before any real-data run (see "What I had seen").
- 2026-10-03: synthetic validation run; Amendment 1 written before any real-data statistic.
- 2026-10-03: G folders created with dated predictions before running on each period; NE34 folder after (see its note).
- 2026-10-03: exploratory round 1 done. Status: **HH77 partially supported** (exactly one Curie–Weiss-like market mode, partly lulls); **HH58 refuted in direction** (kickoffs expand; loops, not consensus, collapse dimensionality). Confirmatory C1–C8 written (Amendment 2); `analysis/confirm.py` not run, awaiting sign-off.
- Compute: all real-data runs took < 2 min wall time on ≤ 2 processes. Synthetic runs took ~3 min. Disk: 26 MB.
