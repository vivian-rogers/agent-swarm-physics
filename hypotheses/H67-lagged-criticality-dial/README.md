# H67: A lagged criticality dial

**Status:** exploratory round 1 done (2026-10-04; non-holdout only). **The HH claim fails; a calibrated read-out dial results.**
- **The lagged gain is subcritical everywhere and is not larger than the equal-time dial.** The read-out loop gain g_lag (extra talk messages caused, through reading, per talk message) has every unit's upper bound below 0.40 (66 units, 35 periods). It exceeds the equal-time dial in only 7/35 periods (median ratio 0.09).
- **Regime III only, and mostly named.** Regime III median g_lag 0.13 (J₁* > 0 at 95% in 80% of units); regime I 0.005. In regime III, messages that name the recipient carry 0.079 [0.069, 0.089] extra talk calls per read, others 0.004 [0.003, 0.006] (×19); the named part is about half of g_lag.
- **Consistent with H42's read-out Hawkes fit:** Spearman ρ(g_lag, world-B n_x) = 0.55 across 35 periods (p 0.0007), median ratio 2.0.
- **The equal-time talk dial reads a field in regime I** (g_eq − g_lag median +0.17), where read-out coupling is ≈ 0. Synthetic: the equal-time dial is not blind to hop-1 coupling on real call grids, and it reads fast shared fields as gain.
- Natives: NE14 descriptive (gain switches on at the regime II → III boundary at fixed cadence), NE42 mixed (#40's merged room loses read-out coupling: dilution, not equal-time blindness), G51 mixed (flat g_lag ≈ 0.14 over N 21 → 32). Scorecard A1 B1 C1 D1 E1 F2 G1 H1 I0. `confirm.py` frozen, guarded and dry-run; **not run**.
**Research question (GOALS.md):** **Q3** (is there collective order beyond fields: how close is the swarm to runaway talk cascades?), with **Q1** (what couples agents) as the mechanism it measures.
**Fields:** stat mech, dynamics, sociophysics
**Literature:** model references in [`physics-models/01-inverse-ising/README.md`](../../physics-models/01-inverse-ising/README.md) (mean-field susceptibility) and [`physics-models/09-hawkes/README.md`](../../physics-models/09-hawkes/README.md) (branching ratio as loop gain; Hawkes 1971†; Filimonov & Sornette 2015†). No notes file in `literature/` covers call-clock linear response.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t); Regime; Driving / external field; **Exposure (turn read-out)** (H08; implemented by the context ledger); **Call cycle (hop)** and **Read-out jump J₁** (H50 named variants); **Loop gain (equal-time, daily dial)** and **Per-pair correlation ρ̄** (H25 named variants). **New named variants proposed for DEFINITIONS.md** (not edited here), defined under Model: *in-flight placebo (matched-lag)*, *read-out loop gain g_lag*.
**From:** HH262 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/01-inverse-ising/`, `physics-models/09-hawkes/`
**Data inputs (shared tables first):** DQ1 `call_windows`, `context_ledger_items`, `context_ledger_turns`; `chat_core`, `chat_mentions_clean`, `calendar`, `period_units`, `roster`. Comparison only (read, never recomputed): H25's trimmed talk dial in `per_period_estimates`; H42's `periods.parquet` (world-B and world-A n_x); H50's `unit_table.parquet` (J₁).

## Question
Does a read-out-lagged susceptibility (the response at the recipient's next model call) reveal larger, still subcritical gains than the equal-time dial, consistent with read-out Hawkes fits per period?

**Why it should.** H25's equal-time 1-min dial reads the talk loop gain at g ≈ 0.14–0.16 (round 1b), but its synthetic S3 showed it reads ≈ 0 when agents respond to others with a 2–8 min delay. H08, H40 and H50 show that coupling acts at the recipient's next call (hop 1), and the call can come minutes after the message (pauses, long tool calls). A dial built on the call clock should see the coupling the 1-min dial misses. H42 (world B) and H50 (J₁) are two read-out estimators that already disagree by about an order of magnitude on per-message excitation; H67 puts both on one loop-gain scale.

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication (layer 1):** the common estimator (below) on every eligible non-holdout period unit (`period_units`: ≥ 3 calling agents, ≥ 100 agent chat messages, ≥ 200 receiving calls in the trimmed window). One README per goal period, role `replication`; units of a split period are reported separately and pooled by a random-effects mean (CLAUDE.md exception (d)).
- **Period-native tests (layer 2), each with its own dated prediction in its folder:**
  - **NE14** (#36, regime II → III inside one goal): the call cadence changes ~5× (scheduled chat calls → chained computer-use calls). A coupling on the call clock should keep g_lag, while the equal-time dial should change with cadence.
  - **NE42** (#39 → #40 → #41, room merge and split at a fixed roster): the readers per message r̄ jumps. Mean field says g_lag ∝ r̄ at fixed per-read coupling; attention dilution says less than ∝ r̄.
  - **G51** (head, 11 units, N 21 → 32): the size sweep. Does the lagged gain approach 1 as N grows?
- **Faithfulness lever (HH262):** H (consistency across methods) and D (unfitted predictions). The scorecard says whether each was raised.

## Model
**From:** `physics-models/01-inverse-ising` (mean-field susceptibility, loop gain) with the kinetic, read-out-gated update of `physics-models/02-nonequilibrium-ising` (H40, H50), and `physics-models/09-hawkes` (branching ratio = loop gain of a linear point process).

**H67 variant: a linear-response swarm on the call clock.** Agent i makes model calls c (start t_c = `t_call`, first output record t_c^out = `t_first`). Its talk outcome Y_ic ∈ {0, 1} (the call is a talk call) responds to what the call newly reads:

  P(Y_ic = 1) = a_{i,d,κ} + J₁ R_ic + J₂ R_{i,c−1} + J₃ R_{i,c−2} + β_P P_ic + γ·E_ic + ρ Y_{i,c−1}

- R_ic: peer agent messages first read at call c (posted in i's room by another agent in [t_{c−1}, t_c); the ledger's visibility rule). Split by age: **R_ic^m**, read messages posted in the matched window (t_c − d_c, t_c), d_c = t_c^out − t_c (the call's own output latency, capped at 120 s); R_ic^o, older read messages.
- **In-flight placebo (matched-lag) P_ic:** peer messages posted in i's room in (t_c, t_c + d_c), i.e. after the call's context was assembled and before its first output. Call c cannot read them, and they cannot be replies to call c's output. They share every time-local field (conversation burst, day edge, a kickoff) with R_ic^m, which sits in the mirror window just before t_c.
- a_{i,d,κ}: agent × day × call-class baseline (κ = context mode {chat, computer use} × {wake, ordinary}; wake = gap kind pause / first-of-day / after-summary / session start / marker). It absorbs the agent's own call clock and call type (H42's main lesson).
- E_ic: exogenous items read at c (human messages; nudges; nudges naming i). Y_{i,c−1}: the agent's own previous talk (conversation persistence).

**Read-out jump (matched-lag):** J₁* = β(R^m) − β_P: the extra talk probability per peer message read at the call, against the same message count posted one latency later. Under pure field (any common drive smooth on the scale d_c ≈ 5–60 s) J₁* = 0. Under read-out-gated coupling J₁* = J₁.

**Read-out loop gain g_lag (proposed named variant).** Each peer message is read once by each recipient, at its read-out call. If the per-read jump J₁* holds for all reads at that call, one talk message causes m̄ · r̄ · J₁* further talk messages directly, with r̄ = recipients per peer message and m̄ = talk messages per talk call. In mean field this is the eigenvalue of the cross-response matrix on the collective mode, so

  **g_lag = m̄ r̄ J₁***, T/T_c = 1/g_lag, amplification of a push 1/(1 − g_lag).

g_lag < 1 is subcritical (talk cascades through reading die out). Variants: **g_lag,3** adds hops 2–3 (Σ_{h=2,3} (β_h − β_P)); **g_lag,het** is the spectral radius of K_ij = m̄_i J₁*_i Pr(i reads j) with per-recipient J₁*_i shrunk toward the pooled value; **g_lag,all** uses β(R^m ∪ R^o) − β_P.

**What each reading predicts.**
- H25's S3 (delayed reads): the equal-time dial g_eq ≈ 0 while g_lag recovers the true gain, so g_lag > g_eq.
- H42 world B (n_x ≈ 0.004 per message, mostly named messages): g_lag ≈ 0.01, below g_eq.
- H50 (J₁ ≈ 0.02–0.03 per read, ~5–15 recipients): g_lag ≈ 0.1–0.4, comparable to or above g_eq.

**Equal-time comparison on identical data.** On the same trimmed unit-days, a 1-min talk spin s_i(t) = 1 if agent i logged a talk call in minute t; 30-min block demeaning; VR = Σ_t(Σ_i X_it)²/Σ_t Σ_i X_it²; g_eq = 1 − 1/VR (H25's estimator, `nulls.stat_cw_gain`). H25's own trimmed talk dial (per-period IVW mean) is the external reference.

## Data scheme (`scheme/`)
- **Inputs:** `call_windows` (turn_id, agent, pt_date, goal_no, holdout, talk, ctx_mode, t_call, t_first, gap_kind, first_of_day), `context_ledger_turns` (room, reset flags), `context_ledger_items` (turn_id, message_id, sender, kind, ment: for the visibility check and exogenous counts), `chat_core` (agent messages: t, room, agent), `chat_mentions_clean` (mentions_roster, for named counts of in-flight messages), `calendar`, `period_units`. The Claude Code agent is a sender, never a recipient (as in the ledger).
- **Transform (`scheme/build.py`):** per non-holdout unit (holdout asserted twice: `calendar.holdout` and `common.holdout_mask`):
  1. receiving calls (`ctx_mode != summary`) of every recipient, with room, call class, d_c = clip(t_first − t_call, 1 s, 120 s);
  2. agent chat messages with room and named recipients;
  3. per call: R^m, R^o, P (all, named, unnamed), lagged R at c−1, c−2, E (human, nudge, nudge naming i, from ledger items), Y_{c−1};
  4. **all-present window (DQ8)** per day: [max_i first t_call, min_i last t_call] over agents with ≥ 20 calls that day; flag calls inside;
  5. a 1-min talk-spin grid per unit-day on the trimmed window (for g_eq on identical data);
  6. verification: my visibility rule vs `context_ledger_items` (share of (message, recipient) pairs assigned to the same call).
- **Output:** `data/processed/H67-lagged-criticality-dial/units/<unit>.parquet` (call rows, codes only), `grid/<unit>.npz`, `unit_meta.parquet`, `results/`, `synthetic/`, `_provenance.json`. Budget ≤ 150 MB.
- **Regimes covered:** I, II, III (non-holdout). Fits are within unit.

## Observables
Per unit (and per period by random-effects pooling of its units):
1. **J₁*** (matched-lag read-out jump; per read message, talk probability), its CI (day-block bootstrap, 200 draws; 1-h blocks for 1-day units), β(R^m), β_P, β(R^o), β₂, β₃, ρ.
2. **g_lag** = m̄ r̄ J₁* with CI; T/T_c; r̄, m̄; variants g_lag,3, g_lag,all, g_lag,het; untrimmed and no-exogenous variants.
3. **Named vs unnamed:** J₁* separately for peer messages that name i (`mentions_roster`) and for the rest, each against its own in-flight placebo.
4. **g_eq** on identical trimmed data, and the ratio g_lag/g_eq; H25's trimmed talk dial for the same period.
5. **Hawkes agreement:** per period, Spearman ρ and median log ratio of g_lag vs H42's world-B n_x (nxB_w) and world-A n_x (nxA_w); per unit, vs H50's J₁ × r̄.
6. **Per-pair gain:** J₁* (per read) and ρ̄_lag = g_lag/(N − 1) vs N.

## Null / baseline
- **In-flight placebo** (contemporaneous convergence and every time-local field): β_P. J₁* is the jump over it.
- **Shift null (day-preserving):** each sender's messages shifted by an independent ±U(5, 30) min within the trimmed day window, reads and in-flight counts recomputed on the recipients' real call grids; 49 surrogates per unit for J₁* and g_lag (size check: the share of surrogates with CI excluding 0).
- **Field-only synthetic worlds** (axis F): a shared OU rate field (τ 3–15 min), day edges and burst pulses with no coupling must give g_lag ≈ 0.
- **Equal-time rival:** the 1-min dial on the same data.
- **Hawkes rivals:** H42's world-B and world-A per-period n_x (no refit).

## Impostors (STANDARDS §1)
| Impostor | How H67 removes it | Residual risk |
| --- | --- | --- |
| **Scheduler field** (central here) | Calls restricted to the DQ8 all-present window (primary); per-call clock (each call is one update; agent × day × call-class baselines absorb cadence and call type, H40/H42); the matched-lag placebo cancels any field smooth on the scale of one call latency (5–60 s), including day edges inside the window. Untrimmed variant reported. | A field that switches on exactly at t_c (none known: call starts are agent-specific) |
| **Exogenous field** (kickoff, goal, operator) | Human messages, nudges and nudges naming i read at c are covariates; the placebo shares any kickoff burst; kickoff day reported with and without its first hour (variant). | Goal content differences between periods (comparisons are within unit) |
| **Shared model priors** | Agent × day baselines remove family talk propensity; the coupling is identified within agent-day from timing only. Family-level heterogeneity of J₁*_i is reported, not claimed. | Same-family agents reacting to the same cue at the same moment (cancelled by the placebo) |
| **Contemporaneous convergence** | The in-flight placebo is exactly the "posted but not yet read at matched lag" control (H57, RE-D1). | Replies to i's previous call in both windows (symmetric, cancels to first order; Y_{c−1} control) |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** the equal-time Curie–Weiss dial (H25); H42's world-B read-out Hawkes kernel (n_x per message); H42's world-A exponential Hawkes kernel; pure field (shared rate modulation, no coupling).
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (frozen, guarded, not run) targets #28, #22 (regime I), #43 and the #51 tail (regime III).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Calls, reads, in-flight messages and windows come from the ledger (my rule reproduces `context_ledger_items` in 100% of calls in #27, #40, #51c). Assumption listed: the per-read jump of fresh messages holds for older reads (g_all, which drops it, gives regime-III median 0.11 vs 0.13). **Not invariant:** ≈ 0 in regimes I/II, 0.13 in III; regime-I talk happens at scheduled chat-mode calls, so a hop-1 estimator is the wrong clock there. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Update order audited (reads strictly before t_call; placebo strictly after and before the call's first output). Hour-block bootstrap. Robust to trimming (regime-III median 0.129 → 0.117 untrimmed), exogenous controls (0.129), decision-time matching (0.133), heterogeneous spectral radius (0.137). The post hoc quiet-recipient subset lowers it to 0.086. No Markov-order test. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | β(read) > β(in-flight) in 76% of units; J₁* > 0 at 95% in 35% overall, 80% in regime III. The shift null's CI-excludes-0 share is 13.6% (synthetic: 7.5–10%), so per-unit significance is mildly anti-conservative. No held-out likelihood. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | P1 (subcritical), P5 (address gating ×19 in III), P7 (per-read J₁* falls with N, ρ −0.59; g_lag flat in N, ρ 0.24) pass as predicted. P2 (the HH signature: lagged > equal-time) fails. |
| E interventional | predicts the change across a natural experiment | 1 | NE42: the merged room removes read-out coupling (J₁* 0.016 → 0.000 → 0.023), as the dilution prediction said; the "lag sees what equal time misses" clause failed. NE14 descriptive (premise of a cadence change was wrong). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | On real call grids (4 units, 10 replicates × 5 worlds): bias −1% to −3% at g = 0.15–0.60, coverage 0.88–0.98, null and burst worlds ≈ 0 (CI excludes 0 in 7.5% / 10%). The day-block CI and the decision-time variant failed calibration and were replaced before real data (A1). |
| G ground truth | agrees with known structure | 1 | Agrees with H50 (hop-1 gating, address gating in III), H42 (regime-III-only, named-message carrier; ρ 0.55 with world-B n_x) and H25 (#40 collapse). Not checked against a talk-level ground truth (Claude Code input stream). |
| H comparative | beats the named rivals | 1 | Beats the uncorrected lagged gain (which reads 0.06 in a burst world with no coupling) and the equal-time dial as a coupling gauge (the equal-time dial reads 0.10–0.31 from fields alone). Agrees in rank with H42's world B. Does not reconcile H50's larger J₁ (ρ 0.24 with J₁·r̄; H50 implies g ≈ 0.24). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holds across regime-III periods (7/8 periods with g_lag > 0 at 95%; #40 is the exception), but no holdout run. |

**Faithfulness lever (HH262):** H was raised to 1 (two estimators now agree in rank; H50 still disagrees in size). D was raised to 1 through unfitted size and gating predictions, but the HH's own signature (lagged > equal-time) failed.

## Prediction
*Written 2026-10-04 19:15 UTC, before any real-data statistic. Seen beforehand: table schemas, period-unit counts, and the published per-period results of H25 (round 1b talk dial median 0.162, trimmed 0.143), H42 (world-B n_x median 0.004; named 0.15 per message in regime III), H50 (J₁ 0.034 / 0.019 in regimes I / III; named 0.17, unnamed 0.004 in III) and H40. Not seen: any H67 statistic.*

**Synthetic (axis F), before real data.** Talk simulated on the real call grids of four units (one regime-I, three regime-III), with a shared OU rate field (τ = 5 min) and day edges in every arm:
- **S1 recovery:** planted read-out-gated coupling with g_true ∈ {0.15, 0.3, 0.6}: g_lag within ±25% of truth (median over 8 replicates per cell), 95% CI covers the truth in ≥ 80%. [0.6]
- **S2 null:** g_true = 0 (field and edges only): |median g_lag| ≤ 0.03 and the CI excludes 0 in ≤ 10% of replicates. [0.7]
- **S3 equal-time blindness:** in the planted worlds g_eq (same data, trimmed) < 0.5 · g_true in regime III. [0.6]
- **S4 burst field:** a shared 3-min conversation-burst pulse with no coupling: the uncorrected β(R) > 0, but J₁* ≈ 0 (|J₁*| within its CI of 0 in ≥ 80%). [0.6]

**Real data (exploratory, non-holdout).**

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 | **Subcritical.** The 95% upper bound of g_lag is < 1 in every eligible unit, and g_lag < 0.5 in ≥ 90% of units. | any unit with a lower bound ≥ 1 | 0.9 |
| P2 | **Larger than the equal-time dial (the HH claim).** g_lag > g_eq (same data) in ≥ 2/3 of eligible periods, and the median ratio g_lag/g_eq ≥ 1.5. Same against H25's trimmed talk dial. | g_lag ≤ g_eq in ≥ 1/2 of periods | 0.4 |
| P3 | **Consistent with read-out Hawkes fits.** Across periods, Spearman ρ(g_lag, H42 world-B n_x) ≥ 0.3 and the median of g_lag/n_x,B within [1/3, 3]. | ρ < 0.3 or the ratio outside [1/3, 3] | 0.3 |
| P3b | **Consistent with H50's gate.** Per unit, ρ(g_lag, H50 J₁·r̄) ≥ 0.5. | ρ < 0.3 | 0.7 |
| P4 | **Jump over the placebo.** J₁* > 0 (CI excluding 0) in ≥ 50% of units, and β(R^m) > β_P in ≥ 2/3; the shift null's false-positive share ≤ 10%. | J₁* > 0 in < 1/3 of units | 0.6 |
| P5 | **Address gating (regime III).** Pooled named J₁* ≥ 5 × unnamed J₁*; in regime I the ratio is < 3. | regime-III ratio < 2 | 0.65 |
| P6 | **Impostor robustness.** Trimming vs untrimmed and with vs without exogenous controls each change the median g_lag by < 25%. | either changes it by > 50% | 0.6 |
| P7 | **Size.** Per-read J₁* falls with N across units within regime (Spearman ρ < 0), and g_lag does not rise with N (ρ(g_lag, N) ≤ 0.3). | g_lag rises with N (ρ > 0.5) | 0.5 |

**Amendment A1 (2026-10-04 19:55 UTC, after the synthetic validation, before any real-data estimate).** Seen: only synthetic runs on real call grids (units 27, 40, 41, 51e; 10 replicates × 5 worlds) and the visibility check (my rule reproduces `context_ledger_items` in 100% of calls in #27, #40, #51c).
- **Bootstrap blocks: 1 hour everywhere** (was days when ≥ 3 days). With day blocks the CI of g_lag excluded 0 in 28% of null runs; with hour blocks in 7.5% (null) and 10% (burst).
- **Primary estimator unchanged** (posting-time matched in-flight placebo, "pm"). A decision-time matched variant ("dm": read vs unread messages *decided* at the same lag before the call) was built to remove a suspected burst bias; it was noisier and worse sized (27.5% false exclusions in the burst world), so it is reported as a variant only.
- **Synthetic verdicts:** S1 **passed** (median relative error −1.3%, −1.5%, −2.7% at g = 0.15, 0.30, 0.60; 95% CI coverage 0.88–0.98). S2 **passed** (median g_lag −0.010 at g = 0; CI excludes 0 in 7.5%). S4 **passed** (burst world: median g_lag −0.030, CI excludes 0 in 10%, while the uncorrected gain reads +0.062). **S3 failed:** on real call grids the equal-time dial is *not* blind to hop-1 coupling (g_eq / g_true = 1.44, 0.90, 0.64 at g = 0.15, 0.30, 0.60 in regime III, because a hop-1 response lands within about 30 s), and it reads 0.10–0.15 from a 5-min shared field alone and 0.31 under conversation bursts.
- **Consequence for P2 (stated before real data):** P2 is scored as written. A g_eq above g_lag is now expected wherever fast shared fields exist, because the equal-time dial counts field co-movement as gain and the lagged dial removes it. "g_lag < g_eq" therefore reads as "the equal-time dial overstates coupling", not as "no delayed coupling". The difference g_eq − g_lag is reported per period as a field-contamination estimate.

**Per-period verdict rule (replication):** *supported* if the period's pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; *failed* if J₁* ≤ 0 within CI and g_lag ≤ g_eq, or if any unit's g_lag lower bound ≥ 1; *mixed* otherwise; *descriptive* if the period has fewer than 200 trimmed receiving calls with any read.

Native predictions are in `goalperiod-subhypotheses/NE14/`, `NE42/` and `G51/` (written before those runs).

## Results by goal period
Per-period rule (card). **5 supported, 6 mixed, 24 failed** (35 periods; 66 units; 4 units with < 4 bootstrap blocks dropped: 4b, 4d, 12b, 44a). Regime-I periods fail because J₁* ≈ 0 and the equal-time dial reads a field.

| Period | Role | Verdict | Key numbers (period random-effects pool) |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | failed | I, N 4: g_lag 0.021 [-0.081, 0.124] · J₁* 0.008 · g_eq 0.406 · H42 n_x(B) 0.022 |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | failed | I, N 4: g_lag 0.017 [-0.090, 0.124] · J₁* 0.006 · g_eq 0.353 · H42 n_x(B) 0.067 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | I, N 4: g_lag 0.011 [-0.023, 0.046] · J₁* 0.004 · g_eq 0.268 · H42 n_x(B) 0.030 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | supported | I, N 4: g_lag 0.052 [0.006, 0.099] · J₁* 0.017 · g_eq 0.037 · H42 n_x(B) 0.026 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | failed | I, N 4: g_lag -0.008 [-0.038, 0.023] · J₁* -0.003 · g_eq 0.158 · H42 n_x(B) 0.000 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | failed | I, N 4: g_lag 0.035 [-0.029, 0.099] · J₁* 0.012 · g_eq 0.111 · H42 n_x(B) 0.000 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | mixed | I, N 4: g_lag 0.005 [-0.018, 0.027] · J₁* 0.001 · g_eq -0.014 · H42 n_x(B) 0.000 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | failed | I, N 7: g_lag 0.002 [-0.050, 0.054] · J₁* 0.000 · g_eq 0.069 · H42 n_x(B) 0.010 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | failed | I, N 7: g_lag 0.027 [-0.026, 0.080] · J₁* 0.005 · g_eq 0.192 · H42 n_x(B) 0.013 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | I, N 7: g_lag 0.039 [-0.008, 0.086] · J₁* 0.007 · g_eq 0.221 · H42 n_x(B) 0.006 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed | I, N 6: g_lag -0.002 [-0.037, 0.033] · J₁* -0.000 · g_eq 0.095 · H42 n_x(B) 0.000 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | failed | I, N 7: g_lag 0.031 [-0.022, 0.083] · J₁* 0.005 · g_eq 0.231 · H42 n_x(B) 0.011 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | failed | I, N 7: g_lag 0.038 [-0.075, 0.150] · J₁* 0.006 · g_eq 0.347 · H42 n_x(B) 0.000 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | I, N 7: g_lag 0.048 [-0.000, 0.097] · J₁* 0.007 · g_eq 0.293 · H42 n_x(B) 0.002 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | I, N 8: g_lag -0.003 [-0.032, 0.026] · J₁* -0.001 · g_eq 0.248 · H42 n_x(B) 0.000 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | failed | I, N 9: g_lag -0.020 [-0.046, 0.006] · J₁* -0.002 · g_eq 0.148 · H42 n_x(B) 0.002 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | I, N 8: g_lag -0.018 [-0.051, 0.014] · J₁* -0.002 · g_eq 0.154 · H42 n_x(B) 0.002 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | failed | I, N 10: g_lag -0.038 [-0.064, -0.012] · J₁* -0.004 · g_eq 0.171 · H42 n_x(B) 0.000 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | failed | I, N 10: g_lag 0.009 [-0.025, 0.044] · J₁* 0.001 · g_eq 0.138 · H42 n_x(B) 0.002 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | failed | I, N 10: g_lag 0.012 [-0.033, 0.058] · J₁* 0.001 · g_eq 0.128 · H42 n_x(B) 0.009 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed | I, N 10: g_lag 0.012 [-0.055, 0.079] · J₁* 0.001 · g_eq 0.310 · H42 n_x(B) 0.030 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | I, N 10: g_lag 0.006 [-0.025, 0.037] · J₁* 0.001 · g_eq 0.071 · H42 n_x(B) 0.000 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | failed | I, N 11: g_lag -0.005 [-0.041, 0.030] · J₁* -0.001 · g_eq 0.182 · H42 n_x(B) 0.000 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | failed | I, N 11: g_lag -0.035 [-0.094, 0.025] · J₁* -0.003 · g_eq 0.050 · H42 n_x(B) 0.000 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | failed | II, N 11: g_lag -0.029 [-0.133, 0.076] · J₁* -0.003 · g_eq 0.083 · H42 n_x(B) 0.000 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | mixed | II, N 12: g_lag 0.046 [0.015, 0.076] · J₁* 0.007 · g_eq 0.107 · H42 n_x(B) 0.010 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication (NE14 native separate) | failed | II, N 12: g_lag 0.068 [-0.030, 0.166] · J₁* 0.015 · g_eq 0.136 · H42 n_x(B) 0.031 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | III, N 12: g_lag 0.220 [0.141, 0.299] · J₁* 0.038 · g_eq 0.230 · H42 n_x(B) 0.027 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | III, N 13: g_lag 0.066 [0.041, 0.090] · J₁* 0.012 · g_eq 0.108 · H42 n_x(B) 0.036 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication + NE42 | mixed | III, N 15: g_lag 0.144 [0.066, 0.223] · J₁* 0.016 · g_eq 0.159 · H42 n_x(B) 0.072 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication + NE42 | mixed | III, N 15: g_lag 0.003 [-0.110, 0.117] · J₁* 0.000 · g_eq -0.048 · H42 n_x(B) 0.004 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication + NE42 | supported | III, N 15: g_lag 0.189 [0.093, 0.286] · J₁* 0.023 · g_eq 0.162 · H42 n_x(B) 0.014 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | supported | III, N 16: g_lag 0.154 [0.059, 0.248] · J₁* 0.018 · g_eq 0.091 · H42 n_x(B) 0.047 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | supported | III, N 18: g_lag 0.234 [0.129, 0.340] · J₁* 0.027 · g_eq 0.121 · H42 n_x(B) 0.000 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native + replication | supported | III, N 27: g_lag 0.142 [0.111, 0.174] · J₁* 0.006 · g_eq 0.125 · H42 n_x(B) 0.016 |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | native | descriptive | 36a g_lag −0.06 [−0.15, 0.03] → 36b ∪ 36c 0.12 [0.06, 0.17]; call interval 13.7 → 12.0 s |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | mixed | g_lag 0.144 → 0.003 → 0.189 (#39 → #40 → #41); r̄ ×1.45; J₁* 0.016 → 0.000 → 0.023 |

## Results
*Exploratory round 1, 2026-10-04: 66 non-holdout units in 35 goal periods, 1.47M receiving calls in all-present windows. Numbers from `data/processed/H67-lagged-criticality-dial/results/{units,periods}.parquet`, `summary.json`, `synthetic/summary.json`. Code: `scheme/build.py`, `analysis/h67lib.py`, `synthetic.py`, `run_units.py`, `summarize.py`, `write_period_folders.py`, `figs_col.py`, `confirm.py`.*

### Headline
The read-out loop gain is a calibrated, subcritical number: **g_lag = 0.13 (regime-III median; units 0.00–0.29, every upper bound < 0.40)** and ≈ 0 in regimes I and II. One talk message causes about 0.13 further talk messages through reading, so a push is amplified ×1.15 (T/T_c ≈ 8). The HH claim fails: the lagged gain is not larger than the equal-time dial (7/35 periods). The equal-time talk dial over-reads coupling wherever fast shared fields drive talk (regime I: g_eq 0.16 vs g_lag 0.005). About half of the regime-III gain comes from messages that name the recipient.

### Outcome vs prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| S1 | recovery ±25%, coverage ≥ 80% | −1.3% / −1.5% / −2.7%; coverage 0.88–0.98 (after A1) | passed |
| S2 | null \|g\| ≤ 0.03, CI ≠ 0 ≤ 10% | −0.010; 7.5% | passed |
| S3 | equal-time dial < 0.5 g_true (III) | 1.44 / 0.90 / 0.64 × g_true; reads 0.10–0.31 from fields | **failed** (A1) |
| S4 | burst field: J₁* ≈ 0 | median g −0.03; CI ≠ 0 in 10%; uncorrected +0.06 | passed |
| P1 | all units subcritical; g < 0.5 in ≥ 90% | max upper bound 0.39; 100% < 0.5 | **supported** |
| P2 | g_lag > g_eq in ≥ 2/3 of periods, ratio ≥ 1.5 | 20% (7/35), median ratio 0.09; vs H25 trimmed 20%, 0.06; regime III 62.5% | **failed** |
| P3 | ρ(g_lag, H42 n_x(B)) ≥ 0.3; ratio in [1/3, 3] | ρ 0.55 (p 0.0007, 35 periods); median ratio 2.0 | **supported** |
| P3b | ρ(g_lag, H50 J₁·r̄) ≥ 0.5 per unit | ρ 0.24 (p 0.05, 66 units); H50 implies median 0.24 | **failed** |
| P4 | J₁* > 0 in ≥ 50% of units; β(read) > β_P in ≥ 2/3; shift size ≤ 10% | 35% (III 80%); 76%; 13.6% | mixed |
| P5 | named ≥ 5× unnamed (III); < 3× (I) | III: 0.079 vs 0.004 (×19); I: named 0.004 n.s. | **supported** |
| P6 | trim and exogenous controls change median g < 25% | III: −10% untrimmed, 0% without exogenous terms | **supported** |
| P7 | ρ(J₁*, N) < 0; ρ(g, N) ≤ 0.3 (within regime) | III: −0.59 (p 0.002); 0.24 | **supported** |

### Findings
1. **Read-out coupling is a regime-III property.** In regimes I and II, fresh peer messages read at a call do not raise the call's talk probability beyond messages posted while it ran (median J₁* 0.0007). In regime III, J₁* = 0.008 per read (median), with r̄ ≈ 9–30 readers per message. Regime-I talk happens at scheduled chat-mode calls, so a response to reading could sit at a later hop; the hop-1 estimator does not see it (H50 found a rising regime-I kernel).
2. **Address gating carries the gain.** A read message naming the recipient raises its talk probability by 0.079 [0.069, 0.089]; an unnamed one by 0.004 [0.003, 0.006]. Named items are 3–16% of reads, yet give a median 0.067 of regime III's 0.13.
3. **The equal-time dial is not a coupling gauge.** On real call grids it sees hop-1 coupling (synthetic S3 failed) and reads 0.10–0.31 from fields alone. In regime I it reads 0.16 where the lagged dial reads 0.
4. **Size.** Per-read coupling falls with N (regime III ρ −0.59), and g_lag stays flat (#51: 0.14 over N 21 → 32): read-out dilution holds the loop gain constant as the swarm grows.
5. **Reconciling H42 and H50.** g_lag ranks periods like H42's world-B n_x (ρ 0.55) and sits 2× above it; H50's J₁·r̄ (median 0.24) is about twice g_lag and correlates weakly. H50's 120-s bandwidth and shifted-time placebo admit more of the conversation field than the matched in-flight placebo does.

### Post hoc (labelled; after the first real-data pass)
- **A2 quiet recipients:** in #51 the fresh-read coefficient is ≈ 0 and J₁* comes from a negative in-flight coefficient. Restricting to recipients with no own talk in the last 5 min keeps the sign but lowers the regime-III median to 0.086 (−34%). Unnamed messages near the call carry a small negative association (turn-taking or a negative field). The named part, whose in-flight placebo is ≈ 0, is the cleanest component.
- **Named/unnamed decomposition** of g_lag per unit (`g_named`, `g_unnamed`).

### Caveats
- The unnamed part of g_lag (≈ 0.002–0.004 per read × 20–30 readers in #51) is at the resolution of the in-flight placebo. A latency asymmetry (in-flight messages are decided closer to the call) can bias it by about ±0.03 in g (synthetic burst world −0.03).
- Regime I is measured on the wrong clock for talk (see Finding 1); "regime I ≈ 0" means "no hop-1 read-out talk coupling".
- g_lag counts direct (first-generation) offspring at hop 1; hops 2–3 (g3, regime-III median 0.28) are not placebo-corrected.
- Shift-null size 13.6% per unit: per-unit significance calls are mildly anti-conservative; cross-unit counts carry the evidence.
- Not blind: H25, H42, H50 numbers were known when predictions were written.

## Round 2 redirects
- **What the direction is really after:** a lag-aware, field-free loop gain that an operator can trust as "distance to runaway talk", on the clock the scaffold imposes.
- **H67-R1. Regime-I clock.** Re-index regime-I reads to the next *chat-mode* call (talk-capable), with an in-flight placebo at that call.
- **H67-R2. Named vs unnamed on the holdout.** Confirm the named-message gain (C3) and test whether the unnamed part survives a decision-time-matched placebo at larger samples.
- **H67-R3. Reconcile with H50.** Run both estimators on identical pairs with matched bandwidths to locate the factor-2 gap.
- **H67-R4. Multi-generation gain.** Placebo-correct hops 2–5 with a lagged in-flight design and report the full DC loop gain.

## Notes
- 2026-10-04 19:15 UTC: round 1 started; card filled before any real-data statistic. Compute: local, ≤ 4 threads per process; after the coordinator's load notice (~20:25 UTC) ≤ 2 workers, one job at a time.
- 2026-10-04 19:55 UTC: Amendment A1 after the synthetic validation (before real data).
- 2026-10-04 ~20:10–20:30 UTC: replication run (66 units, ~6 min), then the post hoc A2 variants (rerun, ~6 min).
- Data: `data/processed/H67-lagged-criticality-dial/` (41 MB).
- Proposed for `physics-models/DEFINITIONS.md` (not edited): *in-flight placebo (matched-lag)*, *read-out loop gain g_lag*.


