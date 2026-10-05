# H67: A lagged criticality dial

**Status:** exploratory round 2 done (2026-10-05; non-reserved data only): R3, R4, R1. R2 needs reserved data. **Round 2: H50's factor 2 is located and the hop-1 gain is confirmed by an independent fluctuation bound.**
- **R3:** H50's regime-III value (0.24) comes from its pair-RD design: local-linear extrapolation plus pair sampling. Its regime-I value comes from call-class composition (cells remove 69–95%). Bandwidth, placebo, normalization (ΔR 1.04) and pooling do not explain it. H111's Fano-implied total gain 0.149 [0.123, 0.175] matches H67's 0.127 and excludes 0.24.
- **R4:** the lagged in-flight multi-hop gain failed synthetic validation and is descriptive (G₅ pool 0.24 [−0.03, 0.51]). The Fano bound caps hops 2–5 at about +0.05.
- **R1:** on the chat clock, regime I has no read-out gain (−0.022 [−0.052, 0.009]; attenuation-corrected < 0.04). Post hoc: 3/4 of the "read → chat-mode" effect is the chat-turn schedule; the mode-free excess is 0.035 [0.023, 0.046].
- Round-2 scorecard A1 B1 C1 D2 E1 F2 G1 H2 I0.

*Round 1 (kept):* exploratory round 1 done (2026-10-04; non-holdout only). **The HH claim fails; a calibrated read-out dial results.**
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
| D unfitted predictions | unfitted statistics and the model's signature | 2 | Round 2: g_lag (response, 0.127 pool) matches the Fano-implied total gain from H111's fluctuations (0.149 [0.123, 0.175]), a statistic it was not fitted to; the first stage ΔR = 1.04 as predicted. Round 1: P1, P5, P7 passed; P2 (the HH signature: lagged > equal-time) failed. |
| E interventional | predicts the change across a natural experiment | 1 | NE42: the merged room removes read-out coupling (J₁* 0.016 → 0.000 → 0.023), as the dilution prediction said; the "lag sees what equal time misses" clause failed. NE14 descriptive (premise of a cadence change was wrong). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | On real call grids (4 units, 10 replicates × 5 worlds): bias −1% to −3% at g = 0.15–0.60, coverage 0.88–0.98, null and burst worlds ≈ 0 (CI excludes 0 in 7.5% / 10%). The day-block CI and the decision-time variant failed calibration and were replaced before real data (A1). |
| G ground truth | agrees with known structure | 1 | Agrees with H50 (hop-1 gating, address gating in III), H42 (regime-III-only, named-message carrier; ρ 0.55 with world-B n_x) and H25 (#40 collapse). Not checked against a talk-level ground truth (Claude Code input stream). |
| H comparative | beats the named rivals | 2 | Round 2: H50's factor 2 located (regime III: pair-RD design; regime I: call-class composition). H50's pair RD fails synthetic recovery (+0.05 with no coupling) and its regime-III scale (0.24) exceeds the Fano bound (0.175). Beats the equal-time dial and the uncorrected lagged gain (round 1); agrees in rank with H42's world B. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holds across regime-III periods (7/8 periods with g_lag > 0 at 95%; #40 is the exception), but no holdout run. |

**Faithfulness lever (HH262), round 2:** H raised to 2 and D to 2 (H50 reconciled; Fano cross-check). Round 1: H was raised to 1 (two estimators now agree in rank; H50 still disagrees in size). D was raised to 1 through unfitted size and gating predictions, but the HH's own signature (lagged > equal-time) failed.

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
Round 2 (2026-10-05): regime-I verdicts re-scored on the chat clock (card, Round 2): G05 → failed, G07 → supported, G27 → mixed; other periods unchanged. Round-1 rule (card): **5 supported, 6 mixed, 24 failed** (35 periods; 66 units; 4 units with < 4 bootstrap blocks dropped: 4b, 4d, 12b, 44a). Regime-I periods fail because J₁* ≈ 0 and the equal-time dial reads a field.

| Period | Role | Verdict | Key numbers (period random-effects pool) |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | failed | I, N 4: g_lag 0.021 [-0.081, 0.124] · J₁* 0.008 · g_eq 0.406 · H42 n_x(B) 0.022 |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | failed | I, N 4: g_lag 0.017 [-0.090, 0.124] · J₁* 0.006 · g_eq 0.353 · H42 n_x(B) 0.067 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | I, N 4: g_lag 0.011 [-0.023, 0.046] · J₁* 0.004 · g_eq 0.268 · H42 n_x(B) 0.030 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | failed (r2 chat clock; r1 supported) | I, N 4: g_lag 0.052 [0.006, 0.099] · J₁* 0.017 · g_eq 0.037 · H42 n_x(B) 0.026 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | failed | I, N 4: g_lag -0.008 [-0.038, 0.023] · J₁* -0.003 · g_eq 0.158 · H42 n_x(B) 0.000 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | supported (r2 chat clock; r1 failed) | I, N 4: g_lag 0.035 [-0.029, 0.099] · J₁* 0.012 · g_eq 0.111 · H42 n_x(B) 0.000 |
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
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | mixed (r2 chat clock; r1 failed) | I, N 10: g_lag 0.006 [-0.025, 0.037] · J₁* 0.001 · g_eq 0.071 · H42 n_x(B) 0.000 |
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

## Round 2 (2026-10-05): R3, R4, R1
Round 2 runs H67-R3, R4 and R1. R2 needs reserved data and is not run. Non-reserved data only (`holdout_mask` asserted on every unit's days).

### Pre-registration
*Written 2026-10-05 02:45 UTC (committed 02:47), before any round-2 statistic on real data.*

**Seen beforehand:**
- Everything on this card.
- Round-1 per-unit design quantities: r̄, m̄, the median call interval and matched window, the base talk rate, and the list of columns in H50's unit table.
- The regime-I call mix in 10 units. Chat-mode calls are 5–10% of trimmed calls and talk at 0.7–0.85 of them; computer-use calls talk at 0.01–0.10. Chat calls are spaced 60–560 s apart (median), and 75% of their starts are latency-placed (`start_conf` low).
- H50's published J₁ and its hop kernel: a drop at hop 2, then a plateau near 0.015 in regime III; a rise in regime I.
- H111's r_F (hop-1 g closes regime III, g3 over-predicts) and H99 round 2 (named messages keep acting one call later).
- No round-2 estimator has run on real data.

**Correction to round 1, Finding 5.** H50's gate bandwidth is not 120 s. H50's Amendment 1 set W = 1.5 × the unit's median act-call interval (≈ 17–20 s). The "120-s bandwidth" explanation of the gap is withdrawn untested; R3 tests it.

**Code switches.** All round-2 code is new (`analysis/r2lib.py`, `r2_synthetic.py`, `r2_run.py`, `r2_summarize.py`). `h67lib.py` and the round-1 scripts are unchanged, so round 1 reproduces exactly. H50's estimator is re-implemented in `r2lib.py`, never imported.

#### R3: reconcile with H50 (a ladder on identical pairs)
Both estimators run on the same unit tables (H67's `units/` and `msgs/`; visibility = the ledger rule). Each rung changes one thing. Gains are put on one scale as g = m̄ r̄ × (per-read jump).

| Rung | Estimator | Changes |
| --- | --- | --- |
| L0 | H50's published J₁ × r̄ | (round 1, P3b) |
| L1 | H50's pair RD, re-implemented. Pairs: (peer message, room recipient that reads it). Anchor calls within ±W of the message (W = H50's unit W); 2-s donut; local-linear limits at s = 0. Minus the same RD at placebo times shifted by ±U(5, 30) min (2 copies). All calls of the unit. | reproduction |
| L2 | L1 on the all-present window only | trimming |
| L3 | L2 with bandwidth = the unit's median H67 matched window w̄ | bandwidth |
| L4 | L3 with talk demeaned in H67's agent × day × call-class cells | call-class baseline |
| L5 | L4 without the shifted-time placebo | placebo |
| L6 | L4 divided by the RD jump of the anchor call's read count (first stage ΔR) | per-read normalization |
| L7 | Call-level count regression on the same trimmed rows: talk ~ R^m + P, pooled (no cells); J = β(R^m) − β(P) | pair → call design |
| L8 | L7 with agent × day × call-class cells | cells in the call design |
| L9 | H67 main (L8 + R^o, R_{c−1}, R_{c−2}, y_{c−1}, exogenous items) = round-1 g_lag | controls |
| L9b | L9 with the matched window capped at H50's W | bandwidth, reverse |

- **Unit pooling** (the fifth candidate): period pools of L1 and L9 by both IVW and random effects.
- **Attribution:** the change in the regime median of g at each rung, with the per-unit median of the paired difference and its sign share.
- **The gap is located** if one or two named rungs carry ≥ 2/3 of the regime-III change from L1 to L9.

#### R4: multi-generation gain (lagged in-flight design)
- **Design.** On the all-call clock, call c of agent i, and k = 0…4: R^m_{c−k}, P_{c−k} and R^o_{c−k} are H67's counts at the same agent's call c − k (same day; the first 4 calls of each agent-day drop out).
  - Regress talk_c on all 15 counts, the exogenous items at c, and the pre-window own talk y_{c−5}. Use agent × day × call-class cells, trimmed rows and a 1-h block bootstrap (200 draws).
  - No own-talk lag inside the window: y_{c−1}…y_{c−4} are mediators of earlier reads.
- **Identification.** A message read at c − k is at hop k + 1 for call c. A message in flight at c − k is read at c − k + 1, which is hop k. So β(R^m_{c−k}) = δ(k+1) + f_k and β(P_{c−k}) = δ(k) + f_k, with the same field term f_k (δ(0) = 0).
  - Kernel increment: Δ_k = β(R^m_{c−k}) − β(P_{c−k}) = δ(k+1) − δ(k).
  - Kernel: δ(h) = Σ_{k<h} Δ_k.
  - **Multi-generation (DC) loop gain:** G_H = m̄ r̄ Σ_{h=1..H} δ(h). The primary is **g_full = G_5**.
  - It counts first-generation offspring over hops 1–5, including the recipient's own talk persistence. That is the gain H111's Fano sum rule needs, g/(1 − a).
- **Fano check.** Φ_pred(G_5) uses H111's formula and room sizes (H111's `present` table, days weighted equally). H111's Φ_obs(10) and its log-SE are read as data; nothing is refitted.
  - r_F = Φ_obs/Φ_pred.
  - Pooled by random effects on log r_F (regime III), with G_5's bootstrap SE propagated by the delta method.
- **Rivals:**
  - (a) Hop 1 is the whole gain: G_5 ≈ g_lag.
  - (b) H50's plateau: δ(h) stays near 0.8 δ(1) to hop 5, so G_5 ≈ 4 g_lag.
  - (c) The uncorrected round-1 g3 (0.28 in regime III).

#### R1: the regime-I chat clock
- **Design.** In regime I and II units, the response clock is the agent's chat-mode receiving calls (the talk-capable ones). t_prev is the previous chat-mode call of the same agent-day. Per chat call c:
  - **R^m:** peer messages posted in (t_c − w_c, t_c), read at c itself.
  - **P:** peer messages posted in (t_c, t_c + w_c), in flight at c.
  - w_c = min(t_first − t_call, chat-to-chat interval, 120 s).
  - **R^o_chat:** reads since the previous chat call minus R^m. It includes reads at the computer-use calls in between.
  - y = talk at the previous chat call; exogenous items summed since the previous chat call.
  - Cells: agent × day × wake class. Trimmed rows; 1-h blocks.
- **Primary:** J*_chat = β(R^m) − β(P) and **g_chat = m̄ r̄ J*_chat**. Every read reaches exactly one next chat call, so r̄ is unchanged.
- **Variants:**
  - Re-indexed all reads, g_chat,all = m̄ r̄ (β(R^m + R^o_chat) − β(P)). It is not matched-lag.
  - Logged-start chat calls only (`start_conf` high).
  - Named vs unnamed.
- **Regime-I total:** g_I = g_cu + g_chat, where g_cu is the round-1 estimator on computer-use rows only.
- **Start-time error.** Chat-call starts are mostly latency-placed (t_call = first output − calibrated latency), so reads and in-flight messages near t_c can swap sides. That attenuates J*_chat toward 0. Synthetic worlds measure the size of this effect.

#### Synthetic validation (before real data; worlds on real call grids, H67's simulator extended)
- **R3 (units 27, 41, 51e):** null, burst, g = 0.15 and g = 0.30 (hop 1), 8 replicates each.
  - **S-R3a:** L9 recovers truth within ±10% and L1 within ±25% (median relative error).
  - **S-R3b:** in null and burst worlds, |median g| ≤ 0.03 for both.
- **R4 (units 27, 41, 51e):** five worlds, 8 replicates each.
  - Worlds: (a) hop 1 only, g = 0.15; (b) decaying kernel δ = J·(1, 0.6, 0.4, 0.2, 0), G_5 = 0.22; (c) plateau kernel δ = J·(1, 0.8, 0.8, 0.8, 0.8), G_5 = 0.33; (d) null; (e) burst null.
  - **S-R4a:** in (a)–(c), the median G_5 is within ±25% of truth and 95% coverage is ≥ 0.8.
  - **S-R4b:** in (d)–(e), |median G_5| ≤ 0.05 and the CI excludes 0 in ≤ 15%.
- **R1 (regime-I units 4c, 19a, 27):** four worlds, 8 replicates each.
  - Worlds: (a) chat-clock coupling: talk at chat calls responds to all reads since the previous chat call, g_chat = 0.15, no computer-use coupling; (b) null; (c) burst null; (d) world (a) with start-time error (true latency lognormal, median 11 s, σ_log 0.5; observed start = first output − 11.3 s).
  - **S-R1a:** in (a), the median g_chat is within ±25% of truth and coverage is ≥ 0.8.
  - **S-R1b:** in (b)–(c), |median| ≤ 0.03 and the CI excludes 0 in ≤ 15%.
  - **S-R1c:** in (a), the round-1 hop-1 estimator reads < 0.5 × truth (the wrong-clock claim).
  - **S-R1d:** in (d), the attenuation of g_chat is reported, and it rescales the real-data reading.

#### Predictions (real data, exploratory, non-reserved)
| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| R3-P1 | **Reproduction.** L1 reproduces H50's J₁: median L1/L0 in [0.85, 1.15], Spearman ≥ 0.8 over units. | median outside [0.7, 1.4] (kill: ladder not interpretable) | 0.7 |
| R3-P2 | **Where the gap lives (regime III).** The call-class baseline (L3→L4) and the placebo design (L4→L5, and L1 vs L7) together carry ≥ 50% of the change from L1 to L9. Trimming (L1→L2) and bandwidth (L2→L3, L9→L9b) each carry < 25%. | bandwidth or trimming carries ≥ 50% | 0.45 |
| R3-P3 | **Normalization is not the cause.** The first-stage jump ΔR in reads at the boundary is in [0.8, 1.25] (regime-III median). | ΔR ≥ 1.5 | 0.6 |
| R3-P4 | **Regime I.** The call-class baseline removes ≥ 70% of H50's positive regime-I gain (L3→L4). | < 30% removed | 0.5 |
| R3-P5 | **Synthetic arbitration.** Both estimators recover planted hop-1 coupling (S-R3a), so the real-data gap comes from structure the simulator lacks. | L1 biased > 25% in synthetic | 0.6 |
| R4-P1 | **Hop 1 carries most of the gain.** Regime-III median g_full = G_5 is within [0.7, 1.5] × the round-1 median g_lag (0.09–0.20). | G_5 ≥ 2.5 × g_lag (H50's plateau) | 0.55 |
| R4-P2 | **The uncorrected hop 2–3 sum was a field.** Regime-III median G_3 < 0.20 (round-1 uncorrected g3 0.28). | G_3 ≥ 0.28 | 0.65 |
| R4-P3 | **Subcritical.** Every unit's G_5 upper bound < 1. | any unit with lower bound ≥ 1 | 0.85 |
| R4-P4 | **Fano closure with the full gain.** Regime-III pooled r_F with Φ_pred(G_5) in [0.8, 1.25] with CI including 1. | pooled r_F < 0.7 | 0.5 |
| R1-P1 | **Coupling on the chat clock.** Regime-I median g_chat ≥ 0.05, and J*_chat > 0 at 95% in ≥ 1/3 of regime-I units. | median g_chat ≤ 0.02 and ≤ 10% of units > 0 | 0.4 |
| R1-P2 | **It explains H111's regime-I excess.** Regime-I pooled r_F with Φ_pred(g_cu + g_chat) in [0.8, 1.25]. | r_F ≥ 1.25 still | 0.3 |
| R1-P3 | **No address gating in regime I.** Named/unnamed J*_chat ratio < 3 (H50: 0.042 vs 0.031). | ratio ≥ 5 with CI excluding 3 | 0.5 |

**Kill rules.**
- If a synthetic criterion fails for an estimator, its real-data number is descriptive only, and the card says so.
- If R3-P1 fails, the ladder result is "not reconciled".

#### Amendment B (2026-10-05 ~03:05 UTC, after the synthetic runs, before any real-data statistic)
*Seen: only synthetic runs on real call grids (`round2/synthetic/summary.json`; 16 replicates per unit × world for R3 and R1, 48 for R4) and two design quantities. The design quantities are H50's per-unit W and the logged chat-call latency spread in regime I (median 9.4 s, σ_log 0.47; calibrated starts σ_log 0.22).*
- **B1 (R4, design fix).** As first written, P_{c−k} and the reads at c−k+1 shared messages: the latency (≈ 9.5 s) exceeds half the call interval (≈ 12.5 s). The windows are now disjoint and symmetric.
  - Half-width h_c = min(latency, half the previous interval, half the next interval, 120 s).
  - R^o_c excludes the in-flight messages of call c−1.
  - Every message enters one regressor only.
- **B2 (R4, design fix).** For k ≥ 1 the two windows straddle t_{c−k}, but the outcome is at t_c. So the in-flight window sits closer to the outcome.
  - With B1 alone, a field biases the increments negative: G_5 = −0.30 in the burst world, −45% in the decaying-kernel world.
  - Fix: each window gets an offset sum Σ (distance from t_{c−k})/h, so its effect is a + b·x. Δ_k compares the boundary limits a (the regression form of a local-linear RD).
- **Synthetic verdicts, R3** (the regime medians of g; truth 0.15 and 0.30).
  - **S-R3a:** L9 (H67) passed (−4.5% / −2.5%, coverage 0.88 / 0.96). L1 (H50's pair RD) failed (+43% / +35%).
  - **S-R3b:** L9 passed (null +0.003, burst −0.019). L1 failed: +0.053 null and +0.072 burst, with the CI excluding 0 in 25% of no-coupling runs.
  - The rung that removes L1's no-coupling excess is the call-class demeaning: L2 → L4W (bandwidth W) +0.062 → +0.021; L3 → L4 (bandwidth w̄) +0.098 → +0.040.
  - The first stage ΔR is 1.06–1.10 in every world.
  - **R3-P5 is therefore failed before real data.** H50's estimator is biased by structure the simulator has: per-agent, per-class talk baselines that differ across the read-out boundary.
- **Synthetic verdicts, R4** (48 replicates × 3 units).
  - **G_1** (the k = 0 boundary of this design) recovers truth: −15% to +6.5%, coverage 0.88–0.93; null −0.012, burst +0.002.
  - **G_5** is very imprecise: the per-run SD is 0.44–1.47 against truths of 0.15–0.33. Median relative error: hop-1 world +92%, decaying world −1%, plateau world −14%. Null +0.060, burst +0.094; coverage 0.89–0.92.
  - **S-R4a failed** (hop-1 world) and **S-R4b failed** (+0.06 and +0.09 > 0.05).
  - **G_3** is also imprecise: SD 0.23–0.74; hop-1 world +57%.
  - **Consequence (kill rule):** the real-data G_3 and G_5 are descriptive only. They are reported as regime-III random-effects pools with this synthetic bias band (up to +0.14 in G_5).
  - Added for R4-P4: the **Fano-implied total gain** g_Fano. It inverts H111's Φ_pred(g) at H111's observed Φ(10) and its CI, with no refit. This is not an independent test: H111 already reported r_F ≈ 1 with g_lag.
- **Synthetic verdicts, R1.**
  - **S-R1a:** passed narrowly (−21%; by unit −50%, −34%, +22%; coverage 0.88). The truth is partly capped by saturation at chat calls.
  - **S-R1b:** passed (null +0.009, burst −0.022; CI ≠ 0 in 12% and 2%).
  - **S-R1c:** passed. The round-1 hop-1 estimator on all calls reads 0.18 × truth in the chat world: regime-I coupling on the chat clock is invisible to it.
  - **S-R1d:** a start-time error at the measured spread (σ_log 0.5) attenuates g_chat to 0.23 × truth (−77%). **The real-data g_chat is a lower bound, at about a quarter to a third of the truth.**
  - **Variants:**
    - The re-indexed all-reads variant g_chat,all is invalid (−2.4 × truth; null −0.35). It is dropped.
    - The logged-start variant has too few rows per unit (unit 27: 890 chat calls; null −0.15). It is reported only as a regime-I pool.

**Round-2 per-period verdicts.**
- **Regime-I periods:** re-apply the round-1 rule on the chat clock. Use g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. The period README's top verdict takes this round-2 verdict, marked "(round 2, chat clock)".
- **Regime-II and regime-III periods:** the top verdict stays as in round 1. A "Round 2" section adds G_5, δ(h) and the ladder values, as descriptive numbers.

### Round 2 results (2026-10-05; 66 non-reserved units, 35 periods)
*Code: `analysis/r2lib.py`, `r2_synthetic.py`, `r2_run.py`, `r2_summarize.py`, `r2_write_periods.py`, `r2_posthoc_mode.py`, `r2_posthoc_mode_null.py`.*
*Data: `data/processed/H67-lagged-criticality-dial/round2/` (`units.parquet`, `periods.parquet`, `summary.json`, `synthetic/`, `posthoc_mode*.parquet`).*
*Figure: `figures/round2_col.pdf`. Rows in `per_period_estimates`:*
- `h50_pair_rd_gain_reimplemented`
- `pair_rd_gain_call_class_cells`
- `readout_loop_gain_multihop_G5` (status descriptive)
- `readout_loop_gain_chat_clock`
- `readout_loop_gain_regimeI_total`

Round 1 reproduces exactly: the L9 rung is the round-1 call, and unit 41 gives g_lag 0.189 again. Every number below is a unit median or a random-effects pool, with a 95% CI.

#### Outcome vs prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| R3-P1 | L1 reproduces H50's J₁ | median L1/L0 0.94; Spearman 0.87 (66 units) | **supported** |
| R3-P2 | regime III: cells + placebo carry ≥ 50%; trimming and bandwidth < 25% each | the pair-RD → call-count rung (L4 → L8) carries the whole gap: median share 1.02, pool 0.96. Cells: −0.07 (median) / +0.32 (pool). Shifted-time placebo alone (L4 vs L5): 0.016 of 0.11. Bandwidth −0.31 (the gap *grows* at w̄). Trimming 0.37 / 0.10 | **failed** |
| R3-P3 | first stage ΔR in [0.8, 1.25] | 1.04 (III), 0.95 (I) | **supported** |
| R3-P4 | regime I: cells remove ≥ 70% of H50's gain (L3 → L4) | 69% (median); 85% at H50's bandwidth (L2 → L4W); 95% (pool) | **failed narrowly** as written; supported in substance |
| R3-P5 | synthetic: both estimators recover planted coupling | L1 +43% / +35%; +0.05 / +0.07 with no coupling | **failed** (before real data, Amendment B) |
| R4-P1 | regime-III G₅ within [0.7, 1.5] × g_lag | median 0.094 (0.73 × g_lag); pool 0.24 [−0.03, 0.51] | descriptive only (S-R4 failed); **inconclusive** |
| R4-P2 | regime-III G₃ < 0.20 | median 0.129; pool 0.096 [−0.045, 0.24] | descriptive only; consistent |
| R4-P3 | every unit's G₅ upper bound < 1 | 26/66 (imprecise); no unit has a lower bound ≥ 1 | **failed** as written (power); not falsified |
| R4-P4 | Fano closure with G₅: r_F in [0.8, 1.25], CI includes 1 | r_F(pooled G₅) 0.78 [0.67, 0.90]. Fano-implied total gain g_Fano 0.149 [0.123, 0.175] vs round-1 g_lag pool 0.127 | **failed** for G₅; the Fano bound sides with hop 1 |
| R1-P1 | regime-I median g_chat ≥ 0.05; J*_chat > 0 in ≥ 1/3 | median −0.008; pool −0.022 [−0.052, 0.009] (36 units); > 0 at 95% in 1/36, < 0 in 4/36 | **failed**; the "counts against" clause is met |
| R1-P2 | g_I explains H111's regime-I excess | r_F(g_I) 1.35 [1.14, 1.60], unchanged from r_F(g_lag) 1.35 | **failed** |
| R1-P3 | named/unnamed < 3 on the chat clock | both ≈ 0 (named −0.002 ± 0.008, unnamed −0.004 ± 0.003) | vacuous |

#### R3: where H50's factor 2 lives (unit medians of g; regime III, 25 units / regime I, 38 units)
| Rung | What changes | Regime III | Regime I |
| --- | --- | --- | --- |
| L0 | H50 published J₁ × m̄ r̄ | 0.235 | 0.248 |
| L1 | H50's pair RD, re-implemented | 0.238 | 0.248 |
| L2 | + all-present window | 0.197 | 0.219 |
| L3 | + bandwidth w̄ (≈ 9.6 s) | 0.231 | 0.132 |
| L4 | + agent × day × call-class cells | 0.239 | 0.041 |
| L4W | L2 + cells (bandwidth W) | 0.242 | 0.032 |
| L5 | L4 without the shifted-time placebo | 0.223 | 0.023 |
| L6 | L4 / first stage | 0.200 | 0.038 |
| L7 | call counts, pooled (no cells) | 0.141 | 0.085 |
| L8 | call counts + cells | 0.128 | 0.004 |
| L9 | H67 main (round 1) | 0.129 | 0.005 |
| L9b | L9 with the window capped at W | 0.148 | 0.008 |

- **Regime I: H50's gain is call-class composition.** Chat-mode calls talk at 0.79 and sit more often on the read-out side of a peer message than on the in-flight side. Demeaning talk within agent × day × call class removes 69–95% of the gain.
  - The synthetic worlds show the same thing with no coupling at all: L1 reads +0.05 there and the cells remove it.
- **Regime III: the gap is the estimator design, not the placebo, bandwidth, normalization or pooling.**
  - Placebo: removing the shifted-time placebo moves the pair RD by 0.016.
  - First stage: ΔR = 1.04.
  - Unit pooling: IVW − RE = 0.000 (median over periods).
  - Post hoc probe P1: a local-constant pair estimator gives 0.177. So about half of the 0.11 gap is the local-linear extrapolation to s = 0, and half is pair sampling (0.177 vs L8 0.128).
- **Which scale is right.** Both estimators recover homogeneous planted coupling. L1 alone carries a no-coupling excess of +0.05 to +0.07.
  - The independent fluctuation measure decides: H111's Φ(10) inverted through H111's own formula gives g_Fano = 0.149 [0.123, 0.175] (25 regime-III units).
  - That matches H67's 0.127 and **excludes H50's scale (0.24)**.
  - g_Fano is an upper bound on the read-out gain, because fields only add variance.
- **H50 effect heterogeneity is not the cause.** Splitting H67's reads into named and unnamed gives 0.121, against 0.129 pooled.

#### R4: multi-generation gain (descriptive)
- **Kernel.** Pooled over 25 regime-III units, the kernel δ(h) per read for h = 1…5 is 0.001, 0.004, 0.004, 0.009, 0.007. CI widths are 0.006–0.017.
- **Gains.** G₁ pool 0.005 [−0.04, 0.05], G₃ 0.096 [−0.05, 0.24], G₅ 0.24 [−0.03, 0.51]. Per-unit G₅ is uninformative: the upper bound is < 1 in 26/66 units.
- **This design cannot resolve hop 1 in real data.** Its G₁ pools to ≈ 0, while the window-average estimator gives 0.127. A likely reason: its boundary limits are sensitive to start-time error at computer-use calls, which the synthetic worlds did not include.
- **What R4 supports.** The uncorrected round-1 g3 (0.28) is not a multi-hop gain. In synthetic field worlds it reads −0.1 to −0.4.
  - The full DC gain is bounded by the Fano-implied total gain, ≤ 0.175 at 95%.
  - So hops 2–5 add at most about 0.05 to hop 1's 0.127.
  - H50's plateau rival (G₅ ≈ 4 g_lag ≈ 0.5) is excluded through the sum rule, which is model-based. The response design alone does not exclude it.

#### R1: the regime-I chat clock
- **Result.** On talk-capable calls, a fresh read does not raise talk beyond messages in flight:
  - g_chat pool −0.022 [−0.052, 0.009]
  - g_cu 0.003 [−0.003, 0.008]
  - g_I −0.015 [−0.047, 0.017] (35 units)
  - The chat calls already talk at 0.79.
- **Bound.** Start-time error attenuates the estimate to about 0.23 × truth (S-R1d). Rescaled, the chat-clock gain is still < 0.04 at 95%.
- **Logged-start variant.** Only 4 regime-I units have enough logged chat starts (pool 0.055 [−0.18, 0.29]): unpowered.
- **Period verdicts (round 2, chat clock).** 21 failed, 2 mixed (G08, G27), 1 supported (G07, one unit; chance level at 24 periods). G05 changes from supported to failed.
- **Post hoc P2** (prompted by H50 round 2: "a read raises the chance that the next regime-I call is chat-mode").
  - With the in-flight design and the call mode as the outcome, a fresh read raises P(chat-mode) by 0.0080 [0.0052, 0.0109] per read.
  - The same design on synthetic worlds built on the real regime-I call skeleton, with no coupling and fixed modes, gives 0.0054 (median over 38 units × 8 replicates). The excess is 0.0021 [0.0000, 0.0042].
  - **About 3/4 of the "read → chat-mode" effect is the scaffold's chat-turn order:** an agent's chat call follows peers' chat posts.
  - Without conditioning on call mode, the read-out talk gain is 0.056 [0.041, 0.070]. Its skeleton-null value is 0.019, so the excess is **0.035 [0.023, 0.046]**.
  - This is a small regime-I coupling that the class cells hide. It is post hoc, and far below the g ≈ 0.13 that H111's regime-I excess (r_F 1.35) would need.

#### Old → new
| Quantity | Round 1 | Round 2 |
| --- | --- | --- |
| H50 vs H67 gap | "factor 2, H50's 120-s bandwidth admits more field" (untested) | regime III: the pair-RD design (local-linear extrapolation + pair sampling), not bandwidth (H50's W is ≈ 19 s), placebo, normalization or pooling; regime I: call-class composition |
| Which regime-III scale is right | unresolved (ρ 0.24) | H67's 0.13: the Fano-implied total gain is 0.149 [0.123, 0.175] |
| Hops 2–3 | g3 = 0.28, not placebo-corrected | not a gain (synthetic field bias); multi-hop G₃ 0.10 [−0.05, 0.24], G₅ 0.24 [−0.03, 0.51] (descriptive); full gain ≤ 0.175 by the Fano bound |
| Regime I | ≈ 0 on the wrong clock | ≈ 0 on the chat clock (−0.022 [−0.052, 0.009]); post hoc 0.035 [0.023, 0.046] when call mode is not conditioned on |
| Regime-I period verdicts | 1 supported, 1 mixed, 22 failed | 1 supported, 2 mixed, 21 failed (chat clock) |

#### Impostors (round 2 additions)
| Impostor | Round 2 | Status |
| --- | --- | --- |
| Scheduler field | Regime I: the chat-turn schedule fakes a read → chat-mode effect (3/4 of it) and a +0.02 mode-free gain; corrected with a skeleton null. H50's pair RD carries a +0.05 no-coupling excess from per-class baselines; removed by cells. | removed (I: by skeleton null, post hoc) |
| Exogenous field | unchanged (human and nudge items as covariates) | partly |
| Shared priors | unchanged (agent × day cells) | removed |
| Convergence | in-flight placebo at every lagged call (R4); local-linear boundary limits | removed for hop 1; R4 descriptive |

#### Scorecard (round 2)
| Axis | Score | Change |
| --- | --- | --- |
| A | 1 | Regime-I mapping checked on the chat clock (null). Not invariant: III ≈ 0.13, I ≤ 0.04. |
| B | 1 | The update order on the chat clock is audited. The multi-hop design is fragile to start-time error. |
| C | 1 | unchanged |
| D | 2 | Up from 1. Two unfitted cross-checks pass: g_lag (response) vs g_Fano (fluctuation, H111 data), 0.127 vs 0.149 [0.123, 0.175]; the first stage ΔR = 1.04 as predicted. |
| E | 1 | unchanged |
| F | 2 | R3 and R1 estimators validated on real call grids, and a regime-I skeleton null was built. R4 failed its synthetic test and is labelled descriptive. |
| G | 1 | unchanged |
| H | 2 | Up from 1. The H50 disagreement is located and resolved. H50's pair RD fails synthetic recovery and exceeds the Fano bound; H42 still agrees in rank. |
| I | 0 | No reserved-data run. |

#### Constants (proposed for `interpretation/swarm-constants.json`)
| Symbol | Value | 95% interval | Scope |
| --- | --- | --- | --- |
| g_Fano (Fano-implied total talk gain) | 0.149 | [0.123, 0.175] | regime III, 25 units, H111 Φ(10) inverted; upper bound on the read-out gain |
| g_chat (chat-clock read-out gain) | −0.022 | [−0.052, 0.009]; attenuation-corrected < 0.04 | regime I, 36 units |
| g_I,mode-free (post hoc) | 0.035 | [0.023, 0.046] | regime I, 38 units, skeleton-null corrected |
| ΔR (first stage at the read-out boundary) | 1.04 | n/a (median) | regime III, 25 units |

#### Round 3 redirects
- **H67-R5. Reserved-data confirmation.** Confirm g_lag ≈ g_Fano on the reserved regime-III units (re-freeze `confirm.py` with a g_Fano clause). This replaces R2's named/unnamed test only if Vivian chooses.
- **H67-R6. Pair-sampling term.** Identify why the pair-weighted contrast (0.18) exceeds the per-call slope (0.13) in regime III. Candidate: messages near a call start select bursty conversation moments. Test with a simulator that has conversation bursts with heterogeneous per-agent gains.
- **H67-R7. A regime-I fast field.** H111's regime-I excess (r_F 1.35) is neither hop-1 nor chat-clock coupling. Test the chat-turn schedule as the field: it reproduces 3/4 of the mode effect. Use the skeleton null on Φ.
- **H67-R8. Multi-hop with a donut.** Rerun R4 with a 2-s donut and start-time error in the synthetic worlds, before any new reading of δ(h).

**Claim that stands:** In regime III the read-out talk loop gain is subcritical and small, g_lag 0.13 (pool 0.127, 25 units), and it agrees with the Fano-implied total gain 0.149 [0.123, 0.175] from H111's fluctuations. H50's twice-larger value comes from its pair-RD design (regime III) and from call-class composition (regime I). On the chat clock, regime I has no read-out gain (−0.022 [−0.052, 0.009]).
- *Excluded:*
  - R4's G₃/G₅ (descriptive; synthetic failed).
  - Post hoc P1 (local-constant split) and P2 (mode-free regime-I gain 0.035).
  - The logged-start chat variant (unpowered).
  - The all-reads chat variant (withdrawn).

## Notes
- 2026-10-04 19:15 UTC: round 1 started; card filled before any real-data statistic. Compute: local, ≤ 4 threads per process; after the coordinator's load notice (~20:25 UTC) ≤ 2 workers, one job at a time.
- 2026-10-04 19:55 UTC: Amendment A1 after the synthetic validation (before real data).
- 2026-10-04 ~20:10–20:30 UTC: replication run (66 units, ~6 min), then the post hoc A2 variants (rerun, ~6 min).
- Data: `data/processed/H67-lagged-criticality-dial/` (41 MB; 42 MB after round 2).
- 2026-10-05 02:47 UTC: round 2 pre-registration (R3, R4, R1) committed before any round-2 statistic. 02:50–03:03 UTC: synthetic runs; ~03:05 UTC: Amendment B (B1 disjoint windows, B2 local-linear offsets; R4 G₃/G₅ declared descriptive). 03:07 UTC: real-data run (66 units, 2 workers, ~15 s), then synthesis.
- 2026-10-05: post hoc P1 (local-constant pair estimator) after the ladder result. Post hoc P2 (call-mode outcome, mode-free gain, regime-I skeleton null) after the coordinator relayed H50 round 2's chat-mode finding. Both are labelled post hoc and excluded from the claim.
- H50 round 2 left a per-pair hop-1 table (`data/processed/H50-field-vs-coupling-transfer-lag/r2/pair_J1.parquet`; read-only). It is not used here. A per-pair comparison of the pair-RD and call-count designs is a natural input to H67-R6.
- Proposed for `physics-models/DEFINITIONS.md` (not edited): *in-flight placebo (matched-lag)*, *read-out loop gain g_lag*.


