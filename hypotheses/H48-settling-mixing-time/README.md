# H48: The settling time is a mixing time on the read-out graph

**Status:** exploratory round 1 done (2026-10-04). **Inconclusive, with the literal (shallow-coverage) version refuted on magnitude.**
- Read-out coverage is fast: in a median period 90% of room-mate pairs have read each other within 0.24 active h (bulk mixing of the read-out chain: 0.02 h). Content settling after a kickoff, where detectable, takes 4.5 active h (bge; 1.9 h gte): about 10× the coverage time and ~80× the bulk mixing time. Settling does not wait for "everyone has read everyone".
- Across periods neither primary predictor (coverage T90, bulk mixing time) beats a constant in leave-one-period-out prediction, in either embedding model (gains −0.01 to −0.14). But S1 settling is detectable in only 11/27 periods (bge; 14/27 gte), below the pre-registered 12, and a post-hoc synthetic with real-like noise shows ~0 power for *any* predictor, so the scaling question is unanswered.
- Natives: NE42 weakly read-out-like for coverage (gte only); G38's slower-covering room settles faster on H20's clock; #51 newcomers do not assimilate at all (they individuate); NE32 unpowered. Predictions, nulls and native designs were written before any real-data run; Amendment 1 after the synthetic. `confirm.py` written, not run.
**Fields:** stat mech, dynamics, sociophysics (consensus on temporal networks)
**Literature:** none in `literature/` covers mixing times or DeGroot consensus. Standard background: DeGroot (1974) averaging; Levin–Peres–Wilmer, *Markov Chains and Mixing Times* (TV mixing time, relaxation time vs mixing time, cutoff); temporal-network reachability (time-respecting paths).
**Definitions used:** Agent (Claude Code agent excluded as reader and as source); Population N(t) (kickoff roster, below); Regime (whitening per regime; #36 crosses the 03-24 boundary and is excluded from settling); Driving / external field (the kickoff, shared `goal_fields`); **Exposure (turn read-out)** via the shared context ledger (DQ1); H31's **exposure spectral gap λ₂** variants (`w,sym`, `w,dir`, `bin`, `rw`) and **interaction (seen, weighted)**, here in a new named variant **interaction (ledger-read, weighted)**; H01's **agent state (vector), whitened statement mean**; H20's **agent-day statement mean** and its MQ kickoff-transient fit; H54's **quench target (kickoff)**, **quench depth** and **kickoff remanence** (here also at sub-day resolution, new variant **kickoff remanence (active-hour)**). New named variants proposed for DEFINITIONS.md (defined under Observables): **read-out coverage C_k(t)**, **coverage time T_q**, **read-out chain (batch / count)**, **bulk mixing time t_mix^bulk**, **time-respecting DeGroot disagreement time τ_DG**, **newcomer assimilation gap**.
**From:** HH173 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (O(32) content spins, DeGroot read-out averaging), `physics-models/10-potts/` (consensus-time scalings, weakest-link pitfall), `physics-models/03-contagion/` (coverage as an SI process on the read-out graph)
**Data inputs (shared tables first):** DQ1 context ledger (`context_ledger_items`, `context_ledger_turns`, `call_windows`); `embeddings/statements` + `statements_white32_{bge_small,gte_modernbert}.npy`; `embeddings/goals.parquet` + `goal_vectors[_gte_modernbert].npy` (kickoff vectors); `embeddings/agent_win30` white32 vectors; `statement_flags` (DQ5); `calendar`, `period_units`, `rooms_timeline`, `roster`. Read-only imports: H20's per-period MQ fits (`data/processed/H20-content-aging/G<NN>/result*.json`) and `h20lib` estimator functions; H54's day-level remanence fits (`data/processed/H54-kickoff-quench-target/G<NN>/results.json`, `kickoffs.parquet`) and `h54est.exp_plateau_fit`; H31's published predictors (`predictors_period.parquet`) and `h31lib` λ₂ functions.

## Question
Is the post-kickoff content settling time set by how many call cycles it takes for every agent to have read every other agent's work (a bulk mixing time on the read-out graph), rather than by whole-graph λ₂ (a weakest-link statistic, H31)? If so, settling should scale with per-agent reading rate, read-out coverage and room structure.

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimators on every eligible goal period (non-holdout, ≥ 5 active days), one phase-diagram point per period. Period README role: `replication`. Predictions there are templated and labelled as such.
- **Period-native tests (4):** NE42 (merge A-B-A changes mixing), G38 (per-agent and per-room reading heterogeneity in the longest two-room regime-III period), G51 (newcomer assimilation across 11 joins as N grows 21 → 32), NE32 (newcomers isolated in their own rooms for a day: the read-out clock should start at the merge). Period README role: `native`.

## Model
**From:** `physics-models/11-vector-spins/` with read-out dynamics; rivals from `10-potts` (λ₂ / consensus-time scalings).

**H48 variant: settling as read-out mixing after a kickoff quench.** Agent i's content state is a vector x_i ∈ R^32 in the regime's whitened basis; statements are noisy unit samples z = unit(h_i + x_i(t) + ε) (h_i: agent style/field). At the kickoff (t = 0) the field switches to the kickoff target k̂_p and every agent is quenched toward it (H54). Afterwards x_i changes **only at its own read-out calls** (H08), using the batch B of agent messages that newly entered that call's context (the ledger's visibility rule):

