# H122: A batch join is a spin addition: do incumbents respond as the fitted couplings say? (NE27, NE33)

**Status:** exploratory round 1 done (2026-10-04; non-holdout only). **The HH fails: a constant field shift predicts incumbents' first two days after a join better than fitted newcomer couplings.**
- The constant shift beats the couplings in 6 of 10 joins, including NE32, NE33's stand-in (ΔLL −3.7 [−6.9, −0.2] nats per 1,000 calls; the kill fires). Couplings win in 1 of 10.
- Post hoc: without the #51 kickoff day in PRE, NE32's kill weakens to −1.6 [−3.8, +0.7]. Kickoff fields sit inside several join windows.
- Newcomers do couple, and naming carries it: named newcomer reads exceed unnamed ones in 8/10 events. In 2 of 3 resolved events, days 1–2 couple like days 3–7.
- NE27 (regime I): no resolved coupling; the incumbents' step lies inside the regime-I kickoff placebo range; underpowered (power 0.47–0.64). NE33 is confirmation-only and blind.
- Scorecard A1 B1 C1 D0 E1 F1 G1 H0 I0. `confirm.py` (NE33) frozen, guarded and dry-run; **not run**.
(Card, observables and predictions written 2026-10-04 22:05 UTC, before any real-data statistic; approved by Vivian in the dashboard vetting panel 2026-10-04 from HH363.)
**Research question (GOALS.md):** **Q1** (what couples agents?): if newcomers' couplings, fitted after the fact, predict how incumbents respond on the first two days, the coupling is a stable per-read property of the pair and not a novelty response. **Q2** second (a join's step in incumbent behavior: coupling or a constant field shift?).
**Fields:** stat mech (kinetic Ising, open systems / grand-canonical spin addition), sociophysics
**Literature:** model references in [`physics-models/02-nonequilibrium-ising/README.md`](../../physics-models/02-nonequilibrium-ising/README.md) (kinetic Ising, read-out-gated update). Glauber, *J. Math. Phys.* 4, 294 (1963)†. No notes file in `literature/` covers spin addition in kinetic models.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent (Claude Code agent excluded as recipient, as in the ledger); Population N(t) (active variant: agents with ≥ 30 receiving calls that PT day); Regime; Driving / external field; **Exposure (turn read-out)** via the context ledger; **Call cycle (hop)** and **Read-out jump J₁** (H50); **In-flight placebo (matched-lag)** and **Read-out jump (matched-lag) J₁\*** (H67); H18's **pending set** only through the dilution exponent. New named variants proposed for DEFINITIONS.md (not edited here), defined under Model: *join event (batch)*, *incumbent*, *newcomer read coupling J_N*, *constant-shift response δ*, *cross-fit in time (join)*.
**From:** HH363 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/`
**Data inputs (shared tables first):** DQ1 `call_windows`, `context_ledger_turns` (room, exogenous counts), `context_ledger_items` (reads with sender, age, mention flag); `chat_core` + `chat_mentions_clean` (in-flight placebo messages); `roster`, `calendar`, `period_units`. Comparison only (read as data): H67 `results/units.parquet` (J₁\* per read), H18's exponent (β = 0.66 ± 0.02, `interpretation/swarm-constants.json`).

## Source HH (verbatim from the HH list, including refinements)
- **HH363 · A batch join is a spin addition: do incumbents respond as the fitted couplings say? (NE27, NE33).** Three agents join at once. Incumbents' fields shift by the newcomers' couplings, which are unknown at the join but can be fitted on the first week.
  - *Prediction:* the incumbents' response in the first two days is predicted by first-week J (fitted later, then applied back) better than by a constant shift; H83 found newcomers fit in within a day, so the prediction is a fast step.
  - *Check:* cross-fitting in time: fit J on days 3–7, predict days 1–2.
  - *Kill:* the constant-shift model wins.
  - *Impostors:* N rises, which changes per-pair dilution (H18 N^−0.6); include it.
  - *Models:* 02 · *Builds on:* H83, H18, H85

## Question
When agents join, do the incumbents' per-call talk responses on the first two days follow the newcomers' read-out couplings fitted on days 3–7 (a response that tracks what each incumbent reads from the newcomers), or a constant shift of the incumbents' fields?

**Why it matters.** In a kinetic Ising model a new spin j adds J_ij s_j to every incumbent's field. If couplings are stable pair properties, J fitted later predicts the early response. If the early response is a uniform step (novelty, an operator announcement, a kickoff on the same day), it is a field, and a join cannot be forecast from couplings.

## Holdout geometry (stated before any data)
- **NE33** (2026-09-03/04, #51): days 1–2 are 09-03 and 09-04 (non-holdout); days 3–7 are 09-07 … 09-11, inside the locked #51 tail. The cross-fit needs days 3–7, so **NE33 is confirmation-only**. To keep its outcome blind, no H122 statistic touches incumbents' calls on 09-03/04 in exploration (H98 examined the joiners' *content* on those days: a different statistic and modality, disclosed).
- **Exploratory stand-in for NE33: NE32** (2026-07-09, #51): GPT-5.6 Sol/Terra/Luna join on 07-09 and Grok 4.5 on 07-10, a batch of 4 in regime III. H83 and H98 showed NE32 is *not* an isolation experiment (isolation lasted 1.5–2 h); as a join it is clean. Kimi K3 joins on 07-17 (active day 7), so days 3–7 are cut to 07-13 … 07-16.
- **NE27** (2025-08-18, #10, regime I): the pre-join goal #9 (08-13 … 08-15) is held out, so the pre-join window is #8 (08-06 … 08-12). Two confounds sit inside the design: goal #10 starts on day 1 (kickoff), and NE03 (chat context fetch limited) starts on 08-20, the first day of the fitting window; #11 starts on 08-25 (also inside days 3–7).

## Design: two layers (STANDARDS §4)
- **Replication (layer 1):** every eligible non-holdout join event (single or batch) is one replica of a spin addition. Eligible: a pre-join window of ≥ 2 non-holdout active days (same regime), both of days 1–2 non-holdout, ≥ 3 non-holdout fitting days among days 3–7 (cut before the next join event), and ≥ 3 incumbents. One README per goal period of day 1, role `replication`. The transition is the object (CLAUDE.md exception (c)).
- **Period-native tests (layer 2):** NE32 (regime III batch of 4; NE33's stand-in), NE27 (regime I batch of 3, kickoff and NE03 confounds; with a kickoff-matched placebo), and NE33 (confirmation-only; prediction frozen here, not run).

## Model
**From:** `physics-models/02-nonequilibrium-ising` (kinetic Ising on the call clock; read-out-gated update as in H40, H50, H67).

**Degrees of freedom.** Incumbent i's receiving call c (`ctx_mode != summary`) has talk outcome Y_ic ∈ {0, 1}. Its field is set by what the call newly reads (context ledger: agent items in i's room posted since i's previous receiving call).

**Join event (batch), named variant.** Joiners (roster `joined`, Claude Code excluded) whose first active days fall on the same or consecutive active days form one event. Day 1 = the earliest joiner's first active day. *Newcomers* = the event's joiners. *Incumbents* = agents with ≥ 30 receiving calls on ≥ 1 pre-join day and on ≥ 1 of days 1–2, excluding newcomers and agents who joined in the 7 active days before day 1 (their messages count as incumbent-class reads; they are not outcome agents).

**Windows.** PRE = up to 5 non-holdout active days before day 1 within the previous 10 active days (same regime); P12 = active days 1–2; F37 = active days 3–7 (cut at the next event's day 1).

**Per-call logistic model (kinetic Ising, linearized field).**
  logit P(Y_ic = 1) = a_{i,κ} + β_m R^m_ic + β_o R^o_ic + β_P P_ic + γ·E_ic + ρ Y_{i,c−1} + φ(k_ic) + [post-join terms]
- R^m_ic: incumbent-class peer messages read at c and posted within the call's latency d_c = clip(t_first − t_call, 1, 120) s before t_call; R^o_ic: older incumbent-class reads (H67's split). P_ic: incumbent-class messages posted in i's room in (t_c, t_c + d_c] (in-flight placebo, unreadable at c).
- E_ic: human items, nudges and nudges naming i read at c. a_{i,κ}: incumbent × call class (context mode × wake). φ(k): log(1 + k) and its square, k = calls since i's boot that day (the boot transient, H121).
- **M0 (no change):** all parameters fitted on PRE; newcomer reads ignored.
- **Dilution (H18; unfitted):** in every post-join model the read coefficients β_m, β_o, β_P are multiplied by (N̄_post/N̄_pre)^−0.66, N̄ = mean active population of the window's days. M0D = M0 with this factor.
- **MC (constant shift):** M0D + δ. One scalar δ fitted on F37 with M0D's linear predictor as offset.
- **MJ (spin addition, fitted couplings):** M0D + J_N R^N_ic, with R^N_ic = newcomer messages read at c (all ages). J_N fitted on F37 with M0D as offset. Variant MJn: separate J for newcomer reads that name i and for the rest (H67: address gating).
- **M_same (spin addition, incumbent couplings; unfitted):** M0D with newcomer reads counted as incumbent reads (J_N = the PRE read coefficients after dilution).
- **MJC:** M0D + δ + J_N R^N (both, F37).
- **MJ_pl (partition contrast, convergence):** M0D + J_P P^N_ic, with P^N_ic = newcomer messages posted in i's room in (t_c, t_c + d_c] (unreadable at c), fitted on F37.

**Cross-fit in time (named variant).** Every model is fitted on PRE and F37 only and scored on P12, the incumbents' calls on days 1–2. Score: mean log-loss per call. **Primary contrast:** ΔLL = LL(MC) − LL(MJ) (positive favours couplings), in nats per 1,000 calls, with a paired cluster bootstrap over (incumbent, PT hour) blocks of P12 (B = 2,000). Secondary contrasts: MJ vs MJ_pl (read vs in-flight), MJ vs M_same, M0D vs M0.

**Fast step (H83).** J_N fitted on P12 itself (same offset) against J_N from F37: the stability ratio J_N(P12)/J_N(F37). A coupling that is a pair property gives ratio ≈ 1; a novelty response gives > 2.

**Response trajectory.** Per P12 active hour, the incumbents' observed mean talk minus M0D's expected mean (the response r_h), against MC's and MJ's predicted r_h: share of variance of r_h explained (R²_h) by each.

**What each reading predicts.**
| World | J_N (F37) | P12: MJ vs MC | MJ vs MJ_pl | J_N(P12)/J_N(F37) |
| --- | --- | --- | --- | --- |
| Stable read-out coupling (HH) | > 0 | MJ wins | MJ wins | ≈ 1 |
| Novelty / greeting wave (coupling stronger on days 1–2) | > 0 | MJ wins only partly (under-predicts) | MJ wins | > 2 |
| Constant field shift (kickoff, announcement, N) | ≈ 0 | MC wins (kill) | tie | undefined |
| Convergence (newcomers and incumbents answer the same cues) | > 0 | MJ may win | tie or MJ_pl wins | any |
| No response | ≈ 0 | tie | tie | undefined |

## Data scheme (`scheme/`)
- **Inputs:** `call_windows` (turn_id, agent, pt_date, goal_no, regime, holdout, talk, ctx_mode, t_call, t_first, gap_kind), `context_ledger_turns` (turn_id, room, n_human, n_nudge, n_nudge_me), `context_ledger_items` (turn_id, sender, kind, age_s, ment), `chat_core` (agent messages: t, room, agent, message_id), `chat_mentions_clean` (mentions_roster), `roster`, `calendar`, `period_units`.
- **Transform (`scheme/build.py`):**
  1. join events from `roster` and the calendar's active days; windows PRE / P12 / F37; eligibility; holdout asserted twice (`calendar.holdout`, `common.holdout_mask`) on every day used, and NE33's P12 days are refused in exploration;
  2. incumbents' receiving calls in the event's windows, with k since boot, call class, Y and Y_{c−1};
  3. per call: R^m, R^o by sender class (incumbent-class / newcomer; named / unnamed), in-flight P by class, E counts;
  4. N̄ per window (active agents with ≥ 30 calls per day).
- **Output:** `data/processed/H122-batch-join-spin-addition/` with `events.parquet`, `calls/<event>.parquet` (codes only), `results/`, `synthetic/`, `_provenance.json`. Budget ≤ 50 MB.
- **Regimes covered:** I, II, III (non-holdout). Fits are within event.

## Observables
Per join event:
1. ΔLL (MC − MJ) with CI; ΔLL (MJ_pl − MJ); ΔLL (M_same − MJ); ΔLL (M0 − M0D); log-loss of every model on P12.
2. J_N (F37) with CI (logit per read; also converted to talk probability per read at the incumbents' mean rate, for comparison with H67's J₁\*); δ (F37); J_N (P12) and the stability ratio; MJn named / unnamed J.
3. R²_h of MC and MJ for the hourly response trajectory.
4. Counts: incumbents, P12 / F37 calls, newcomer reads per incumbent call in P12 and F37, N̄ per window.

## Null / baseline
- **No change (M0)** and **dilution only (M0D)**: what the incumbents would do with no newcomer effect.
- **Constant shift (MC):** the HH's rival and kill model.
- **In-flight model (MJ_pl):** the convergence partition (STANDARDS §3): messages the incumbent could not read, at matched lag.
- **Kickoff-matched placebo (NE27):** the incumbents' P12 shift δ_P12 (P12 fit with M0D offset) at non-holdout regime-I kickoffs without a join, PRE = the previous goal's last ≤ 5 days. NE27's δ_P12 is compared with that distribution.
- **Synthetic worlds** on the real event skeletons (below) size and power the ΔLL test.

## Impostors (STANDARDS §1)
| Impostor | How H122 removes it | Status |
| --- | --- | --- |
| Scheduler field | Per-call clock; incumbent × call-class baselines; a boot-transient term φ(k); the matched-lag in-flight placebo shares every field smooth on the scale of one call latency. | removed |
| Exogenous field (kickoff, goal, operator) | Human messages and nudges read at the call are covariates. The constant-shift model MC *is* the exogenous-field rival. NE27's kickoff on day 1 gets a kickoff-matched placebo. Goal changes inside a window are flagged per event. | partly |
| Shared model priors | Incumbent baselines per agent; J_N is pooled over newcomers, and family-specific couplings are not claimed. | partly |
| Contemporaneous convergence | MJ_pl: newcomer messages posted but unreadable at the call (matched lag). A coupling claim needs MJ to beat MJ_pl. | removed (by design) |
| N and per-pair dilution (HH) | Every post-join model carries the unfitted H18 factor (N̄_post/N̄_pre)^−0.66 on the read coefficients; M0 vs M0D tests whether it helps. | removed (unfitted adjustment) |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** constant field shift at the join (MC); newcomers couple like incumbents (M_same, unfitted); novelty response (coupling on days 1–2 larger than later); contemporaneous convergence (MJ_pl); no response (M0D).
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (frozen 2026-10-04, guarded, dry-run on NE32; **not run**) targets NE33 (J fitted on 09-07 … 09-11, scored on 09-03/04) and, as transfer, held-out join events whose windows are inside held-out periods or windows (e.g. Gemini 3.1 Pro 03-09 in NE30; Claude Fable 5 06-09, Claude Sonnet 5 06-30, DeepSeek-V4-Pro 07-02 / GLM-5.2 07-03 in NE21+NE23; Fine-Tuned Leader 06-01 in #45), where the design's windows exist.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Events, incumbents, reads from roster and ledger; PRE windows confounded with kickoffs (NE27, NE32) |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Update order audited; coupling stable days 1–2 vs 3–7 in 2/3 resolved events; logistic form untested |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Held-out-day scoring; MC beats M0D (CI > 0) in 4/10; MJ rarely adds |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | Cross-fitted J loses to a constant shift in 6/10 events |
| E interventional | predicts the change across a natural experiment | 1 | 10 joins as interventions; negative result |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | NE32 synthetic passed (power 1.0, size 0.04); NE27 underpowered |
| G ground truth | agrees with known structure | 1 | Address gating (H67) 8/10; fast step (H83) 2/3 |
| H comparative | beats the named rivals | 0 | The constant-shift rival wins |
| I transfer | holds in other same-mode periods, including the holdout | 0 | NE33 not run |

**Scorecard plan.** A from the event and incumbent definitions and the ledger read rule. B from the update-order audit (reads strictly before t_call, placebo strictly after) and the stability ratio. C from ΔLL against M0/M0D on held-out days. D from the cross-fit (J fitted on F37 predicts P12) and M_same (unfitted). E from NE32 and NE27 (each join is an intervention on the roster). F from the synthetic. G from H67 (J per read) and H83 (fast fit-in). H from MJ vs MC, MJ_pl and M_same. I stays 0 until NE33 runs.

## Prediction
*Written 2026-10-04 22:05 UTC, before any real-data statistic. Seen beforehand: table schemas; the roster and calendar (join dates, which days are held out); `period_units`; the published results of H67 (regime-III J₁\* ≈ 0.008 per read, named 0.079, unnamed 0.004; regime I ≈ 0), H18 (dilution exponent 0.66), H83 (newcomers' content gap closes by days 2–4), H85 and H98 (NE33 joiners start off-role). Not seen: any incumbent talk statistic around any join.*

**Synthetic validation (axis F), before real data.** Real event skeletons (NE32 and NE27: the real incumbents' calls and their real read, placebo and exogenous counts); outcomes simulated from M0 fitted on the real PRE window plus planted post-join terms; 100 replicates per world.
- **S1 power (coupling world):** J_N = 0.3 logit per newcomer read on P12 and F37, no shift: MJ beats MC (ΔLL CI > 0) in ≥ 80% of replicates in NE32. Power at J_N = 0.1 reported. [0.5]
- **S2 kill power (shift world):** δ = 0.4 logit on P12 and F37, J_N = 0: MC beats MJ (CI < 0) in ≥ 80%. [0.6]
- **S3 size (null world):** neither term: either model "wins" in ≤ 10% of replicates. [0.7]
- **S4 recovery:** J_N (F37) median within ±30% of 0.3 in the coupling world. [0.6]

**Real data (exploratory, non-holdout).**

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 | **The HH (NE32 native).** MJ beats MC on P12 (ΔLL CI > 0). | MC beats MJ (CI < 0): **kill** | 0.3 |
| P2 | **Regime I (NE27).** J_N (F37) CI includes 0; MC ≥ MJ; NE27's P12 shift lies inside the regime-I kickoff placebo range (the step is the kickoff's, not the join's). | J_N > 0 with CI excluding 0 and MJ beats MC | 0.5 |
| P3 | **Fast step (H83).** Where J_N is resolved in both windows, J_N(P12)/J_N(F37) lies within [0.5, 2]. | ratio > 2 (novelty) or < 0.5 | 0.35 |
| P4 | **Read vs in-flight.** Wherever MJ beats MC, MJ also beats MJ_pl (ΔLL > 0). | MJ_pl ≥ MJ in those events | 0.6 |
| P5 | **Dilution helps.** M0D beats M0 on P12 in ≥ 1/2 of eligible events. | M0 ≥ M0D in > 1/2 | 0.4 |
| P6 | **Newcomers couple like incumbents.** M_same (unfitted) is within the ΔLL CI of MJ in NE32. | MJ beats M_same (CI > 0) | 0.5 |
| P7 | **Replication.** MJ beats MC in ≥ 1/2 of eligible regime-III events; in regime I ΔLL CI includes 0 in ≥ 2/3. | MC wins in ≥ 1/2 of regime-III events | 0.25 |

**Amendment A1 (2026-10-04 23:12 UTC, after the synthetic validation, before any real-data statistic on P12 or F37).** Seen: the real PRE-window M0 fits of NE27 and NE32, which the simulator needs, and the synthetic runs (100 replicates × 5 worlds × 2 events; `data/processed/H122-batch-join-spin-addition/synthetic/`).
- **Estimator fix.** The first synthetic pass diverged on NE27: plain Newton on the 4-incumbent regime-I PRE window ran away under quasi-separation, with coefficients near 10⁶. The IRLS now uses step halving on the penalized log-likelihood. The covariate ridge rose from 10⁻⁴ to 0.1 (weak against 10⁴ calls), and one-parameter fits clip their Newton step at ±2. The model and data are unchanged.
- **NE32 (regime III): passed.** S1 power: MJ beats MC in 100% of replicates at J_N = 0.3 and 43% at J_N = 0.1. S2 kill power: MC beats MJ in 98% at δ = 0.2 and 100% at δ = 0.4. S3 size: either model "wins" in 4% under the null (MJ 1%, MC 3%). S4 recovery: median J_N 0.299 at a planted 0.3. MJ beats MJ_pl in 100% of coupling-world replicates.
- **NE27 (regime I): underpowered and anti-conservative for the kill.** S1 power is 64% at J_N = 0.3 and S2 kill power 47% at δ = 0.4. Under the null, MC "wins" in 12% of replicates (MJ in 1%). Only 4 incumbents and 2,063 P12 calls are available. In the shift world J_N absorbs part of δ (median 0.18 at δ = 0.4), because newcomer reads cluster in time. **Consequence (stated before real data):** an NE27 "MC wins" is weak evidence (size 0.12), and a CI that includes 0 is inconclusive. NE27's verdict is read with this calibration.
- The replication events have between 3 and 25 incumbents, so their power lies between NE27's and NE32's. Per-event power is not simulated; events with fewer than 5 incumbents are flagged as underpowered.

**Per-event verdict rule (replication and natives):** *supported* if MJ beats MC (ΔLL CI > 0) and MJ beats MJ_pl (point estimate > 0); *failed* if MC beats MJ (CI < 0); *mixed* if MJ beats MC but not MJ_pl, or if the ΔLL CI includes 0 (inconclusive; the synthetic power is quoted); *descriptive* if P12 has < 200 incumbent calls with a newcomer read.

**NE33 (confirmation-only, frozen here).** C1: MJ beats MC on 09-03/04 with J fitted on 09-07 … 09-11 (ΔLL CI > 0); C2: MJ beats MJ_pl; C3: J_N(P12)/J_N(F37) in [0.5, 2]. Kill: MC beats MJ. The exact script is `analysis/confirm.py` (frozen after the exploratory run; not run).

## Results by goal period
Per-event rule (card). **0 supported, 4 failed, 3 mixed, 3 descriptive** over 10 eligible non-holdout join events (4 regime I, 1 regime II, 5 regime III). The three "descriptive" events (single joiners with < 200 P12 calls reading a newcomer) still have decisive ΔLL CIs: two favour the constant shift, one favours couplings.

| Period | Role | Verdict | Key numbers (ΔLL in nats per 1,000 incumbent calls on days 1–2; J in logit per newcomer read) |
| --- | --- | --- | --- |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | mixed | J2025-05-22 (+2; I; 3 incumbents): ΔLL(MC−MJ) -1.74 [-15.17, +11.60] · J_N -0.08 [-0.27, +0.18] · δ -0.31 · newcomer reads in P12 419 |
| [NE27](goalperiod-subhypotheses/NE27/README.md) | native | mixed | NE27 (+3; I; 4 incumbents): ΔLL(MC−MJ) -0.52 [-2.07, +0.93] · J_N +0.10 [-0.03, +0.23] · δ +0.09 · newcomer reads in P12 471 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | J2025-10-22 (+1; I; 7 incumbents): ΔLL(MC−MJ) -21.73 [-33.01, -11.37] · J_N +0.25 [+0.15, +0.39] · δ +0.49 · newcomer reads in P12 1199 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | mixed | J2025-11-25 (+1; I; 7 incumbents): ΔLL(MC−MJ) +1.31 [-1.84, +5.47] · J_N -0.38 [-0.63, -0.01] · δ +0.15 · newcomer reads in P12 1071 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | J2026-03-16 (+1; II; 10 incumbents): ΔLL(MC−MJ) -7.89 [-11.17, -4.91] · J_N +0.33 [-0.19, +0.76] · δ -0.62 · newcomer reads in P12 68 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | J2026-04-27 (+1; III; 12 incumbents): ΔLL(MC−MJ) -2.47 [-3.64, -1.33] · J_N +0.21 [-0.36, +0.55] · δ -0.10 · newcomer reads in P12 22 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | J2026-05-20 (+1; III; 15 incumbents): ΔLL(MC−MJ) +14.04 [+11.32, +17.09] · J_N +0.54 [+0.09, +1.08] · δ +0.48 · newcomer reads in P12 83 |
| [NE32](goalperiod-subhypotheses/NE32/README.md) | native | failed | NE32 (+4; III; 18 incumbents): ΔLL(MC−MJ) -3.68 [-6.92, -0.25] · J_N -0.39 [-0.55, -0.28] · δ -0.75 · newcomer reads in P12 2666 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | failed | J2026-07-17 (+1; III; 21 incumbents): ΔLL(MC−MJ) -10.42 [-14.18, -7.31] · J_N +0.62 [+0.24, +0.87] · δ +0.34 · newcomer reads in P12 447 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | failed | J2026-07-24 (+1; III; 25 incumbents): ΔLL(MC−MJ) -0.85 [-1.71, -0.00] · J_N -0.05 [-0.17, +0.03] · δ -0.24 · newcomer reads in P12 2581 |
| [NE33](goalperiod-subhypotheses/NE33/README.md) | confirmatory | pending | not run (days 3–7 held out); `confirm.py` frozen |

## Results
*Exploratory round 1, 2026-10-04: 10 non-holdout join events; 165,000 incumbent calls on days 1–2 (P12), 338,000 on days 3–7 (F37), 384,000 in PRE windows. Numbers from `data/processed/H122-batch-join-spin-addition/results/{events,placebo}.parquet`, `summary.json`, `posthoc/posthoc.json`; synthetic in `synthetic/`. Code: `scheme/build.py`, `analysis/h122lib.py`, `synthetic.py`, `run.py`, `summarize.py`, `posthoc.py`, `confirm.py`.*

### Headline
**The HH fails: fitted newcomer couplings do not predict incumbents' first two days better than a constant field shift.** The constant shift wins (ΔLL CI < 0) in 6 of 10 joins, including the native stand-in NE32 (−3.7 [−6.9, −0.2] nats per 1,000 calls; the kill fires). Couplings win in 1 (Gemini 3.5 Flash, 05-20). Newcomers do couple: where J_N is resolved, read messages that *name* the incumbent carry more than unnamed ones (7/10 events), and the coupling on days 1–2 matches days 3–7 in 2 of 3 resolved events. But the per-read effect is small (median 0.009 talk probability per read in regime III), and it explains less of the incumbents' day-1–2 change than a uniform step does.

### Outcome vs prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| S1–S4 | NE32 synthetic: power, kill power, size, recovery | power 1.00 (J 0.3), kill power 1.00 (δ 0.4), size 0.04, J recovery 0.299/0.3 | passed (NE27 underpowered: 0.64 / 0.47, size 0.12) |
| P1 | NE32: MJ beats MC (**kill** if MC wins) | ΔLL −3.68 [−6.92, −0.25] | **failed: kill fires** (post hoc: −1.6 [−3.8, +0.7] without the #51 kickoff day in PRE) |
| P2 | NE27: J_N ≈ 0; MC ≥ MJ; step inside the kickoff placebo range | J_N +0.10 [−0.03, +0.23]; ΔLL −0.52 [−2.07, +0.93]; δ_P12 +0.21 inside [−0.93, +0.47] (12 kickoffs, median +0.10) | supported (underpowered) |
| P3 | J_N(P12)/J_N(F37) in [0.5, 2] where resolved | J2025-10-22 1.82, J2026-07-17 0.85, NE32 0.29 | mixed (2/3) |
| P4 | where MJ wins, MJ beats MJ_pl | J2026-05-20: +0.03 [−0.13, +0.20] | weakly supported (1 event) |
| P5 | M0D beats M0 in ≥ 1/2 of events | 4/10 | failed |
| P6 | NE32: M_same within the CI of MJ | −0.36 [−1.02, +0.32] | supported (both lose to MC) |
| P7 | MJ wins in ≥ 1/2 of regime-III events; regime-I CI includes 0 in ≥ 2/3 | III: MJ 1/5, MC 4/5; I: 3/4 include 0 | **failed** (regime-I part supported) |

### Findings
1. **A join shifts incumbents' talk uniformly, with an event-specific sign.** The F37 shift δ ranges from −0.75 (NE32) to +0.49 (J2025-10-22) in logit units. MC beats the no-change model M0D (CI > 0) in 4 of 10 events. The sign varies, so there is no universal "join effect": the step tracks what else happens in the window (kickoffs on day 1 or in PRE, goal changes inside F37).
2. **Couplings to newcomers exist and are address-gated.** Named newcomer reads raise the incumbent's talk logit more than unnamed reads in 8/10 events (NE32 +0.83 vs −0.42; J2026-07-17 +1.23 vs +0.61). This agrees with H67's address gating. Splitting J by naming (post hoc MJn) does not rescue the cross-fit: MC still wins or ties in 9/10 events.
3. **Fast step (H83).** In the two events where J_N is positive and resolved in both windows, the day-1–2 coupling equals the later one within ×2 (1.82 and 0.85). Newcomers couple as they will later from day 1. NE32 is resolved but negative in both windows (ratio 0.29).
4. **Dilution does not help prediction.** The unfitted H18 factor (N_post/N_pre)^−0.66 on incumbent read coefficients improves day-1–2 log-loss in 4/10 events. Its effect is ≤ 0.7 nats per 1,000 calls either way.
5. **Regime I (NE27 and three single joins):** no resolved coupling to newcomers, and ΔLL CIs include 0 in 3/4 events. NE27's day-1–2 step (δ_P12 +0.21) lies inside the range of 12 regime-I kickoffs without a join: the step there is the kickoff's.

### Post hoc (labelled; after the first real-data pass)
- **PH1, NE32 without the #51 kickoff day in PRE** (PRE = 07-07, 07-08): ΔLL(MC − MJ) = −1.64 [−3.77, +0.72], so MC no longer wins significantly. The NE32 kill rests partly on the kickoff field in PRE (the shift δ falls from −0.75 to −0.49). J_N stays negative (−0.40).
- **PH2, named/unnamed couplings vs the constant shift:** ΔLL(MC − MJn) < 0 with CI excluding 0 in 4/10 events, > 0 in 1/10 (J2026-05-20), and includes 0 in 5/10.

### Caveats
- Many joins coincide with kickoffs (NE27 day 1, J2026-03-16 and J2026-04-27 day 1; NE32 PRE). MC absorbs a kickoff field as well as any join field. The design cannot separate "the join is a field" from "a kickoff field sits in the window" without a join-free placebo in regime III.
- Single joins give few newcomer reads (22–447 P12 calls with a read); their verdicts rest on MC's fit, not on J.
- NE27's test is underpowered (power 0.47–0.64) and anti-conservative for the kill (size 0.12).
- The logistic model is linear in clipped read counts; a saturating response could favour MJ at high read counts.
- NE33, the HH's second named event, is confirmation-only; its outcome is still blind.

**Claim that stands:** Fitted read couplings to newcomers do not predict incumbents' per-call talk on the first two days after a join better than a constant field shift: the shift wins in 6 of 10 non-holdout joins (NE32 ΔLL −3.7 [−6.9, −0.2] nats per 1,000 calls), couplings win in 1. *Excluded:* the NE32 kill without the kickoff day in PRE (post hoc: −1.6 [−3.8, +0.7], not significant); NE27 (underpowered); the fast-step ratio (2/3 resolved events) and address gating of newcomer reads (secondary); dilution (no effect).

### Scorecard (round 1)
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | Events, incumbents and reads come from the roster and the ledger. PRE windows are confounded with kickoffs in NE27 and NE32. |
| B assumptions | 1 | Update order audited (reads strictly before t_call, placebo strictly after). The coupling is stable from days 1–2 to 3–7 in 2/3 resolved events. Linear-in-counts logistic form untested. |
| C adequacy | 1 | Scored on held-out days; MC beats M0D (CI > 0) in 4/10 events; MJ rarely adds. |
| D unfitted predictions | 0 | The cross-fit (J from days 3–7 applied to days 1–2) loses to a constant shift in 6/10 events. |
| E interventional | 1 | 10 joins used as interventions; a negative, informative result. |
| F identifiability | 1 | NE32 synthetic passed all four checks; NE27 underpowered and anti-conservative. |
| G ground truth | 1 | Address gating of newcomer reads agrees with H67; the fast step agrees with H83 in 2/3 resolved events. |
| H comparative | 0 | The rival (constant shift) beats the coupling model. |
| I transfer | 0 | NE33 not run. |

## Round 2 redirects
- **H122-R1. Join-free placebo in regime III.** Pseudo-joins at matched calendar positions (and kickoffs) with no roster change: if |δ| is as large there, the "join step" is calendar drift.
- **H122-R2. Kickoff-free PRE windows.** Re-run every event with PRE windows that exclude kickoff days (PH1 showed the NE32 kill depends on it); pre-register before running.
- **H122-R3. Saturating read response.** Fit J on log(1 + reads) or on named reads only, with the synthetic redone at that form.
- **H122-R4. NE33 on the holdout** with the frozen `confirm.py`.

## Notes
- 2026-10-04 22:05 UTC: round 1 started; card filled before any real-data statistic.
- 2026-10-04 23:12 UTC: Amendment A1 after the synthetic validation (IRLS step halving and ridge; NE27 power calibration).
- 2026-10-04 23:13 UTC: replication and natives run (~40 s); kickoff placebo built for 12 regime-I kickoffs.
- 2026-10-04 ~23:17 UTC: post hoc PH1, PH2 (labelled).
- Data: `data/processed/H122-batch-join-spin-addition/` (see `du` in the report).
- Proposed for `physics-models/DEFINITIONS.md` (not edited): *join event (batch)*, *incumbent*, *newcomer read coupling J_N*, *constant-shift response δ*, *cross-fit in time (join)*.
