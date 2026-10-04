# H124: Four agents for weeks: an exact kinetic Ising benchmark for the mean-field approximations (#4, #6)

**Status:** exploratory round 1 **done (2026-10-04): mixed. The 10% claim fails; the mean-field inversions work only when agents' own states are not persistent.** Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH365. Card, observables, nulls and predictions written 2026-10-04 21:59–22:02 UTC, before any real-data statistic; amendment A1 (after the synthetic, before real data) dated below.
- **Per-call talk clock, 9 closed-roster N = 4 units:** TAP or MS within 10% of exact ML in 1/9 units (4c, the only unit with max self-coupling J_ii ≤ 0.6: TAP 0.05, MS 0.03, nMF 0.08). Elsewhere (J_ii 0.86–1.22) TAP has no solution on 25–75% of rows, MS overshoots |J| ×1.2–3.8 (ε_J median 1.28) and naive MF shrinks it (ε_J median 0.25, shrink 0.45–0.95).
- **Couplings are at noise level:** off-diagonal ML J beyond the circular-shift null in 2/9 units; ML's own bootstrap noise ν_J 0.6–1.1. Self-couplings carry the model.
- **1-min grid:** talk (weak persistence) MS within 10% in 6/9 units; activity (strong persistence) in 0/9.
- **Synthetic (N = 4 on #4/#6 schedules, N = 21 on #51's):** the same persistence law; exact ML recovers true J within 0.06–0.20; the best-method ranking against truth matches the ranking against ML in 15/16 cells and carries from N = 4 to N = 21.
- Natives: N1 (#4 vs #6) failed; N2 (G08 data length) mixed. Scorecard A1 B1 C1 D1 E0 F2 G1 H1 I1. `confirm.py` (#1, #9) frozen and guarded; dry-run only, **not run**.
**Fields:** stat mech (inverse kinetic Ising, mean-field theory), inference methods
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (EP of the kinetic Ising, max-ent bound). Cited, not stored (no notes file; flagged for `literature/`): Aguilera, Moosavi & Shimazaki, *Nat. Commun.* 12, 1197 (2021)† (Plefka expansions for asymmetric kinetic Ising: naive = Plefka[t−1,t] first order, TAP = Plefka[t−1,t] second order, Plefka[t] ≡ Mézard–Sakellariou, Plefka2[t]); Roudi & Hertz, *PRL* 106, 048702 (2011)† (kinetic TAP inversion); Mézard & Sakellariou, *J. Stat. Mech.* L07001 (2011)† (Gaussian-field inversion, exact for asymmetric SK).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t); Regime; Action; Agent state (binary variant); Entropy production / irreversibility (here the model EP of a fitted kinetic Ising). **New named variants proposed** (not edited into DEFINITIONS.md; defined under Model): *per-call talk spin*, *1-min talk / activity spin (parallel grid)*, *mean-field inverse estimators nMF / TAP / MS*, *coupling error ε_J*, *model EP σ_J and its error ε_σ*.
**Question served:** **Q1** (what couples agents? the method that measures couplings at large N), as a method benchmark; **Q6** second (the EP of the fitted kinetic model).
**From:** HH365 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (kinetic Ising, ML fit, mean-field forward and inverse)
**Data inputs (shared tables only):** `call_windows` (regime-I calls: agent, `t_call`, `talk`, `ctx_mode`, `turn_id`), `activity_bins_fixed` (1-min talk and activity; never the old `activity_bins`), `period_units`, `roster`, `calendar`. For the N = 21 synthetic: `call_windows` of non-holdout #51-head days (order and counts only). No text. Every row passes `holdout_mask` and `~holdout`.

## Source HH (verbatim from the HH list, including refinements)
- **HH365 · Four agents for weeks: an exact kinetic Ising benchmark for the mean-field approximations (#4, #6).** With N = 4 and weeks of data, the full kinetic Ising likelihood is exact and cheap. That lets us test the mean-field approximations (naive, TAP, Plefka orders; Aguilera et al. 2021) on real data before trusting them at N = 21.
  - *Prediction:* TAP or second-order Plefka recovers the exact J and the EP bound within 10% at N = 4; naive mean field does not. The ranking carries to synthetic N = 21 worlds built on #51's schedule.
  - *Check:* exact ML vs approximations on #4 and #6 (merch competition) per call; then synthetic scaling.
  - *Kill:* no approximation gets within 25%. Then the large-N results that use them need the exact or pseudo-likelihood route.
  - *Impostors:* n/a (method benchmark); scheduler field removed as usual.
  - *Models:* 02 · *Builds on:* H25, H67, H90

## Standards (2026-10-04)
**Question served:** Q1 (method), then Q6.

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes, for any coupling reading | A method benchmark compares estimators on the same data, so the scheduler biases all of them alike. For the 1-min grid each day is trimmed to the all-present window (DQ8, `nulls.all_present_window`) and the first and last 10% of each day's calls are dropped on the per-call clock. No coupling claim is made. | removed (as usual) |
| Exogenous field (kickoff, goal, operator) | no claim | A shared drive enters J identically for every estimator. No coupling or influence claim; the N1 native's J̄ contrast is descriptive. | n/a (benchmark); open for N1 |
| Shared model priors | no claim | Same reason; four agents of three or four families. | n/a |
| Contemporaneous convergence | no claim | Same reason; lagged fits only. | n/a |

**Two layers:** replication on every non-holdout closed-roster N = 4 unit (G02, G03, G04a, G04c, G05, G06a, G06b, G07, G08); natives N1 (G04 cooperation vs G06 competition), N2 (G08 data-length curve). Plus the synthetic N = 4 (real #4/#6 schedules) and N = 21 (real #51-head schedule) worlds.
**Confirm script:** `analysis/confirm.py`, frozen and guarded; not run.

## Question
At N = 4, where the exact kinetic Ising likelihood is cheap, how close do the mean-field inversions (naive, TAP, Mézard–Sakellariou) come to the exact couplings and to the model's entropy production, and does their ranking hold at N = 21 on a real schedule?

## Model
**From:** `physics-models/02-nonequilibrium-ising` (kinetic Ising: each spin's transition is a logistic regression on the previous configuration; mean-field forward version).

**Kinetic Ising (both clocks).** For an update of agent i from configuration s (±1 spins, own spin included): P(s_i' = +1 | s) = 1/(1 + e^{−2H_i}), H_i = h_i + Σ_j J_ij s_j (J_ii = self-coupling = persistence).
- **Per-call clock (primary; the HH's "per call").** Rows of agent i are i's calls: s_i' = *per-call talk spin* (+1 if the call produced chat, `talk`); s = every agent's latest talk spin just before the call (own previous call included). Asynchronous: one agent per row.
- **1-min parallel grid (companion; the setting of Aguilera et al. 2021).** *1-min talk spin* (talk > 0) and *1-min activity spin* (state ≥ 3) from `activity_bins_fixed`; all agents update every minute; rows inside each day's all-present window.

**Inverse estimators (row by row; m_i' = ⟨s_i'⟩ over i's rows, m_j, C = Cov(s) over i's rows, D_i = Cov(s_i', s) over i's rows, B_i = D_i C⁻¹):**
- **Exact ML:** per-row logistic regression (Newton, L2 10⁻⁴), the reference. Exact here because N = 4 (no partition function in the kinetic likelihood; nothing is approximated).
- **nMF** (naive; Plefka[t−1,t] first order): J_i = B_i / (1 − m_i'²); h_i = atanh m_i' − Σ_j J_ij m_j.
- **TAP** (Plefka[t−1,t] second order; Roudi & Hertz 2011): J_i = B_i / a_i with a_i = (1 − m_i'²)[1 − (1 − m_i'²) Σ_j J_ij² (1 − m_j²)], solved by fixed point; h_i = atanh m_i' − Σ_j J_ij m_j + m_i' Σ_j J_ij²(1 − m_j²). Fails (no solution) when the bracket ≤ 0; failures are counted.
- **MS** (Plefka[t] ≡ Mézard–Sakellariou Gaussian-field inversion): J_i = B_i / a_i, a_i = ∫Dx [1 − tanh²(g_i + x√Δ_i)], m_i' = ∫Dx tanh(g_i + x√Δ_i), Δ_i = J_i C J_iᵀ; (g_i, a_i) by fixed point; h_i = g_i − Σ_j J_ij m_j.
- **Not implemented:** Plefka2[t] (Aguilera 2021's new second-order expansion). The paper is not in `literature/`, and I will not write its equations from memory. TAP is the second-order Plefka expansion tested here.
- **Model EP σ_J** = Σ_{i,j} (J_ij − J_ji) D_ij (D_ij = ⟨s_i' s_j⟩ − m_i' m_j; self-couplings cancel). Exact for the stationary parallel kinetic Ising (nats per step). On the per-call clock the same algebra is an *asymmetry index* (labelled so), not a full EP.

## Data scheme (`scheme/build.py`)
- **Inputs:** `call_windows` (units above, non-holdout), `activity_bins_fixed`, `period_units`, `roster`; #51-head `call_windows` for the N = 21 synthetic schedule.
- **Transform:**
  1. Per unit × day, calls sorted by (`t_call`, `turn_id`); the four roster agents; drop the first and last 10% of each day's calls; drop steps before all four agents have called once.
  2. Per-call design: for each call of agent i, y = talk spin, X = the four latest talk spins before it.
  3. 1-min grid: talk and activity spins per agent-minute inside the all-present window, pairs (t, t+1) within a day.
- **Output:** `data/processed/H124-small-n-meanfield-benchmark/` with `percall/<unit>.parquet` (day, agent, y, x1..x4; int8), `grid/<unit>.npz`, `results/` (fits, errors, bootstraps), `synthetic/`, `_provenance.json`. Expected < 20 MB.
- **Regimes covered:** regime I (#2–#8 closed-roster units); regime III #51 head (schedule only, synthetic).

## Observables
Per unit × clock × channel, for each approximation k ∈ {nMF, TAP, MS} against exact ML:
1. **Coupling error ε_J** = ‖J_k − J_ML‖_F / ‖J_ML‖_F over **off-diagonal** entries (primary); all entries (with self-couplings) secondary.
2. **EP error ε_σ** = |σ_J(J_k) − σ_J(J_ML)| / |σ_J(J_ML)| (with the same empirical D).
3. **Exact ML's own noise** ν_J: median over 200 day-bootstrap replicates of ‖J_ML,b − J_ML‖_F / ‖J_ML‖_F (off-diagonal). An approximation error below ν_J is not resolvable.
4. Day-bootstrap 95% intervals for ε_J and ε_σ (both estimators refitted on each replicate).
5. Synthetic: the same errors against the **true** J, and the ranking of the three approximations.

## Null / baseline
- **Within-data reference:** exact ML is the truth proxy; ν_J is the noise floor.
- **Coupling-free null (for reading the real J, not the benchmark):** each agent's day sequence circularly shifted against the others (20 reps); off-diagonal ‖J_ML‖ under the shift gives the scale of pure-noise couplings. If the real off-diagonal J is inside that null, ε_J compares noise with noise and the benchmark on that unit is "uninformative" (reported, not scored).
- **Synthetic truth** (axis F, below).

## Synthetic validation plan (axis F; `analysis/synthetic.py`; run before real-data errors)
- **S4 (N = 4, real schedules):** the per-call actor sequence and call counts of G04c and G06 (order only). J_ii from a grid {0.5, 1.5} (persistence), off-diagonal J entries N(0, σ_J²) with σ_J ∈ {0.1, 0.3, 0.6}, asymmetric; h_i set for a 25% talk rate. 20 worlds per cell. Errors of ML, nMF, TAP and MS against the true J.
- **S21 (N = 21, real #51-head schedule):** the per-call actor sequence of 10 non-holdout #51-head days with 21 agents most present (order and counts only). Sparse directed J (each agent 3 random partners, |J| ~ σ_J ∈ {0.15, 0.5}), J_ii ∈ {0.5, 1.5}. 10 worlds per cell.
- **Pass:** (a) exact ML recovers the true J with ε_J ≤ 0.2 at the real N = 4 counts for σ_J ≥ 0.3 (else the real benchmark is limited by data, not by the approximations); (b) the ranking of approximations against truth equals their ranking against exact ML (so the real-data comparison against ML is valid).

## Prediction
*Written 2026-10-04 ~22:02 UTC, before any real-data fit. Credences are mine.*

| # | Statistic (per-call talk, G04 and G06 units unless stated) | HH prediction (tested) | My expectation and credence | Kill / counts against |
| --- | --- | --- | --- | --- |
| P1 | best of TAP / MS: ε_J and ε_σ | ≤ 0.10 | ≤ 0.10 in ≥ 1/2 of the G04/G06 units (0.35). Persistence (large J_ii) makes the local field bimodal, which hurts every Gaussian/expansion method | **Kill (HH):** no approximation ≤ 0.25 on ε_J in ≥ 1/2 of units |
| P2 | nMF ε_J | > 0.10 | > 0.10 (0.75); it underestimates J magnitude by the factor ⟨1 − tanh²⟩/(1 − m²) | nMF ≤ 0.10 everywhere |
| P3 | ranking | TAP or MS < nMF | MS ≤ TAP < nMF on ε_J in ≥ 2/3 of units (0.55); TAP fails to converge in some rows (0.4) | nMF best in ≥ 1/2 of units |
| P4 | ranking carries to S21 | yes | same ranking at N = 21 (0.6); all errors smaller at weak σ_J (mean-field improves with N and with weaker J) (0.7) | ranking reverses at N = 21 |
| P5 | resolvability | (not stated) | real off-diagonal J inside or near the shift null in ≥ 1/2 of units (regime-I couplings are weak: H67 g_lag ≈ 0.005) (0.5), so the real-data benchmark is set by the self-couplings | — |
| P6 | 1-min grid (companion) | (same as P1–P3) | activity spins: nMF ε_J > 0.25 (activity is very persistent minute to minute) (0.6) | — |

**Replication rule:** across the nine closed-roster units, P1 is "supported" if TAP or MS is within 10% (ε_J and ε_σ) in ≥ 2/3 of informative units, "failed" (HH killed) if no approximation is within 25% in ≥ 2/3, else "mixed".

## Native tests (each with its own prediction, written 2026-10-04 ~22:02 UTC)
- **N1 · #4 cooperation vs #6 competition (mode C vs mode K, same four-agent scale).** #4: one shared story and event; #6: each agent its own merch store, most profit wins. *Prediction:* the exact-ML mean off-diagonal talk coupling J̄ is lower in G06 than in G04 (0.55); the approximation ranking is the same in both (0.7). *Against:* J̄(G06) > J̄(G04) beyond the bootstrap CI.
- **N2 · G08 data-length curve (18 days, the longest closed-roster N = 4 unit).** Subsample 2, 4, 8 and 16 days (20 draws each). *Prediction:* the approximations' bias against full-data ML is flat in days, while ML's own noise ν_J falls ~1/√days; ν_J drops below the best approximation's bias by 8 days (0.5). *Against:* bias that shrinks with days (then it was noise, not bias).

## Rivals
- **R0 (HH):** TAP or second-order Plefka within 10%; naive not.
- **R1 all approximations good:** weak couplings and moderate fields make every inversion exact to first order (ε ≤ 0.10 for nMF too).
- **R2 all approximations bad:** strong persistence and sparse spins make the local field non-Gaussian; no inversion within 25%; use exact or pseudo-likelihood at large N.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0–R2 above.
**Locked holdout used for confirmation:** regime-I N = 4 held-out goal period #1 (units 1a, 1c, 1d, 1e; 1b is one day) and #9 (N = 4, 3 days), frozen in `analysis/confirm.py`.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Per-call talk spin from `call_windows.talk`, regressors = latest talk of the four agents; 1-min talk/activity from `activity_bins_fixed`. Regime I only (N = 4 exists only there); four to five model families per unit, not separated. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Day folds and day bootstraps absorb day-to-day drift; edges cut. Markov order beyond one call not tested. The update order is the real per-call schedule (H123 audit: self-clocked asynchronous). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Leave-one-day-out log-likelihood: exact ML is best in every unit with ≥ 4 days; stratified nMF (A1) within 0.0044 nats/call; plain nMF loses 0.005–0.061, TAP 0.013–0.11, MS 0.011–0.62. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | P2's predicted direction holds unfitted: nMF underestimates J magnitude (shrink 0.45–0.95 in 9/9 units). The persistence law was seen first in the synthetic (A1) and then held in 9/9 real units. |
| E interventional | predicts the change across a natural experiment | 0 | Method benchmark; N1 (cooperation vs competition) is descriptive and failed. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | S4 (280 worlds on 4c/6b schedules) and S21 (40 worlds on the #51-head schedule, N = 21): ML recovers truth within 0.06–0.20 at σ_J ≥ 0.3; best-method agreement truth vs ML 15/16 cells; code validated on a dense world without self-coupling (MS ≈ ML, TAP good where defined). |
| G ground truth | agrees with known structure | 1 | Reproduces the known limits of the expansions (TAP's existence bound S/a₀ ≤ 4/27; MS exact only for Gaussian fields). No ground-truth village couplings exist. |
| H comparative | beats the named rivals | 1 | R0 (HH) holds only at weak persistence (1/9 units); R1 (all good) fails; R2 (all bad) holds for plain TAP/MS when J_ii > 0.6 but not for nMF (≤ 0.25 in 5/9 units). |
| I transfer | holds in other same-mode periods, including the holdout | 1 | 9 regime-I units and S21. Holdout (#1, #9) not run. |

**Scorecard plan:** A from the spin definitions (two clocks); B from Markov-order and stationarity checks of the per-call fit (held-out day log-likelihood of ML vs ML + lag-2 terms); C from the held-out day log-likelihood of each estimator (does an approximation lose predictive power?); D from P2's predicted shrink factor; E n/a (benchmark; N1 is descriptive); F from S4/S21; G from known structure (#6 competitors); H from R0–R2; I from replication over the nine units and S21.

## Amendment A1 (2026-10-04 22:34 UTC; after the synthetic, before any real-data error)
- **What the synthetic showed** (`analysis/synthetic.py`, S4/S21, 280 worlds): with any self-coupling (J_ii ≥ 0.5, i.e. persistence of the own spin) the plain inversions break. TAP has no real solution (S/a₀ > 4/27) in nearly every row; MS overshoots (ε_J vs truth 0.2–11); nMF shrinks |J| (ε_J 0.25–0.84). On a dense world without self-coupling the code behaves as theory says (MS ≈ ML, ε 0.03–0.16; TAP good where it exists; nMF shrinks with J₀), so the failure is the persistence, not the code.
- **Added variants (not in the HH):** nMF|s, TAP|s and MS|s invert the off-diagonal couplings within each stratum of the agent's own previous spin, and read J_ii from the stratum fields (`h124lib.strat_row`). They are scored next to the plain methods; the HH's P1–P3 are still scored on the plain methods.
- **Synthetic pass criteria:** (a) ML recovers the true J within ε_J ≤ 0.2 for σ_J ≥ 0.3 on both N = 4 schedules (0.06–0.20): **pass**. (b) ranking against truth vs against ML: reported in Results.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | exploratory (replication) | failed | 2: J_ii≤1.08, nMF 0.48, TAP 0.03 (1/4 rows), MS 2.45 |
| [G03](goalperiod-subhypotheses/G03/README.md) | exploratory (replication) | failed | 3: J_ii≤1.06, nMF 0.57, TAP 0.04 (1/4 rows), MS 1.83 |
| [G04](goalperiod-subhypotheses/G04/README.md) | exploratory (primary + N1) | mixed | 4a: J_ii≤1.05, nMF 0.39, TAP 0.04 (1/4 rows), MS 1.28; 4c: J_ii≤0.51, nMF 0.08, TAP 0.05 (4/4 rows), MS 0.03 |
| [G05](goalperiod-subhypotheses/G05/README.md) | exploratory (replication) | failed | 5: J_ii≤0.89, nMF 0.17, TAP 0.04 (3/4 rows), MS 0.31 |
| [G06](goalperiod-subhypotheses/G06/README.md) | exploratory (primary + N1) | failed | 6a: J_ii≤1.00, nMF 0.20, TAP 0.06 (2/4 rows), MS 1.20; 6b: J_ii≤1.22, nMF 0.30, TAP 0.10 (2/4 rows), MS 3.83 |
| [G07](goalperiod-subhypotheses/G07/README.md) | exploratory (replication) | failed | 7: J_ii≤1.05, nMF 0.21, TAP 0.15 (2/4 rows), MS 3.59 |
| [G08](goalperiod-subhypotheses/G08/README.md) | exploratory (replication + N2) | failed | 8: J_ii≤0.86, nMF 0.25, TAP 0.02 (2/4 rows), MS 0.82 |

## Results
### Exploratory round 1 (2026-10-04; `scheme/build.py`, `analysis/synthetic.py`, `analysis/run.py`, `analysis/summarize.py`; data `data/processed/H124-small-n-meanfield-benchmark/`)
Old → new: this is round 1. Figure: `figures/benchmark.pdf`. ε_J = off-diagonal relative Frobenius error; "cover" = share of rows where the method has a solution.

**Synthetic (before real data; A1).** Median ε_J against the true J:

| World | ML | nMF | TAP (cover) | MS | nMF\|s |
| --- | --- | --- | --- | --- | --- |
| S4 4c, J_ii 0.5, σ_J 0.3 | 0.07 | 0.33 | ≈ 0 rows | 0.27 | 0.18 |
| S4 4c, J_ii 1.5, σ_J 0.3 | 0.17 | 0.81 | ≈ 0 rows | 1.94 | 0.25 |
| S21, J_ii 0.5, σ_J 0.15 | 0.25 | 0.30 | 0 rows | 0.27 | 0.25 |
| S21, J_ii 1.5, σ_J 0.5 | 0.22 | 0.84 | 0 rows | 5.25 | 0.32 |
| Dense N = 21, J_ii 0, J₀ 0.3 / 1.0 | 0.34 / 0.17 | 0.32 / 0.41 | 1.0 / 0 cover | 0.34 / 0.24 | — |

Against ML (same data) at J_ii 0.5 and weak σ_J, MS and nMF|s agree within 0.08 at N = 4 and N = 21, nMF within 0.20–0.24: the same order at both sizes.

**Real data, per-call talk clock (9 units).**

| Statistic | Result |
| --- | --- |
| Off-diagonal J beyond the circular-shift null | 2/9 units (2, 4a) |
| ML bootstrap noise ν_J (units with ≥ 3 days) | 0.58–1.10 |
| Max self-coupling J_ii | 0.51 (4c); 0.86–1.22 elsewhere |
| TAP or MS within 10%, full cover | 1/9 (4c: TAP 0.05 [0.03, 0.11], MS 0.03 [0.02, 0.06]) |
| nMF within 10% / 25% | 1/9 / 5/9; shrink 0.45–0.95 (median ε_J 0.25) |
| TAP row cover | 0.25 (2, 3, 4a), 0.5 (6a, 6b, 7, 8), 0.75 (5), 1.0 (4c); ε_J 0.02–0.15 on covered rows |
| MS | overshoot 1.0–3.8; ε_J median 1.28 (0.03–3.8) |
| Held-out LL gap to ML (≥ 4 days) | nMF −0.005 to −0.061; TAP −0.013 to −0.11; MS −0.011 to −0.62; nMF\|s −0.000 to −0.004 nats/call |
| 1-min grid: MS within 10% | talk 6/9; activity 0/9 |

**Predictions vs results.**

| # | Prediction | Result | Verdict |
| --- | --- | --- | --- |
| P1 (HH) | TAP or MS within 10% (ε_J and ε_σ) in ≥ 1/2 of G04/G06 units | 1/4 (4c) | **failed** |
| Kill (HH) | no method ≤ 0.25 in ≥ 1/2 of G04/G06 units | 2/4 with none (4a, 6b): at the threshold; 4/9 in the replication set (< 2/3) | met at threshold (primary), not met (replication) |
| P2 | nMF ε_J > 0.10 | 8/9 units | supported |
| P3 | MS ≤ TAP < nMF in ≥ 2/3 | only in 4c; nMF is the best full-cover plain method in 8/9 | failed |
| P4 | ranking carries to N = 21 | yes (synthetic, 15/16 cells best-method agreement) | supported |
| P5 | off-diagonal J near the null in ≥ 1/2 | 7/9 | supported |
| P6 | 1-min activity nMF > 0.25 | 7/8 units with a grid > 0.25 (all 8 > 0.10) | supported |
| N1 | J̄(G06) < J̄(G04); same ranking | no difference; ranking follows persistence | failed |
| N2 | ν_J below best bias by 8 days | flat bias (supported); crossover 16–18 days | mixed |

**Reading.** The control parameter is persistence, not N. A persistent own spin makes the local field bimodal (±J_ii), which breaks the Gaussian (MS) and small-coupling (TAP) assumptions; naive MF fails more gently because it only rescales. In this village the per-call talk spin is persistent (agents in chat mode keep talking, agents in sessions keep working), so the plain inversions are unreliable on the call clock. Exact logistic ML is cheap at N = 21 (seconds per fit) and is the route to use.

**Impostors.** Not applicable to a method benchmark (all estimators see the same data). No coupling claim is made; N1's J̄ is descriptive.

**Claim that stands:** on the per-call talk clock, mean-field inversions match exact kinetic Ising ML only when self-coupling is weak (max J_ii ≤ 0.6: 1/9 units, TAP 0.05, MS 0.03); with persistent own spins (J_ii 0.86–1.22, 8/9 units) TAP has no solution on 25–75% of rows, MS overshoots |J| up to ×3.8 and naive MF shrinks it (ε_J median 0.25), and synthetic N = 4 and N = 21 worlds on real schedules show the same law. Excluded: ε_σ (the reference EP is at noise level), N1 (failed), the N2 crossover (later than predicted), the stratified variants (A1, not in the HH), units 2, 3, 7 intervals and log-likelihood (≤ 3 days).

## Confirmatory predictions (C-*): for the locked holdout, frozen 2026-10-04 after round 1, not run (`analysis/confirm.py`)
Targets: held-out N = 4 units 1a, 1c, 1d, 1e (#1) and 9 (#9).
- **C1 persistence law:** units with max J_ii > 0.6 have TAP undefined on ≥ 1 row and MS ε_J > 0.25; units with max J_ii ≤ 0.6 have min(TAP, MS) ε_J ≤ 0.10 with TAP on every row; holds in ≥ 4/5 units.
- **C2:** nMF ε_J > 0.10 in ≥ 2/3 of units.
- **C3:** off-diagonal ML J inside the shift-null q95 in ≥ 1/2 of units.
- **C4:** 1-min talk grid, MS ε_J ≤ 0.10 in ≥ 1/2 of units with ≥ 3 grid days.
- **C5:** nMF|s within 0.01 nats/call of ML (held-out LL) in ≥ 2/3 of units with ≥ 5 days.
- Dry run on two relabelled stand-in units passed. New estimator family `kinetic_ising_inverse`; #1 and #9 are planned by H03, H19, H81, H97 and others (disclose).

## Round 2 redirects
**What the direction is really after:** which coupling estimator to trust at N = 21; round 1 says exact (or pseudo-) likelihood on the call clock, because own-state persistence breaks the mean-field inversions.
- **H124-R1. Large-N rule.** Use per-row logistic ML or pseudo-likelihood for kinetic Ising fits on the call clock, never plain TAP or MS when J_ii > 0.6; report J_ii with every fit.
- **H124-R2. Plefka2[t].** Add Aguilera 2021's second-order Plefka[t] once its notes are in `literature/`, and test it on bimodal (persistent) fields.
- **H124-R3. Real couplings.** Repeat the benchmark where couplings exceed noise (regime-III named talk, H50), or with partial pooling across N = 4 units (exception d).
- **H124-R4. Markov order.** Add lag-2 own and partner terms and compare held-out log-likelihood (axis B).

## Notes
- 2026-10-04: units 2 and 7 have two days; their bootstrap intervals and ν_J are degenerate. Unit 3 (3 days): plain nMF beats ML on held-out LL (+0.13 nats/call), a small-sample artifact of ML on a near-separable day.
- Estimates: 238 rows in `per_period_estimates` (ε_J per method and clock, ν_J, ‖J_off‖ vs null, J̄, max J_ii, LL gaps, N2 curve).
- 2026-10-04: "per call" is read as the asynchronous clock: one row per call of the updating agent, regressed on the others' latest states. The inversions are row by row, so the parallel-update formulas apply unchanged with row-specific m, C and D.