- **RD (read-out DeGroot with innovation):** x_i ← (1 − α) x_i + α [mean_{m∈B} x_{s(m)}(t_m) + η], η a fresh innovation per reading call. The kickoff component relaxes at a rate ∝ α × (reading-turn rate); disagreement relaxes as the batch read-out chain mixes.
- **RC (coverage completion, the literal HH173 mechanism):** x_i(t) = A k̂_p + w_i + Σ_{j≠i} g(n_ij(t)) w_j with g(n) = 1 − e^{−n/κ}: agent i's content is the kickoff plus the work it has read; it settles once it has read κ-deep from everyone (coverage at depth κ).

Both predict τ_settle ∝ a bulk read-out time (1/(α ū) or T_cov), not 1/λ₂. **Rivals:**
- **FD, field-driven (active-hour clock):** x_i(t) = A k̂_p e^{−t/τ_f} + w_i (1 − e^{−t/τ_f}) + OU noise; τ_f set by the kickoff/goal, independent of reading.
- **FC, own-call clock:** the same with t replaced by agent i's own call count: settling ∝ 1 / call rate (scaffold cadence, not reading).
- **Day clock (memory consolidation):** settling takes one overnight cycle: τ_settle ∝ active hours per day.
- **Weakest link (H31):** τ ∝ 1/λ₂^{w,sym} (min over room blocks), or room count.

## Data scheme (`scheme/`)
`scheme/build.py` (no text anywhere; holdout masked with `common.holdout_mask` on (pt_date, goal_no) before anything is computed; `--allow-holdout` only for `analysis/confirm.py`).
- **Inputs:** `context_ledger_items` (kind = agent; turn_id, message_id, sender), `context_ledger_turns` (turn_id → agent, t_call, room, k_new), `call_windows` (talk, kind), `chat_core` (message time, sender, room), `calendar` (active time), H54 `kickoffs.parquet` (kickoff time t0; fallback: the period's first window start), `roster`.
- **Transform:** per goal period p: kickoff roster R_p = agents (≠ Claude Code) with ≥ 1 call on the first active day; active time since kickoff a(t) = active_offset_s(day) + clip(t − win_start, 0, window_s) − a(t0), in hours. Calls (agent, t_call, a, room, n_agent_items) and reads (reader, sender, a_read, a_msg, room) for agent messages posted at or after t0 by roster agents.
- **Output:** `data/processed/H48-settling-mixing-time/`: `calls.parquet`, `reads.parquet`, `msgs.parquet`, `roster.parquet` (period × agent: kickoff room, join time), `periods.parquet`, per-period results in `G<NN>/`, natives in `NE42/`, `NE32/`, synthetic results in `synthetic/`, `_provenance.json`. Budget ≤ 200 MB.
- **Regimes covered:** I, II, III; one period at a time, never pooled. #51: head only (through 09-06).

## Candidate goal periods
- **Replication (non-holdout, ≥ 5 active days):** #4, #5, #6, #8, #10, #11, #12, #13, #16, #17, #18, #19, #20, #21, #24, #25, #26, #27, #30, #31, #35, #38, #39, #40, #41, #42, #51 (head) = 27 periods. #36 (crosses the regime boundary on day 2): predictors only, no settling. #23: excluded from kickoff-alignment settling, following H54 (kept blind for H10's confirmatory #22 → #23 pair); predictors computed.
- **Native:** NE42 (#39 → #40 → #41), G38, G51 (head), NE32 (07-09 → 07-10).
- **Holdout (confirmation only):** see Prediction / `analysis/confirm.py`.

## Observables
*Specified 2026-10-04, before any real-data run.*

**Settling (outcome), per period, for each embedding model m ∈ {bge_small (primary), gte_modernbert}:**
- **S1, kickoff remanence at active-hour resolution (primary τ_settle).** Bins of 1 active hour from t0, up to min(T, 10 active days). Agent-bin vector v_ib = unit(mean of i's unit white32 statements in bin b), n ≥ 2 statements; bins with ≥ 3 agents. Kickoff excess A_ex(b) = mean_i cos(v_ib, k̂_p) − mean_{q≠p} mean_i cos(v_ib, k̂_q), decoys = the other eligible non-holdout kickoffs in the same regime basis (H54 rule). Fit A_ex(t) = A_∞ + (A_0 − A_∞) e^{−t/τ_S1} (H54's `exp_plateau_fit`, τ on a geometric grid 0.25 h … 4× span, weights = agents per bin). **Detected** if ΔBIC(constant − exponential) ≥ 2, A_0 > A_∞ and τ below the grid's top. τ_S1 in active hours.
- **S2, H20's kickoff transient τ_q.** H20's estimator recomputed from the shared white32 statements (agent-day means, n ≥ 8, C(d, d′) ratio of sums, entries t_w ≥ 2, τ ≤ ⌊(T − 1)/2⌋, MQ fit with `h20lib.fit_model`). τ_q in active days, × the period's median active hours per day. Validated against H20's published bge fits. Detected if b² ≥ 0.1 and τ_q inside the bounds.
- **S3, H54's day-level τ_K** (bge, imported read-only). Descriptive cross-check.
- **S4 robustness:** S1 with `statement_flags.templated` and `self_repeat_both` statements removed; S1 chat-only.
- **S5, pairwise-alignment relaxation (H31 E-C):** within-room mean pairwise cosine of agent_win30 white32 vectors fitted with the same plateau form, in active hours. Descriptive.

**Read-out predictors, per period** (early window = kickoff to the end of active day 2, unless stated):
- **(a) Read-out coverage C_k(t):** the share of ordered pairs (i, j) of the kickoff roster, i ≠ j, such that i has read ≥ k messages that j posted after t0, by active time t. Pair sets: **room-reachable** (i, j in the same kickoff room; primary) and **all pairs**. Depths k = 1 (primary), 5. **Time-respecting reachability coverage** C_tr(t): i has a time-respecting read path from j's post-kickoff output. **Coverage time T_q** = first t with C ≥ q, q ∈ {0.5, 0.9}; right-censored at the period end. Primary: **T90 = T_0.9 of C_1 over room-reachable pairs**, in active hours. Also in call cycles (÷ median per-agent median inter-call interval) and reading cycles (× median reading-turn rate).
- **(b) Bulk mixing time.** Ledger-read weighted graph W_ij = j's messages read by i per active hour (early window). **Batch chain** (primary): generator Q_ij = u_i W_ij / Σ_k W_ik (u_i = i's reading-turn rate). **Count chain:** Q = W − diag(W1). Per room block, t_i = min{t : TV(e_i e^{Qt}, e_i e^{Q∞}) ≤ 1/4}; **t_mix^bulk** = median over roster agents of t_i; **t_mix^worst** = max (the weakest-link contrast). **τ_DG:** DeGroot (batch mean, α = 0.1; robustness 0.03, 0.3) simulated on the real read sequence from t0 with random initial vectors; the time at which within-room disagreement falls to 1/e (bulk) and the time the worst agent's falls to 1/e (worst).
- **(c) Reading rate:** median over roster agents of reading turns (≥ 1 new agent item) per active hour; reads per active hour; call rate.
- **(d) Rivals (λ₂):** H31's λ₂^{w,sym}, λ₂^{w,dir}, u·λ₂^{rw} on the ledger graph (min over room blocks = the whole reachable graph's weakest link); H31's published λ₂^{w,sym} and γ_tr (#10–#44) as published.
- **(e) Room structure:** number of rooms with ≥ 3 roster agents, N, the room-reachable share of pairs.
- **Other rivals:** active hours per day (day clock); median call rate (own-call clock).

