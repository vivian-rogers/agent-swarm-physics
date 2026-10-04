# H103: Nights demagnetize: remanence decays per night

**Status:** exploratory round 1 **done (2026-10-04): failed. Nights do not demagnetize the content; remanence decays during active work, and the night slightly re-magnetizes toward the goal.**
- **Clock comparison (P1, failed by the kill clause).** In 22/31 periods the kickoff remanence decays. The active-hour clock fits as well as or better than the night clock in 17/22 (bge) / 16/22 (gte); the night clock wins in 5/22 / 3/22. Synthetic clock-selection accuracy 0.82 at real counts, so the negative is a failure, not inconclusive.
- **No night step at fixed active lag (O3, 41 units).** β_N −0.001 [−0.023, +0.021] (bge), −0.002 [−0.028, +0.024] (gte). Across the night the kickoff alignment rises relative to a midday split (+0.03 [+0.01, +0.06]), a morning re-orientation.
- **Natives:** the end of the operator's bookends (NE43) and context resets inside the day (NE41) leave content unchanged (both supported as predicted); a 300-min village-off midday break behaves like a same-day gap (descriptive). An agent's own idle hour does not age its content (+0.10), pointing to the agent's call clock.
- Card, predictions and synthetic came first; Amendment 1 (O3 design) after the synthetic, before real data. `confirm.py` written, dry-run on stand-ins, **not run**. Scorecard A1 B1 C1 D1 E1 F2 G1 H1 I1.
**Question (GOALS.md):** **Q2** (which clock the content field relaxes on: the scheduler's night, active work, or wall time) and **Q4** (where content memory lives: if nights erase it, the context window carries it; if not, it survives the night in context, memory or artifacts).
**Fields:** stat mech (vector spins, remanence, AC demagnetization), dynamics (clock comparison, relaxation), stochastic thermodynamics (where in time the relaxation happens; H76 found activity excess at day edges)
**Literature:** none in `literature/` covers demagnetization. Background from memory: Bertotti, *Hysteresis in Magnetism* (1998)† (AC demagnetization: an alternating field of decaying amplitude multiplies the remanence per cycle). The relaxation-clock framing follows `physics-models/15-stochastic-thermodynamics-selection/` (excess irreversibility concentrated at day edges, H76).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent (19, 28, 30 excluded); Regime (whitening per regime); Driving / external field (kickoff, goal text, room kickoffs); Activity time (here the **active-hour clock**, below); Agent state, variant *vector*, as H01's **agent state (vector), whitened statement mean** at 30-min resolution (DQ5 `agent_win30_style_resid`); H54's **quench target (kickoff)** and **kickoff remanence** (here at 30-min resolution, H48's variant **kickoff remanence (active-hour)**); Context segment (H45; resets `reset_consol | reset_session | reset_forced`). New named variants proposed for DEFINITIONS.md (defined under Observables): **night clock N**, **active-hour clock H**, **wall clock W**, **reset clock R**, **night factor λ**, **night step β_N**, **break-length term β_G**, **own-gap placebo β_gap**.
**From:** HH331 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (primary: remanent content magnetization), `physics-models/15-stochastic-thermodynamics-selection/` (secondary: where the relaxation happens in time; day-edge excess vs housekeeping, H76)
**Data inputs (shared tables first):** DQ5 `embeddings/agent_win30.parquet` + `agent_win30_{style_resid,white32}_{bge_small,gte_modernbert}.npy`; DQ5 statement vectors (`statements.parquet`, `statements_style_resid32_*`) for the previous-centroid series; shared `goal_fields` (`embeddings/goals.parquet` + goal vectors); `calendar`; `call_windows` (own-gap placebo); `context_ledger_turns` (reset flags `reset_consol`, `reset_session`, `reset_forced`); `outages_fixed/outages.parquet` (village-off midday breaks); `roster`; `period_units`; `holdout_mask`.
**Relation to H82 (running in parallel; no card results or data existed when this card was written):** HH331 asks for a clock comparison on H82's remanence series. H82 has no outputs yet, so H103 builds its own two remanence series (the finished kickoff, and the previous centroid with the new field projected out) with the same construction H82 specifies (leave-i-out centroid, placebo centroids). H103's test is distinct: which clock the decay runs on, with a midday-gap placebo. No H82 code or data is used.

## Source HH (verbatim from the HH list, including refinements)
Nights demagnetize: remanence decays per night, not per hour. Overnight consolidation and erasure act like an AC demagnetization step on the content magnetization.
  - *Prediction:* alignment with the previous period's centroid, and with a finished kickoff, falls in steps at night boundaries by a roughly fixed factor per night. Active-hour clocks fit worse than the night-count clock.
  - *Check:* a clock comparison (nights vs active hours vs wall time) on H82's remanence series, plus a placebo on midday breaks of the same length.
  - *Kill:* active hours fit as well as or better than nights.
  - *Models:* 11, 15 · *Builds on:* H82, H71, H20

## Question
When the swarm's content remembers a field that has stopped acting (the kickoff message, the previous goal's state), does the memory fall in steps at night boundaries, by a fixed factor per night, or does it decay smoothly with active work or with wall time?

## Design: two layers (Vivian, 2026-10-04)
- **Replication** (role `replication`): the clock comparison on every eligible non-holdout goal period (kickoff remanence, O1; previous-centroid remanence, O2) and the two-time self-overlap night step on every eligible period unit (O3).
- **Natives** (role `native`): **G51 NE43** (the operator's daily pause/resume messages stop after 2026-08-04: does the night step need the operator's bookends?), **NE41 reset clock** (regime III: forced erasures every 41 calls inside a day; does a context reset act like a night?), **G04/G06 village-off midday breaks** (2025-06-18, 300 min; 2025-06-29, 774 min: the literal "midday break of night length" placebo).

## Model
**From:** `physics-models/11-vector-spins/`. The remanent part of the content magnetization along a direction ê that no longer has a source (a kickoff message that has scrolled away; the previous goal's state) relaxes as

  m(t) = m_∞ + Δm · f(t),   with one of four clocks:
  - **night clock N** (HH331, AC demagnetization): f = λ^{N(t)}, N = night boundaries crossed since the kickoff; flat inside a day;
  - **active-hour clock H:** f = exp(−H(t)/τ_H), H = active hours since the kickoff (calendar activity windows);
  - **wall clock W:** f = exp(−W(t)/τ_W), W = wall hours since the kickoff;
  - **reset clock R:** f = exp(−R(t)/ρ), R = mean context resets per agent since the kickoff (`reset_consol | reset_session | reset_forced`).
- Nested: f = λ^N exp(−H/τ_H). λ < 1 at fixed H is the night step beyond active-hour decay.
- Each model also carries a **time-of-day profile** s(slot) (4 slots = quarters of the day's active window), common to all days. It removes a scheduler field: a morning re-orientation that looks the same every day.
- The mechanism HH331 names (overnight consolidation and erasure) predicts the night clock in regime III only if nights carry a reset. In regime III the context carries over the night (H69; first-of-day calls are resets in about a third of cases), and resets happen every ~41 calls inside the day (NE41). In regimes I/II, first-of-day calls are resets in 6–10% of cases.

**Rivals.** R1 active-hour decay (HH331's kill); R2 wall-clock decay (a night is just long); R3 reset clock (erasures, not nights); R4 time-of-day field (a daily morning profile with no decay); R5 no decay (persistent field: after NE08/NE13 the goal and the kickoff sit in the prompt).

## Data scheme (`scheme/`)
Script: `scheme/build.py` (shared tables only; no text; holdout rows dropped with `common.holdout_mask` and asserted).
- **Windows:** DQ5 agent × 30-min windows (`agent_win30`, aligned to each day's calendar window start), eligible agents only, n_chat + n_intent ≥ 2, unit-normalized. Variants style_resid [primary] and white32, both models. Window time = window midpoint.
- **Clocks per window:** H (active hours since t₀, summed over calendar windows), N (active-day index − 1), W (wall hours since t₀), R (mean over the period's incumbent agents of their resets with `t_call` in (t₀, t]), slot (quarter of the day's window), day index.
- **O1 kickoff series:** eligible goal periods = non-holdout, shared kickoff, ≥ 3 active days in one regime; #23 (H10 blind), #36 (regime boundary inside its first days) and #7 (2 days) excluded. Fit window: the first min(5, n_days) active days. Incumbents = agents with an eligible window on day 1 after t₀ (later joiners excluded, so composition is fixed). Per window: a_{iw} = cos(s_{iw}, k̂_P) − mean_q cos(s_{iw}, k̂_q), decoys q = every other eligible non-holdout kickoff except P−1, P+1 and #23, whitened in P's regime basis (H54's genericness correction). A_w = mean over agents in the window; weight = number of agents.
- **O2 previous-centroid series:** the H82 construction: ê_{P−1}^{(−i)} = unit mean of the other agents' agent-day vectors over P−1's last 3 active days; projected orthogonal to P's field span (kickoff, goal text, room kickoffs); minus the median over placebo centroids of non-adjacent same-regime periods (≥ 3 needed). Same windows and clocks as O1, transitions with both periods non-holdout.
- **O3 self-overlap pairs:** per period unit (`period_units`, non-holdout, ≥ 3 active days, one regime): pairs of the same agent's windows (w, w′) on the same active day with ΔH ≥ 0.5 h, or on consecutive active days (N = 1). Pair covariates: ΔH (active hours between window midpoints), N, the night's wall length G (h), slots of both windows, `gap_own` (same-day pair whose agent has a call-free interval ≥ 60 min between them; `call_windows`), and Δr (the agent's own resets between the windows; regime III, N2). G51 is split at NE43 (07-06 → 08-04 vs 08-05 → 09-04) for N1.
- **Output:** `data/processed/H103-nights-demagnetize/` (`windows_<model>_<variant>.parquet` with clocks and A_w per period; `prev_<model>.parquet`; `pairs_<model>_<unit>.parquet` aggregated by covariate cell; `replication/`, `natives/`, `synthetic/`; `_provenance.json`).
- **Regimes covered:** I, II (#33, #35 for O1/O3; O2 has too few placebos), III.

## Observables
*Written 2026-10-04 20:45 UTC. Sampling facts already seen: eligible 30-min window counts per period, night and day lengths per regime (median night 19–21 h; median active day 3.0 h in regime I, 4.0 h in II, 7.6 h in III), reset flags at first-of-day calls by regime (session or consolidation resets in 6% / 10% / ~35–70% of first-of-day calls in I / II / III), village-off midday breaks ≥ 60 min (two, both regime I: 2025-06-18 300 min, 2025-06-29 774 min). No content statistic has been computed.*

**O1. Kickoff-remanence clock comparison (primary).** For each period: weighted least squares of A_w on each clock model (3 parameters + 3 slot effects each; equal parameter counts, so SSE compares directly). Statistics:
- **decay present:** Δm of the best clock model > 0 with its agent-bootstrap CI (200 draws) excluding 0;
- **winning clock** (lowest SSE) and the bootstrap share of draws in which the night model beats the active-hour model;
- **night factor λ** in the nested model (λ^N e^{−H/τ_H}), with its bootstrap CI;
- model-free companions: the night step S_N = Ā(first 2 windows of day d+1) − Ā(last 2 windows of day d), the day drift D_d = Ā(last 2) − Ā(first 2) of day d, and the midday step S_mid (2 windows each side of the active midpoint), averaged over days.
Card level: share of periods with decay whose winner is N; RE mean of log λ; RE mean of S_N − S_mid.

**O2. Previous-centroid clock comparison.** Day-1 level M_1 with its CI; the clock comparison of O1 only where M_1's CI excludes 0 ("no remanence to clock" otherwise).

**O3. Two-time night step (powered secondary).** Per unit, OLS over pairs: C = cos(s_{iw}, s_{iw′}) on agent fixed effects + slot(w) + slot(w′) + ΔH bins ([0.5, 1), [1, 2), [2, 4), [4, 8), [8, 16) h) + β_N·N + β_G·N·(G − Ḡ_weeknight)/24 + β_gap·gap_own. Agent-cluster bootstrap (200). β_N is the night step at fixed active lag; β_G the extra drop per 24 h of break (weekends); β_gap the midday-gap placebo. Card level: RE means, sign counts.

**O4. Clock signatures.** Night clock: β_N < 0, β_G ≈ 0, β_gap ≈ 0, λ < 1, winner N. Active clock: β_N ≈ 0, winner H. Wall clock: β_N < 0, β_G < 0, β_gap < 0, winner W. Reset clock: winner R; within-day Δr effect < 0 (N2).

**O5. Robustness.** Both models; white32; no slot effects; first 3 instead of 5 days; ≥ 3 statements per window.

## Null / baseline
*Written 2026-10-04 20:45 UTC, before any real-data content statistic.*
- **Midday step** (S_mid; the H20 round-1b rule: ordinary in-day boundaries are the empirical placebo for a boundary statistic).
- **Own-gap placebo** (β_gap) and the **village-off midday breaks** (N3).
- **Weekend contrast** (β_G): a weekend is one break in N, three calendar nights, and ~3× the wall time of a weeknight.
- **Synthetic** (axis F, before real outcomes): the real window skeletons (agents, windows, clocks, slots) of every eligible period, with planted A_w series and window noise drawn from the real within-period residuals (permuted across windows): T-N (λ = 0.5 per night), T-H (τ_H = 5 active h, H54's scale), T-W (τ_W = 20 wall h), T-R (ρ matched to T-H), T-0 (no decay) and T-ToD (no decay, a morning pulse of +0.05 in the first slot). Δm = 0.13 (H54: day-1 excess 0.24, plateau 0.11). 50 replicates per period. Outputs: the clock confusion matrix, the false-night rate under T-H, T-W, T-ToD, and power for λ < 1 under T-N. O3: planted pair series under the same truths (size of β_N under T-H and T-ToD; power under T-N at a step of −0.03).

## Impostor table (STANDARDS.md §1)
| Impostor | How it could fake a night step | How H103 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | every morning starts with re-orientation (re-reading goals, summaries), so the first windows of each day differ from the last ones with no decay at all (T-ToD) | slot effects common to all days in every clock model; the midday step and own-gap placebos; the weekend contrast compares nights with nights; the synthetic T-ToD sizes the false-night rate | removed (if T-ToD's false-night rate is ≤ 0.1) |
| Exogenous field (goal, kickoff, operator) | the goal and kickoff sit in the prompt after NE08/NE13, so the field never switches off (no remanence, only a persistent field); operator messages arrive at day edges | the decay amplitude Δm is fitted above a plateau m_∞; decoy kickoffs; the previous-centroid series projects out the new field; NE43 (G51) removes the operator's bookends | partly (human messages are not regressed out) |
| Shared model priors (family, style) | style drifts with context position and resets at erasures (H46), which a reset at night would turn into a content step | DQ5 `style_resid`; agent fixed effects (O3); fixed incumbent composition (O1) | removed |
| Contemporaneous convergence | agents move together at day start because they read the same overnight backlog | not a coupling claim: the test is the clock of a field's decay; backlog reading at day start is part of the night mechanism under test | n/a |

## Prediction
*Written 2026-10-04 20:45 UTC, before running the analysis on real data.*

What I expect: H54's kickoff excess falls from 0.24 to a plateau of 0.11 within 1–2 active days (τ ≈ 5 active h), and H36 saw alignment relax within the kickoff day (0.64 → 0.29 over hours). Most of the decay therefore happens inside day 1, which the night clock cannot fit. Context and memory carry over the night in regime III (H69, H71), and content does not move at erasures (H46). My prior on HH331 is about 0.15.

- **P1 (HH331, the test):** among periods where the kickoff remanence decays, the night clock has the lowest SSE in ≥ 2/3, and the RE mean of log λ (nested model) is < 0 with the CI excluding 0, in both models. *Against (kill):* the active-hour model fits as well as or better than the night model (SSE_H ≤ SSE_N) in ≥ 1/2 of periods with decay. A negative counts as **failed** only if the synthetic clock-selection accuracy for T-N vs T-H is ≥ 0.8 at real counts; otherwise **inconclusive**. I predict **failed** (active hours win).
- **P2 (O2):** the previous-centroid day-1 level M_1's CI excludes 0 in ≤ 1/3 of transitions (little remanence to clock). *Against:* M_1 > 0 in > 1/3.
- **P3 (O3 night step):** the RE mean of β_N < 0 with the CI excluding 0 [0.5: a morning re-orientation may survive the slot effects]; β_G ≈ 0 (CI includes 0) [0.6]; β_gap ≈ 0 [0.6]. *Against the night clock specifically:* β_G < 0 (wall time matters) or β_gap < 0 of the same size as β_N (any break does it).
- **Effect that matters:** λ = 0.5 per night (half the remanence per night) and β_N = −0.03 (about a tenth of the typical within-day self-overlap range).
- **Per-period verdict (replication, O1):** *descriptive* if Δm's CI includes 0 (no remanence to clock); else *supported* if N wins and the nested λ's CI is below 1; *failed* if SSE_H ≤ SSE_N; *mixed* otherwise (N wins with λ's CI including 1, or W or R wins over both N and H). Units with only O3: *descriptive*, with β_N in the key numbers.
- **Overall reading (fixed now):** **Supported:** P1 passes. **Failed:** the kill holds with synthetic accuracy ≥ 0.8. **Mixed:** neither (for example, a night step in O3 without a night win in O1).

**Natives (dated predictions also in each folder).**
- **N1 G51 NE43:** β_N(after 08-04) − β_N(before) has a CI that includes 0 [0.6]. *Against:* the step changes with the CI excluding 0 (the bookends matter; confounded with the 08-05 room split).
- **N2 NE41 reset clock (regime III units):** the within-day reset term β_R (per own reset between the windows, at fixed ΔH bins) has a CI that includes 0, |β_R| < 0.005 [0.55]. *Against:* β_R < 0 with the CI excluding 0 (erasures demagnetize content).
- **N3 G04/G06 midday breaks:** self-overlap across each village-off break is within the range of same-day pairs at matched ΔH, not at the cross-night level [0.6]. Descriptive (4 agents, 2 events).

### Amendment 1 (2026-10-04 ~23:05 UTC, after the synthetic, before any real-data output was read)
*Disclosure: the code changes below were made before the real run; this text was written while the real run was starting (no output had been read).*
- **O3 design changed (synthetic, before real data).** With additive slot effects and the coarse lag bins written above, β_N came out at −0.10 to −0.14 under an active-hour truth and −0.07 to −0.13 under a time-of-day truth (no night effect planted). The design now uses **unordered slot-pair fixed effects** (10 classes), **0.5-h lag bins up to 8 h** plus a quadratic lag term, and a break-length term only for real weekend breaks (night > 30 h). Under this design the planted truths give β_N median +0.004 (active-hour; CI below 0 in 0/20), +0.003 (time-of-day; CI below 0 in 2/20, above 0 in 3/20), −0.17 (night jump; CI below 0 in 20/20), −0.22 with β_G < 0 in 14/20 (wall clock). Per-unit CIs are anti-conservative (10–25% two-sided under null truths), so card-level claims use the RE mean and the sign count.
- **O1 synthetic (as designed, amplitudes calibrated to H54's 0.24 → 0.11):** the night model beats the active-hour model in 86–91% of planted night truths and in 22–27% of planted active-hour truths (clock-selection accuracy ≈ 0.82 ≥ 0.8, so a negative P1 counts as **failed**). Verdict rates: night truth → supported 64%, mixed 27%, failed 9%; active-hour truth → failed 73%, mixed 18%, supported 9%; time-of-day truth → descriptive 100%; no decay → descriptive 95%. Wall-clock truths are often read as night (36%), so a night win is checked against β_G.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 active-hour decay; R2 wall-clock decay; R3 reset clock; R4 time-of-day field; R5 persistent field (no decay).
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (frozen, guarded, **not run**) targets the held-out goal periods with ≥ 3 days and the #51 tail.

Round 1 scores (2026-10-04; details in "Round 1 results"):

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | four clocks from the calendar, ledger resets and window times; same estimators in three regimes and both models; the kickoff field is a text-embedding proxy |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | single-exponential clock models; the data show a daily sawtooth (decay inside the day, partial recovery overnight) that none of the four models has |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | decay present beyond a constant in 22/31 periods; the night model loses to active-hour time in 17/22 (bge) / 16/22 (gte); no out-of-sample day test |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | the night step's sign (positive), the weekend term (negative, small) and the own-gap term (positive) are unfitted signatures; all three contradict HH331 |
| E interventional | predicts the change across a natural experiment | 1 | NE43 (bookends stop) and NE41 (resets inside the day) leave content unchanged, as predicted; the village-off break of 2025-06-18 behaves like a same-day pair (descriptive) |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | clock-selection accuracy 0.82 at real skeletons; time-of-day truth never read as decay; the O3 design was repaired before real data (A1); results agree in both models |
| G ground truth | agrees with known structure | 1 | the reset flags reproduce the 41-call cap (NE41); context carries over the night in regime III (H69) and the night shows no step |
| H comparative | beats the named rivals | 1 | R1 (activity clocks) beats the night clock; R2 is partly supported (weekend term); R3 vs R1 is not separable (resets track active time) |
| I transfer | holds in other same-mode periods, including the holdout | 1 | same reading in regimes I and III and both models; holdout not run |

**Scorecard: A1 B1 C1 D1 E1 F2 G1 H1 I1.**

## Results by goal period
O1 replication verdicts follow the card rule (*failed* = the active-hour clock fits as well as or better than the night clock).

| Period | Role | Verdict | Key numbers (bge) |
| --- | --- | --- | --- |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | descriptive | winner R; SSE_H/SSE_N 0.93; λ 0.05 [0.05, 1.50]; S_N +0.012, D +0.020; β_N(3) -0.539 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | descriptive | winner H; SSE_H/SSE_N 1.00; λ 1.30 [0.05, 1.50]; S_N +0.020, D -0.030; β_N(4a) +0.168; β_N(4c) +0.082 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | failed | winner R; SSE_H/SSE_N 0.70; λ 0.05 [0.05, 1.30]; S_N -0.015, D -0.031; β_N(5) +2.797 |
| [G06](goalperiod-subhypotheses/G06/README.md) | native | descriptive | winner H; SSE_H/SSE_N 0.79; λ 1.10 [1.05, 1.50]; S_N -0.010, D -0.005; β_N(6a) -0.161; β_N(6b) -0.080 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | failed | winner R; SSE_H/SSE_N 0.76; λ 1.50 [0.05, 1.50]; S_N -0.064, D +0.022; β_N(8) +0.114 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | failed | winner H; SSE_H/SSE_N 0.71; λ 1.50 [0.05, 1.50]; S_N +0.074, D -0.117; β_N(10b) -0.019 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | mixed | winner N; SSE_H/SSE_N 1.04; λ 1.05 [0.55, 1.50]; S_N -0.034, D +0.014; β_N(11) +0.206 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | winner R; SSE_H/SSE_N 0.99; λ 1.50 [1.05, 1.50]; S_N -0.065, D -0.051; β_N(12a) -0.076 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed | winner W; SSE_H/SSE_N 0.67; λ 0.05 [0.05, 1.50]; S_N +0.013, D -0.055; β_N(13) +0.001 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | descriptive | winner R; SSE_H/SSE_N 1.01; λ 0.75 [0.30, 1.35]; S_N -0.022, D +0.029; β_N(16) -0.117 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | descriptive | winner R; SSE_H/SSE_N 0.99; λ 1.35 [1.25, 1.50]; S_N +0.095, D -0.082; β_N(17) -0.061 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | winner W; SSE_H/SSE_N 0.91; λ 0.10 [0.05, 1.50]; S_N +0.046, D -0.081; β_N(18b) -0.194; β_N(18c) -0.034 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | winner R; SSE_H/SSE_N 0.61; λ 1.50 [1.50, 1.50]; S_N -0.015, D -0.062; β_N(19a) +0.125 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | supported | winner N; SSE_H/SSE_N 1.22; λ 0.05 [0.05, 0.85]; S_N +0.037, D -0.078; β_N(20c) +0.207; β_N(20d) -0.082 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | winner R; SSE_H/SSE_N 0.88; λ 1.50 [0.40, 1.50]; S_N +0.096, D -0.161; β_N(21a) +5.039 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | failed | winner H; SSE_H/SSE_N 0.98; λ 1.05 [1.03, 1.50]; S_N +0.000, D -0.025; β_N(24) +0.044 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | descriptive | winner W; SSE_H/SSE_N 1.01; λ 1.45 [1.00, 1.50]; S_N +0.060, D -0.059; β_N(25) -0.074 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed | winner R; SSE_H/SSE_N 0.97; λ 1.50 [1.40, 1.50]; S_N +0.180, D -0.247; β_N(26) -0.032 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | winner H; SSE_H/SSE_N 0.96; λ 1.40 [1.10, 1.50]; S_N +0.085, D -0.102; β_N(27) +0.002 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | failed | winner W; SSE_H/SSE_N 0.82; λ 0.05 [0.05, 1.50]; S_N +0.053, D -0.083; β_N(30b) -0.024 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | winner N; SSE_H/SSE_N 1.02; λ 0.60 [0.30, 1.50]; S_N -0.128, D +0.090 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | failed | winner H; SSE_H/SSE_N 0.98; λ 1.25 [1.05, 1.50]; S_N +0.128, D -0.147; β_N(33) +0.078 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | winner R; SSE_H/SSE_N 0.86; λ 1.50 [0.05, 1.50]; S_N +0.052, D -0.062; β_N(35) +0.000 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | winner N; SSE_H/SSE_N 1.10; λ 1.10 [0.05, 1.50]; S_N -0.023, D -0.012; β_N(37) -0.002 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | descriptive | winner W; SSE_H/SSE_N 0.87; λ 0.05 [0.05, 1.50]; S_N +0.015, D -0.035; β_N(38a) -0.014; β_N(38b) -0.049 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | failed | winner R; SSE_H/SSE_N 0.97; λ 1.50 [1.10, 1.50]; S_N +0.030, D -0.049; β_N(39) -0.019 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | winner N; SSE_H/SSE_N 1.07; λ 0.75 [0.35, 1.15]; S_N +0.036, D -0.063; β_N(40) -0.057 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | winner R; SSE_H/SSE_N 0.95; λ 1.05 [0.40, 1.50]; S_N -0.008, D -0.001; β_N(41) -0.018 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | winner H; SSE_H/SSE_N 0.96; λ 1.45 [0.05, 1.50]; S_N -0.008, D +0.004; β_N(42b) -0.067 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | descriptive | winner R; SSE_H/SSE_N 1.00; λ 1.50 [0.05, 1.50]; S_N -0.003, D -0.016 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | descriptive | winner N; SSE_H/SSE_N 1.03; λ 0.30 [0.05, 1.30]; S_N +0.013, D -0.013; β_N(51a) -0.018; β_N(51c) +0.016 |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | supported | Δβ_N +0.023 [−0.017, +0.062] (gte +0.021) |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native | supported | β_R +0.0003 [−0.0011, +0.0018] per reset, 15 units (gte +0.0008) |

## Round 1 results (2026-10-04, exploratory, non-holdout)
*Scripts: `scheme/build.py`; `analysis/{h103lib, synthetic, run, period_folders, figures, estimates_rows, confirm}.py`. Numbers: `data/processed/H103-nights-demagnetize/results/{card,o1,o2,o3,natives}_<model>_style_resid.json`, `synthetic/synthetic.json`. Figures: `figures/summary_obs.pdf`, `figures/summary_synthetic.pdf`. 24,470 eligible agent × 30-min windows; 31 O1 periods; 23 O2 transitions; 41 O3 units; both embedding models.*

### Synthetic validation (axis F, before real outcomes)
See Amendment 1. O1: clock-selection accuracy (night vs active hours) ≈ 0.82; false "supported" rate under an active-hour truth 0.09; a time-of-day field is read as no decay in 100%. O3 (repaired design): β_N ≈ 0 under active-hour and time-of-day truths, −0.17 under a night-jump truth (20/20 detected).

### Outcome vs prediction
| # | Prediction (locked 20:45 UTC) | Observed (bge / gte) | Verdict |
| --- | --- | --- | --- |
| P1 | night clock best in ≥ 2/3 of periods with decay; RE ln λ < 0 | night best 5/22 / 3/22; SSE_H ≤ SSE_N in 17/22 / 16/22 (kill); RE ln λ +0.06 [−0.11, +0.23] / −0.19 [−0.38, +0.00] | **failed** (kill holds; accuracy 0.82 ≥ 0.8) |
| P2 | previous-centroid day-1 level > 0 in ≤ 1/3 | 11/23 / 10/23 | **failed** (more remanence than expected; too weak to clock: 17–18/23 descriptive) |
| P3a | RE β_N < 0 | −0.001 [−0.023, +0.021] / −0.002 [−0.028, +0.024]; CI < 0 in 7/41, > 0 in 8/41 | **failed** (no night step at fixed active lag) |
| P3b | β_G ≈ 0 | −0.017 [−0.030, −0.005] / −0.014 [−0.028, −0.000] per extra 24 h (17 units with weekends) | **failed (small)**: a weekend lowers self-overlap a little more than a night |
| P3c | β_gap ≈ 0 | +0.099 [+0.055, +0.142] / +0.100 [+0.045, +0.154] | **failed, opposite to the wall clock**: an agent's own idle gap *raises* overlap at matched active lag |
| N1 NE43 | Δβ_N CI includes 0 | +0.023 [−0.017, +0.062] / +0.021 [−0.020, +0.062] | **supported** |
| N2 NE41 | β_R CI includes 0, \|β_R\| < 0.005 | +0.0003 [−0.0011, +0.0018] / +0.0008 [−0.0003, +0.0020] per reset (15 units) | **supported** |
| N3 G06 | across-break overlap at the same-day level | 2025-06-18: 0.37 across vs 0.35 same-side vs 0.52 cross-night (bge); 2025-06-29: no agent posted on both sides | **descriptive** |

**Robustness (O5, bge).** Without slot effects: decay in 23/31, SSE_H ≤ SSE_N in 0.87, night wins 0.09, RE ln λ +0.10 [−0.04, +0.24]. white32 (no style residualization): decay in 20/31, SSE_H ≤ SSE_N in 0.85, RE ln λ −0.16 [−0.42, +0.10]; β_N +0.003 [−0.019, +0.026]; β_gap +0.094 [+0.059, +0.128]. The kill and the null night step survive every variant.

**Model-free steps (O1).** The kickoff alignment falls inside the day (day drift D median −0.055 bge / −0.023 gte in regime I; −0.014 / −0.041 in regime III) and partly recovers overnight: S_N − S_mid RE +0.037 [+0.009, +0.065] / +0.028 [+0.007, +0.050] (31 periods). The night *raises* the kickoff alignment relative to a midday split. The synthetic time-of-day truth also produces a positive S_N − S_mid (+0.11), so this step is consistent with a morning re-orientation toward the goal, not with demagnetization.

**Overall reading (rule fixed before data):** the kill holds with synthetic accuracy ≥ 0.8, so the card verdict is **failed**. Nights do not demagnetize the content magnetization. The decay runs on activity clocks (active hours or resets, not separable here), and each morning re-magnetizes toward the goal a little.

### Post hoc (labelled)
- **The agent's own call clock.** β_gap > 0 means that an hour in which the agent itself was idle does not age its content. Together with β_R ≈ 0 (erasures do not age it either) and β_N ≈ 0, the simplest reading is that content ages with the agent's own work (calls), consistent with H40's per-call clock. A direct test would put the agent's own call count between the windows in the O3 regression.
- **Weekend term.** A weekend break costs about −0.015 in self-overlap beyond a weeknight, about the same as one or two extra active hours. Wall time matters a little, nights per se do not.
- **gte λ.** gte's nested night factor is 0.83 [0.68, 1.00]; bge's is 1.06. The night step is not robust in either direction.

### Answer to the question
No. A remanent field (the kickoff, the previous goal's state) does not fall in steps at night boundaries. Its decay happens during the working day, and across the night the alignment with the current goal rises a little (re-orientation). At fixed active lag an agent's content is as similar across a night as within a day; context resets (41-call cap) and the end of the operator's bookends change nothing; an agent's own idle time does not age its content.

## Round 2 redirects (2026-10-04)
- **H103-R1.** Put the agent's own call count (the H40 clock) into the O3 regression next to active hours and resets; test whether calls absorb the active-hour decay.
- **H103-R2.** Model the daily sawtooth explicitly: an activity-clock decay plus a morning re-orientation pulse toward the prompt-resident goal; compare eras before and after NE08/NE13 (goal and kickoff in the prompt).
- **H103-R3.** Rerun O2 with H82's remanence series once it exists, to see whether its veteran/newcomer split changes the clock.
- **H103-R4.** Run `confirm.py` after Vivian's sign-off and the ledger disclosure.

## Notes
- 2026-10-04 20:45 UTC: card written before any content statistic. Holdout masked with `holdout_mask`; held-out counts never printed. #23 excluded (H10's blind pair).
- 2026-10-04 ~23:05 UTC: Amendment 1 (O3 design repaired after the synthetic, before real data; its text was written while the real run was starting, disclosed above).
- H82 had no outputs when this ran; H103 built its own previous-centroid series with H82's construction. No H82 code or data was used.
- Per-unit O3 estimates in short-day regime-I units are poorly identified (β_N SE up to 2.9 in #21a); the RE mean weights them down.
- The 2025-06-29 village-off break (774 min) had no agent posting on both sides, so N3 has one usable event.