**Test (cross-period, never pooled fits):** each period is one point. Leave-one-period-out (LOPO) prediction of log τ_settle by log x (free slope; n_rooms linear), against M0 = the training mean. Metric: LOPO RMSE; ΔRMSE vs M0; permutation p (predictor permuted across periods, 2,000×, full LOPO recomputed). Also with regime intercepts (log τ = a_regime + b log x vs regime means): the within-regime version.

## Null / baseline
- **N0 constant (field / kickoff clock):** τ_settle is a constant across periods (M0). The strongest practical null.
- **N1 permutation:** predictor values shuffled across periods (exchangeability of periods).
- **N2 rivals:** λ₂ variants, room count, N, day clock, own-call clock (above).
- **N3 synthetic truths** RD, RC, FD, FC on the real read-out schedules and real statement times/counts, through the identical S1 estimator and LOPO test: which predictors win under which truth, size under FD, power under RD/RC.
- **Known confounds:** regime (call cadence, rooms, N and hours per day all change together at NE14 / 03-24); goal type (kickoff strength); period length bounds τ; the visibility rule has low-confidence starts in regimes I/II (scheduled chat-mode calls); agents read only their own room (cross-room pairs are structurally unreachable).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** FD (field clock), FC (own-call clock), day clock, weakest-link λ₂ (H31), room count.
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (targets #1, #15, #28, #29, #47, #50; content modality, content_alignment family; `holdout_ledger.check()` allows all six with disclosure) is written and dry-run on stand-ins, not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Coverage, mixing and λ₂ come from the DQ1 ledger (visibility rule, call times); settling from shared whitened statements and kickoff vectors; assumptions listed. Not invariant: regime-I/II call starts are low-confidence (scheduled chat calls), the kickoff target is missing in private-goal #51, and room-level coverage times are set by single silent agents. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Update order is the real read sequence. The single-exponential settling shape fails in most periods: fast drops within 1 h then slow recovery (#38), multi-day declines (#12, #40), or no kickoff signal (#11, #51); only 41–52% fit as detected relaxations. Call-cycle and active-hour clocks both reported. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | Neither primary beats the constant (LOPO gain T90 −0.10 / −0.14, t_mix −0.01 / −0.06, bge / gte; permutation p 0.30–0.89). Also within regime (−0.08, −0.12). |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | Magnitude fails: τ_S1 / T90 = 10 (IQR 3–19; gte 4.5), τ / t_mix ≈ 78. Bulk does not beat worst-case (0/3 pairs). #51 newcomers do not assimilate (premise fails, 3/11). Post hoc: τ ≈ depth-5 coverage (ratio 1.4–1.5 in both models). |
| E interventional | predicts the change across a natural experiment | 0 | NE42: τ follows block coverage in rank for gte (ρ 0.90, exact p 0.04) but not bge (0.30), and not bulk mixing (≤ 0.10); the merged room settles slower, as its coverage is slower (one contrast). NE32 unpowered (1/4 isolated arms spoke). Not counted. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | At the pre-registered SNR, S1 detects 93–100%, the primaries identify read-out truths (pass 0.97–1.00) with size 0.00–0.03 under field and own-call clocks. At real-like noise (detection 37–70%) power is ≈ 0 for every predictor. Robust to DQ5 flags (ρ 0.97), chat-only (0.88), embedding model where both detect (0.80). |
| G ground truth | agrees with known structure | 1 | The ledger reproduces known structure: no cross-room reads; 0 agent reads during NE32 isolation; merge raises reachable pairs 0.57 → 0.87. S2 recompute matches H20's published τ_q (ρ 0.92); S1 ranks match H54's day-level τ_K (ρ 0.81, n 8). No ground truth for settling times. |
| H comparative | beats the named rivals | 0 | Nothing beats the constant robustly: λ₂ variants (gain ≤ 0.05), room count (−0.13), call rate (−0.19); N (0.25, p 0.01) and depth-5 coverage (0.22, p 0.02) only with bge, and not with gte. λ₂ and reading rate are nearly collinear across periods (r 0.90), so the rival comparison cannot separate them anyway. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Nothing to transfer; holdout not run. |

## Prediction
*Written 2026-10-04 (UTC ~06:40), before running any analysis on real data.*

**What I had seen when writing this:** the round-1 results of H20 (no aging; #38's lag-1 correlation relaxes over ~4 active days, then flat; τ ≈ 2–11 days for the stationary part), H54 (kickoff excess 0.24 → plateau 0.11 within ~1–2 active days, τ_K median ≈ 1.2 active days ≈ 5 active h; plateau positive in 25/28), H31 (whole-graph λ₂ is a weakest-link volume proxy; bulk predictors recover slope ≈ 1 in synthetics; content alignment relaxes 0.64 → 0.29 with τ ≈ 4.4 h), H47 (content co-moves within rooms; boundary follows the channel at NE42), H26, H08 (responses gated by read-out), DQ1's validation (median visibility lag 18/19/50 s in regimes I/II/III), and calendar/period-unit structure (days, N, rooms, hours). No coverage, mixing or per-period settling numbers.

**Prior, stated plainly.** Rooms are broadcast: every message reaches every room-mate at its next call, within about a minute in regime III. So direct coverage (k = 1) should complete within the first active hours, faster than the ~5 h kickoff remanence and far faster than H20's ~4-day relaxation. I expect the magnitude claim to fail. Across periods, settling may still *scale* with bulk read-out times, because both shrink with reading rate. But reading rate, call cadence, N, rooms and hours per day all change together at the regime boundaries, so I expect the bulk predictors to beat the constant mostly through regime, and the within-regime test to be weak.

**Primary (P1, replication layer, bge S1):**
- **Supported** if T90 (room-reachable, k = 1) *or* t_mix^bulk (batch chain) has LOPO RMSE ≥ 10% below M0 with permutation p_Holm < 0.05 (Holm over the two), *and* the winning bulk predictor has lower LOPO RMSE than every λ₂ variant and room count, *and* the gte S1 replicate gives the same verdict.
- **Failed** if neither bulk predictor beats M0 by ≥ 10% (or p_Holm ≥ 0.05).
- **Mixed** otherwise (beats M0 but not a rival; or only one embedding model; or only without regime intercepts).
- **Inconclusive** if fewer than 12 periods have a detected S1 settling, or if the synthetic power under RD/RC is < 0.5.
- **Credence:** 0.20 supported, 0.45 failed, 0.25 mixed, 0.10 inconclusive.

**Secondary predictions:**

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P2 magnitude | median over periods of τ_S1 / T90 lies in [1/3, 3] (settling ≈ the time to read everyone once) | ratio > 3: coverage is much faster than settling | 0.20 |
| P3 bulk vs weakest link | bulk versions beat their worst-case versions in LOPO RMSE: T90 vs T100-type (T_0.99), t_mix^bulk vs t_mix^worst, τ_DG bulk vs worst | worst-case wins | 0.50 |
| P4 within regime | with regime intercepts, the primary bulk predictor still beats the regime-means model by ≥ 5% | ≤ 0: the cross-period signal is regime | 0.25 |
| P5 models agree | bge and gte τ_S1 rank-correlate (Spearman ≥ 0.6) over periods detected in both | ρ < 0.6 | 0.65 |
| P6 DQ5 robustness | τ_S1 with templated / self_repeat_both removed rank-correlates ≥ 0.8 with the primary | ρ < 0.8 | 0.70 |
| P7 S1 vs S2 | H20's τ_q (hours) and τ_S1 rank-correlate positively (ρ > 0.3) where both are detected | ρ ≤ 0.3: the two "settlings" are different processes | 0.35 |
| P8 detection | S1 settling detected in ≥ 60% of replication periods (bge) | fewer | 0.60 |
| P9 day clock | the day clock (active hours/day) does not beat M0 by ≥ 10% | it does: settling is one overnight cycle | 0.55 |
| P10 λ₂ | no λ₂ variant beats M0 by ≥ 10% with p < 0.05 (weakest link, H31) | one does | 0.65 |

**Synthetic validation predictions (axis F; before the synthetic run):**
- F1: under RD, t_mix^bulk (batch) and reading rate beat M0 in LOPO in ≥ 70% of synthetic datasets; λ₂^{w,sym} in fewer.
- F2: under RC (κ = 5), T90 at depth 5 beats M0 in ≥ 70%; T90 at depth 1 in ≥ 50%.
- F3: under FD, every predictor's false-positive rate (beats M0 by ≥ 10% with p < 0.05) is ≤ 0.10.
- F4: under FC, call rate wins and the reading-based predictors also beat M0 often (they co-vary with call rate): an identifiability limit, quantified rather than predicted (credence 0.6 that ≥ 1 reading predictor passes in ≥ 30% of FC datasets).
- F5: S1 recovers the planted τ (RD/FD) with rank correlation ≥ 0.7 across periods.

### Synthetic validation (axis F) and Amendment 1
*Run 2026-10-04 ~07:45 UTC, after the predictions above and before any content was read. Script `analysis/synthetic.py`; output `data/processed/H48-settling-mixing-time/synthetic/` (27 real schedules, real statement times/counts, 30 datasets per truth, LOPO with 1,000 permutations; parameters in `summary.json`).*

| Truth | S1 detected | S1 recovers planted τ (ρ) | Pass rate (gain ≥ 10%, p < 0.05): T90 k1 / T90 k5 / t_mix bulk / reading rate / λ₂^w,sym / n_rooms | Full P1 rule (M0 clause; + rivals) |
| --- | --- | --- | --- | --- |
| RD read-out DeGroot (α = 0.004) | 0.93 | 0.56 | 0.33 / 0.40 / **0.97** / **1.00** / 0.93 / 0.63 | 0.97; 0.30 |
| RC coverage completion (κ = 5) | 1.00 | – | **0.97** / **0.93** / **1.00** / 0.97 / 1.00 / 0.93 | 1.00; 0.63 |
| FD field clock (τ_f ~ lognormal, median 5 h) | 1.00 | 0.96 | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 / 0.03 (max over all 19 predictors 0.03) | 0.00; 0.00 |
| FC own-call clock | 1.00 | 0.53 | 0.00 for every predictor, call rate included (call rates vary only ~2× across periods) | 0.00; 0.00 |

- F1 holds for bulk mixing and reading rate (0.97, 1.00) but **not** its λ₂ clause: in broadcast rooms λ₂^{w,sym} tracks reading volume, so under the true RD it predicts as well as bulk mixing (0.93). F2 holds (T90 k5 0.93, T90 k1 0.97). F3 holds (size ≤ 0.03). F4 is wrong in the safe direction: the own-call clock is not mistaken for read-out (0/30). F5 holds for FD (0.96), not for RD/FC (0.53–0.56; their planted τ is only the median agent's).
- T90 at depth 1 is diagnostic only under RC (0.97), weak under RD (0.33); t_mix^bulk is diagnostic under both. The time-respecting DeGroot at α = 0.1 (τ_DG) is not diagnostic under either (≤ 0.23): at that α it saturates within a few reads.
- Under RD the settling time is ~25× the direct coverage time (synthetic median τ̂ 6 h vs T90 ≈ 0.25 h), so **P2's magnitude test only tests the shallow-coverage version of the mechanism**, not read-out-driven settling in general.

**Amendment 1 (2026-10-04, before any real-data settling run).**
1. **P1 is decided by the M0 clause** (a bulk predictor beats the constant by ≥ 10% with p_Holm < 0.05, in both embedding models): its power is 0.97 (RD) and 1.00 (RC) and its size 0.00 (FD, FC). The rival clause (beats every λ₂ variant and room count) has power 0.30 (RD) / 0.63 (RC) and is reported as a secondary comparison (axis H), not as a condition for "supported". New reading: **supported** = M0 clause passes in both models *and* the bulk predictor beats the rivals; **read-out-like, not separated from λ₂** (verdict "mixed") = M0 clause passes but rivals are not beaten; **failed** = the M0 clause fails. The "inconclusive on power" clause does not apply (M0-clause power ≥ 0.97).
2. t_mix^bulk (batch chain) is the more general primary; T90 is primary only for the coverage version (RC). Holm over the two is unchanged.
3. P2 (magnitude) is reinterpreted as a test of shallow coverage (RC with κ ≈ 1–5), not of H48 as a whole.

**Native tests (predictions in the folders, dated before their runs):** NE42 (5 room-blocks across the A-B-A: τ_S1 ordered as T90), G38 (per-agent: agents who finish reading their room-mates later settle later; #best vs #rest), G51 (newcomer assimilation time grows with N and with the newcomer's coverage time), NE32 (isolated newcomers do not assimilate before the merge; their clock starts at the merge).

**Multiplicity:** one primary test (P1, Holm over two predictors, two embedding models required to agree). Secondary predictors are reported with their permutation p, uncorrected, and labelled exploratory. Native tests: four, each with its own primary; reported uncorrected with the count stated.

## Results by goal period
| Period | Role | Verdict | Key numbers (τ in active h, bge / gte; * = not detected) |
| --- | --- | --- | --- |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | failed | per-agent settling undetectable (0/12 bge); #rest covers in 10.8 h vs #best 0.02 h but settles faster on H20's clock (gte τ_q 1.6 vs 12.3 d); replication S1 1.5*/17.3* (rooms) |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | failed | newcomers do not assimilate (decaying gap 3/11; median gap −0.16 → ≈ 0 by 9–13 h: they individuate); N-sweep test untestable; replication S1 not detected (no kickoff target) |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | mixed | 5 room blocks: ρ(τ_S1, T90) 0.30 bge / 0.90 gte (exact p 0.34 / 0.04); ρ with t_mix ≤ 0.10; merged #40 settles slower (20 vs 6.7 h) as it covers slower |
| [NE32](goalperiod-subhypotheses/NE32/README.md) | native | n/a | isolation confirmed (0 agent reads); 3/4 arms said ≤ 1 thing in 1.5–2.5 h of isolation; unpowered |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | n/a | τ_S1 1.7* / 1.6* h; T90 0.10 h; depth-5 T90 0.24 h; t_mix 0.014 h |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | failed | τ_S1 0.4 / 0.9 h; T90 0.10 h; depth-5 T90 0.43 h; t_mix 0.015 h |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | n/a | τ_S1 9.6* / 132.0* h; T90 0.09 h; depth-5 T90 0.87 h; t_mix 0.022 h |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | n/a | τ_S1 0.3* / 116.0* h; T90 0.05 h; depth-5 T90 0.65 h; t_mix 0.023 h |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | supported | τ_S1 1.0 / 2.6 h; T90 0.81 h; depth-5 T90 0.96 h; t_mix 0.031 h |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | n/a | τ_S1 60.0* / 60.0* h; T90 0.23 h; depth-5 T90 2.76 h; t_mix 0.020 h |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | n/a | τ_S1 56.0* / 56.0* h; T90 0.11 h; depth-5 T90 0.35 h; t_mix 0.015 h |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | n/a | τ_S1 0.6* / 0.9* h; T90 0.20 h; depth-5 T90 0.66 h; t_mix 0.014 h |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | n/a | τ_S1 30.2* / 10.1* h; T90 0.11 h; depth-5 T90 1.06 h; t_mix 0.019 h |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | n/a | τ_S1 0.2* / 0.2* h; T90 0.21 h; depth-5 T90 1.29 h; t_mix 0.018 h |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | n/a | τ_S1 1.3* / 3.3 h; T90 0.58 h; depth-5 T90 1.65 h; t_mix 0.022 h |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | supported | τ_S1 0.8 / 156.0* h; T90 0.47 h; depth-5 T90 2.17 h; t_mix 0.014 h |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | mixed | τ_S1 4.7 / 5.5 h; T90 0.24 h; depth-5 T90 1.61 h; t_mix 0.022 h |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | mixed | τ_S1 4.5 / 0.4 h; T90 0.26 h; depth-5 T90 1.16 h; t_mix 0.026 h |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | n/a | τ_S1 76.0* / 76.0* h; T90 0.09 h; depth-5 T90 1.63 h; t_mix 0.024 h |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | n/a | τ_S1 0.3* / 1.3 h; T90 0.48 h; depth-5 T90 1.43 h; t_mix 0.019 h |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | mixed | τ_S1 1.6 / 1.0* h; T90 0.10 h; depth-5 T90 1.14 h; t_mix 0.021 h |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | mixed | τ_S1 5.1 / 1.0 h; T90 0.50 h; depth-5 T90 1.96 h; t_mix 0.032 h |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | n/a | τ_S1 0.6* / 0.7 h; T90 0.08 h; depth-5 T90 0.89 h; t_mix 0.020 h |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | n/a | τ_S1 5.6* / 0.2* h; T90 0.28 h; depth-5 T90 1.15 h; t_mix 0.018 h |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | supported | τ_S1 0.6 / 1.0 h; T90 0.62 h; depth-5 T90 2.61 h; t_mix 0.025 h |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | τ_S1 6.2 / 17.3 h; T90 1.00 h; depth-5 T90 7.06 h; t_mix 0.085 h |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | failed | τ_S1 17.3 / 17.3 h; T90 0.57 h; depth-5 T90 8.16 h; t_mix 0.026 h |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | τ_S1 7.0 / 11.6 h; T90 0.15 h; depth-5 T90 2.35 h; t_mix 0.032 h |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | n/a | τ_S1 5.0* / 2.8 h; T90 5.65 h; depth-5 T90 17.26 h; t_mix 0.048 h |

Replication verdict rule (templated, pre-registered): supported = S1 detected, inside the T90 model's LOPO 80% interval and τ/T90 ≤ 3; mixed = inside the interval only; failed = outside; n/a = no detected settling. 27 replication periods: 3 supported, 8 mixed, 2 failed, 14 n/a (G38 and G51 are listed as native). These are 27 points of one estimator, not 27 independent tests.

## Results
*Exploratory round 1, 2026-10-04; 27 non-holdout replication periods (#4–#51 head) plus #23 and #36 for predictors only; no holdout row read. Code: `scheme/build.py`; `analysis/h48lib.py`, `readout.py`, `synthetic.py`, `settling.py`, `compare.py`, `natives.py`, `period_folders.py`, `figures.py`, `estimates_rows.py`, `confirm.py`. Data: `data/processed/H48-settling-mixing-time/` (`readout_period.parquet`, `readout_block.parquet`, `settling_period.parquet`, `compare.json`, `compare_lopo.parquet`, `synthetic/`, `NE42/`, `G38/`, `G51/`, `NE32/`, `estimates_H48.parquet`). Figures: [`figures/H48_summary_obs.pdf`](figures/H48_summary_obs.pdf), [`figures/H48_synthetic.pdf`](figures/H48_synthetic.pdf), [`figures/H48_coverage_and_settling.pdf`](figures/H48_coverage_and_settling.pdf).*

**Headline.** In the AI Village everyone reads everyone within minutes, yet content keeps relaxing after a kickoff for hours. Settling is not the time to read everyone once. Whether it scales with a slower, bulk read-out time could not be decided: the settling estimate is too noisy per period to rank-test anything.

**Read-out graph (no content).**
- Rooms are broadcast. Over the replication periods the median times are: 50% of room pairs covered 0.03 active h after the kickoff; 90% (T90) 0.24 h (10–90% range 0.09–0.91 h); depth-5 coverage 1.4 h (0.56–7.5 h).
- The batch read-out chain mixes (median start, TV ≤ 1/4) in 0.022 h (0.015–0.038 h); median reading-turn rate 48 per active h.
- Long T90s are weakest-link artifacts: one rarely posting agent sets the whole room's coverage (#38 #rest 10.8 h, #42 5.6 h).
- Cross-room pairs are never read (the ledger's visibility rule). The NE42 merge raises the reachable share of all pairs from 0.57 to 0.87 and back to 0.58.
- Whole-graph λ₂^{w,sym} tracks the reading rate across periods (r = 0.90), so λ₂ and "bulk" rates are nearly interchangeable here.

**Settling (outcome).**
- **S1 (kickoff excess at 1-h resolution)** is detected in 11/27 periods with bge and 14/27 with gte. Median τ_S1 is 4.5 h (IQR 1.0–6.2) with bge and 1.9 h (0.9–5.5) with gte.
- Where both models detect, they agree (ρ = 0.80, n = 9). S1 is robust to DQ5's flags (0.97) and to chat-only statements (0.88). With per-room kickoff vectors (only #38, #39 and #42 have them) τ barely changes, except #38 with bge, which becomes detectable at 1.8 h. Its ranks match H54's day-level τ_K (0.81, n = 8). It is unrelated to pairwise-alignment relaxation S5 (ρ 0.0, n = 7; median 1.8 h).
- **S2 (H20's MQ τ_q)** is only identifiable in the 10 long/medium periods: 5-day periods give 5 two-time entries for 6 parameters, and H20 did not fit them either. Recomputed from the shared white32 vectors it matches H20's published fits (ρ 0.92). Median 7.8 h (≈ 2 active days). It overlaps with S1 in only 3 periods.
- The shapes are heterogeneous: a fast drop within an hour followed by slow recovery (#38, #4), steady multi-day declines (#12, #40), or no kickoff signal (#11; #51's private goals).

**Outcome vs prediction**

| Prediction | Expected | Observed | Outcome |
| --- | --- | --- | --- |
| P1 primary: T90 or t_mix beats M0 by ≥ 10% (p_Holm < 0.05), both models | 0.20 supported | gains: T90 −0.10 (bge) / −0.14 (gte); t_mix −0.01 / −0.06; p_Holm ≥ 0.60. Only 11 periods detected (< 12) | **inconclusive** by the pre-registered count rule; point estimates against H48 |
| P2 magnitude: median τ/T90 in [1/3, 3] | 0.20 | 10.1 (IQR 2.9–18.6) bge; 4.5 gte; τ/t_mix ≈ 65–78 | **failed** (settling ≫ shallow coverage) |
| P3 bulk beats worst case (3 pairs) | 0.50 | 0/3: T99 beats T90 (RMSE 1.04 vs 1.37); worst ≈ bulk for t_mix and τ_DG | **failed** |
| P4 within regime (regime intercepts) | 0.25 | T90 −0.08, t_mix −0.12 | **failed** |
| P5 bge vs gte τ ranks ρ ≥ 0.6 | 0.65 | ρ 0.80 (n 9, p 0.009) | holds |
| P6 DQ5-robust ρ ≥ 0.8 | 0.70 | ρ 0.97 | holds |
| P7 S1 vs S2 ρ > 0.3 | 0.35 | n = 3 overlap (S2 only in long periods) | untestable |
| P8 S1 detected in ≥ 60% | 0.60 | 41% (bge), 52% (gte) | **failed** |
| P9 day clock does not beat M0 by ≥ 10% | 0.55 | gain 0.13 (p 0.06) bge; −0.01 gte | failed literally (bge), not significant |
| P10 no λ₂ variant beats M0 by ≥ 10% | 0.65 | best λ₂ gain 0.05 (p 0.13) | holds |
| Natives: NE42 / G38 / G51 / NE32 | 0.35 / 0.25 / 0.25 / 0.4 | mixed / failed / failed (premise) / n/a | see the folders |

**Synthetic validation (Amendment 1 and a post-hoc power check).**
- At the pre-registered SNR the design works. The primaries win under read-out truths (pass 0.97–1.00), the field and own-call clocks give no false positives (≤ 0.03), and S1 recovers a planted field clock (ρ 0.96).
- **Post hoc** (2026-10-04, after the real-data run, labelled as such): the noise was re-calibrated to the real detection rate with A = 0.25, σ = 1.3 and a shared day drive of 0.3; S1 then detects 63% (RD), 37% (RC) and 70% (FD).
  - At that noise level every predictor's pass rate is ≤ 0.12, under every truth.
  - S1 recovers the planted RD τ with ρ 0.22 only.
- **So the real-data null is uninformative about scaling.** What survives is the magnitude result and the descriptive read-out facts. Even under the true RD at α = 0.004 per reading turn, τ (≈ 4.6 h) is ~20× T90, so P2's failure refutes only shallow coverage (κ ≈ 1), not small-α read-out averaging.

**Post hoc leads (not tests).**
- With bge, depth-5 coverage T90 predicts τ_S1 (LOPO gain 0.22, p 0.017, slope 0.94) and matches its magnitude (median ratio 1.43; gte 1.47). N predicts too (gain 0.25, p 0.013, slope 2.1).
- Neither replicates with gte (−0.11, 0.02), and both co-vary with regime and hours per day.
- `confirm.py` freezes the depth-5 rule as C2 for the holdout.

**Synthesis.**
1. **Settling is not a read-out bottleneck.** In broadcast rooms coverage and mixing are a minute-scale property of the scaffold: every agent's next call sees the room. Content relaxes on an hour-to-day scale. If read-out drives it, each read moves an agent only slightly (α of order 1/250 per reading turn), or it takes several reads per pair (depth ≈ 5). Shallow "has everyone read everyone" is not the clock.
2. **The phase-diagram design is noise-limited, not falsified.** Period-level settling estimates are too heterogeneous in shape and too noisy (41–52% detectable) for a 27-point LOPO test to have power. A hierarchical estimator or message-level α estimates are needed (round 2).
3. **Natives point away from read-out as the main driver.**
   - In G38 the room that took 11 h to cover settled faster on H20's day clock.
   - #51 newcomers do not converge toward the swarm after reading it; they individuate, as H54's private-goal pinning predicts.
   - Only NE42 is weakly consistent, and only for coverage in one embedding model.

**Caveats.**
- The settling estimand is fragile: S1 detection fails in half the periods; S2 exists only for long periods; S1, S2 and S5 measure different things (S1–S5 ρ ≈ 0).
- The bge and gte detected sets differ (9 of 16 periods overlap), so the LOPO tables are on different periods.
- Coverage counts chat messages only, not artifacts (repos, docs) agents may read through tools.
- Regime-I/II read times use low-confidence scheduled-call starts.
- Multiplicity: 19 predictors × 2 models × 2 designs are reported uncorrected except P1 (Holm over 2). The bge "leads" are what you'd expect from that many looks.
- The real-like synthetic calibration was chosen after seeing the real detection rate (post hoc).


## Notes
- 2026-10-04: promoted from HH173 (Vivian). Card, observables, nulls, predictions and native designs written before any real-data run.
- 2026-10-04: synthetic validation run before any content was read (Amendment 1 written then). Real-data settling, comparison and natives run afterwards, in that order. Native predictions were dated before their runs (the read-out predictors, which use no content, were computed first).
- 2026-10-04: post-hoc power check (`synthetic.py --tag realistic --A 0.25 --sigma 1.3 --day-sd 0.3`), labelled as post hoc in Results.
- 2026-10-04: H20's MQ fit is unidentified for 5-day periods (5 two-time entries, 6 parameters). H20 fitted only long and medium periods; this is confirmed here, and S2 is restricted to those.
- 2026-10-04: per-period estimates in the shared schema are in `data/processed/H48-settling-mixing-time/estimates_H48.parquet` (189 rows, validated with `estimates.validate`). Merging them into the shared table is left to the coordinator.
- Proposed DEFINITIONS.md variants (H48): **read-out coverage C_k(t)** (share of kickoff-roster ordered pairs where i has read ≥ k post-kickoff messages of j; room-reachable or all pairs); **coverage time T_q**; **time-respecting reachability coverage**; **read-out chain (batch: Q_ij = u_i W_ij/Σ_k W_ik; count: Q = W − diag(W1))**; **bulk mixing time** (median-start TV ≤ 1/4) vs **worst-case mixing time**; **τ_DG** (time-respecting DeGroot disagreement to 1/e); **kickoff remanence (active-hour)** (H54's A_ex in 1-h bins); **newcomer assimilation gap** g_n = b − s_n.
- 2026-10-04: the shared simulator's `degroot` preset averages over the previous 30-min window's room statements, not per-call read-outs, so the synthetic for H48 runs its own per-call read-out dynamics on the ledger schedules (`analysis/synthetic.py`); a cross-check with the shared simulator's field-driven content model (ContentModel `ou` with `A_k`, J = 0) was planned but not run in round 1.

## Round 2 redirects
- **H48-R1. Message-level α.** Estimate the per-read pull of read content on an agent's next statements (H29's influence coupling on ledger read-outs, matched age bins), per period. Predict τ_settle = 1/(α·u) and test that against S1/S2. This tests small-α read-out directly, without the noise-limited cross-period design.
- **H48-R2. A settling estimator with power.** Hierarchical (partial pooling within regime, exception (d)) kickoff-excess curves with day effects removed, or agent-level remanence pooled within a period. First check on synthetic data at real-like noise that it recovers planted τ (ρ ≥ 0.7).
- **H48-R3. Depth-5 coverage (post hoc lead).** Test on the holdout (confirm.py C2). Mechanistically: do agents need several messages per peer before their content moves?
- **H48-R4. Newcomer individuation (from G51).** Newcomers start generic and diverge within a day. Measure the time to own-role alignment against their own call count and their reads of role-relevant messages (links to H54's private-goal pinning).
