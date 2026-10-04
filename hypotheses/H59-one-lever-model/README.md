# H59: One lever model for all operator inputs

**Status:** exploratory round 1 done (2026-10-04): **failed as posed.** Design, nulls and predictions P1–P7 were written before any outcome model was fitted to real data. Synthetic validation came first and amended the planted sizes and the reading of nudge cells (A1). Replication covered G51, G38 and G04; native tests NE43, G05 (#5) and NE38. `analysis/confirm.py` is written and dry-run on stand-ins; **not run**.
**Headline: one triple per class does not predict a held-out class.** Leave-one-class-out loses to class-specific fits in every period: transfer ratio T = S_H59/S_free is 0.47 for G51 nudges, 0.72 for mentions, 0.06–0.75 in G04, 0.12 for G38 nudges and 0–0.16 in G05.
- **What does hold is a narrower regularity:** "one lever at the read-out." On rows read 0–2 calls ago, the shared shape keeps 77–100% of the free fit's skill for G51 nudges and mentions and G04 human messages (post hoc). The class differences sit in the tails: the nudge's persistent after-effect looks like the nudger's selection of idle-prone agents.
- **Two exceptions break even the read-out version:**
  - G04 mentions act as an edge catalyst (work ↔ wait);
  - G38 nudges need their own field direction.
- **The read-out delay alone is not enough for message classes** (H59 beats R_delay for A and Hu). For nudges it is enough: the nudge amplitude equals the pooled one.
- **Natives:**
  - NE43 supported: the A and Hu triples are unchanged across the nudger stop, and the pre-fit predicts the post days with ratio 1.01;
  - G05 mixed: a read is the unit (dose saturates), but LOCO fails;
  - NE38 descriptive: consistent with the Hm lever.
**Fields:** sociophysics (operator levers), stat mech (kinetic / nonequilibrium Markov response, field vs. catalyst), dynamics (point-process kernels)
**Literature:** none of the notes in `literature/` covers multistate response kernels; references in `physics-models/02-nonequilibrium-ising/` ("Susceptibility, response and effective temperature") and `physics-models/09-hawkes/` (log-linear exogenous kernels). The field/catalyst split of a rate change is H39's (time-antisymmetric vs symmetric parts; Maes' frenesy, cited there).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Agent state (categorical: action class, three call-level states below); Driving / external field (nudges, human messages); Interaction (addressed) for @-mentions; Exposure (turn read-out) and H43's **receiving call**; H39's **field effect** and **catalytic effect** are used in a call-level variant, proposed below as **"field strength h (call-level)"**, **"catalytic strength κ (call-level)"** and **"read-out delay d"** (owner to add).
**From:** HH251 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/02-nonequilibrium-ising/`, `physics-models/09-hawkes/`
**Data inputs (shared tables first):** DQ1 context ledger (`context_ledger_items`, via H43's per-call table `data/processed/H43-kick-refractory-window/calls.parquet`, itself built from shared `call_windows`), leading-@ nudge targets (H30's `h30lib.leading_targets`, imported read-only; queued for `infra/shared/`), `roster`, `chat_core`. Round-1b numbers from H30, H35, H39, H43, H04 and H50 enter through `interpretation/lever-table.md` (predictions, ground-truth axis).

## Question
Can every operator input class (nudge, human message, @-mention, kickoff, operator message to one agent) be described by one triple (field strength, catalytic strength, read-out delay) in a single generalized linear response, so that a model fitted on three classes predicts the fourth?

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator on G51 (the only period where all four point-kick classes exist) and two other powered periods, G38 (regime III, nudges) and G04 (regime I, humans). Period README role: `replication`.
- **Period-native tests:** NE43 (G51 split at the nudger stop), #5 (G05, human dose) and NE38 (operator message to one agent, descriptive). Role: `native`.
- **Faithfulness lever:** HH251 targets axis I (transfer across lever classes) and D (a held-out class is an unfitted statistic). The scorecard says whether it moved them.
- **Compute:** ≤ 2 threads, no pools; analysis kept to G51, G38, G04 (+ G05 native).

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (kinetic response: field vs. rate changes, detailed balance) and `physics-models/09-hawkes/` (exogenous events with a response kernel; here log-linear and on the call clock).

**H59 variant: a three-state call-level Markov GLM with one lever per input class.** Each model call of an agent is in one state, s ∈ {I idle, W work, T talk}. For the transition from call j−1 (state i) to call j (state j′ ≠ i), the log-odds against staying,

  η_{ij′}(j) = α_{ij′}·x_j + Σ_c Σ_ℓ D_{cℓ}(j) β_{ij′}(c, ℓ),

has a baseline α·x (agent, day, run length, Markov-2 state, time of day, unaddressed chatter and bookends at this call) and a kick term: D_{cℓ}(j) = 1 if a class-c kick was read at the call ℓ calls before (ℓ = 0 is the **receiving call**, the first call whose context holds the message; DQ1 ledger). A rate change splits into a symmetric part (catalyst, "frenesy") and an antisymmetric part (field, tilt), as in H39.

**One-lever constraint (H59):**

  β_{ij′}(c, ℓ) = K_ℓ · [κ_c + h_c (u_{j′} − u_i)/2],  u = (u_I, u_W, u_T) = (0, cos θ, sin θ),  K_0 = 1.

- **κ_c (catalytic strength):** a uniform symmetric speed-up of every transition, in log-odds per call. It raises traffic at fixed occupancy.
- **h_c (field strength):** a tilt along one **universal field direction** u (θ = 0: toward work; θ = 90°: toward talk). It shifts occupancy.
- **d_c (read-out delay):** the time from posting to the receiving call (median ledger age at read). It sets *when* the response happens in wall-clock time; in the call-aligned GLM it enters only through which call is the receiving call (read-out gating).
- **Shared across classes:** the kernel shape K_ℓ over lag bins ℓ ∈ {0, 1, 2, 3–5, 6–10, 11–30} calls, the direction θ, the baseline. **Class-specific:** only (κ_c, h_c, d_c).
- Overlapping kicks add in log-odds. Calls are the clock (H40: compare per call, not per hour).

**What it predicts.** Once θ and K are fixed by any three classes, a fourth class's whole response (six transition types × six lags = 36 log-odds shifts) follows from two numbers, κ_c and h_c, and its wall-clock timing from d_c.

**Rivals.**
- **R_free (class-specific free response):** each class has its own 36 β's (ridge, prior SD 1). The one-lever model is a 2-parameter restriction of it.
- **R_delay (read-out delay alone):** all classes share one (κ, h); classes differ only in when they are read. Fitted on the other classes, it has *zero* parameters for the held-out class: the purest leave-one-class-out prediction.
- **R_dir (class-specific direction):** (κ_c, h_c, θ_c) per class, shared kernel. Diagnoses whether a failure is about direction.
- **R0 (inert):** no kick term; baseline only.

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H59-one-lever-model/` (non-holdout rows; `holdout_mask` re-checked):
- **Calls:** H43's `calls.parquet` (one row per non-summary model call from shared `call_windows`; holdout already excluded). States: **T** = the call posts chat (talk flag); **I** = kind pause or wait and not talking; **W** = any other call.
- **Transitions:** consecutive calls of the same agent on the same PT day, gap ≤ 60 min (longer gaps are village-off or outages). Covariates known before the call's decision: previous state, state two calls back, run length of the previous state (bins 1, 2–4, 5–14, 15–49, 50+ calls), time since the agent's first call that day (< 1, 1–3, 3–6, ≥ 6 h), count of unaddressed agent messages and bookends read at this call (nuisance).
- **Kicks at the receiving call** (`context_ledger_items`, omitted items dropped):
  - **N** nudge whose *leading @* is the recipient (H35 rule; Known issue "a nudge's target is its leading @");
  - **Hu** human message not naming the recipient (broadcast);
  - **Hm** human message naming the recipient (≈ operator message to one agent; in #51 humans are the operators);
  - **A** agent message naming the recipient (@-mention).
  - Lag bitmasks per class: bit 0 = lag −1 (the call just before the receiving call; a **pre-read term** that absorbs the sender's selection on the recipient's current state, e.g. the nudger firing at idle agents), bits 1–6 = lag bins 0, 1, 2, 3–5, 6–10, 11–30.
- **Read-out delays:** `readout.parquet`, one row per (kick item, recipient) with its age at the receiving call.
- **Kickoff** is not a class here: one kickoff per period reaches ≤ 32 receiving calls, which cannot fit or test a call-level response inside one period (H39 treats kickoffs as steps across periods, NE34). Reported as a limit, not tested.
- **Output:** `transitions.parquet`, `readout.parquet`, per-period `G<NN>/results.json`, `native/`, `synthetic/`, `_provenance.json`. Budget ≤ 100 MB.
- **Regimes covered:** III (G51 non-holdout days 2026-07-06 → 09-04; G38 2026-04-02 → 04-24), I (G04 2025-05-15 → 06-18; G05 native).

Structural counts (receiving calls with a transition; seen before writing the predictions):

| Period | N | Hu | Hm | A | transitions | from I / W / T |
| --- | --- | --- | --- | --- | --- | --- |
| G51 | 720 | 1,569 | 92 | 31,873 | 899k | 25k / 832k / 42k |
| G38 | 109 | 85 | 8 | 2,437 | 114k | – / 108k / 4.6k |
| G04 | 0 | 4,627 | 324 | 2,752 | 31k | 0.6k / 24k / 6.5k |
| G05 | 0 | 2,134 | 143 | 457 | 6.2k | 0.05k / 5.0k / 1.1k |

Read-out delay (median age at read): G51 N 107 s, Hu 51 s, Hm 20 s, A 21 s; G04 11–12 s for every class.

## Observables
Per goal period, per class c with ≥ 50 receiving calls (**powered**):
- **The triple** (κ̂_c, ĥ_c, d̂_c), with θ̂ and K̂ shared, from the one-lever model fitted on all classes (offset = baseline). Day-block bootstrap (200 draws of days, baseline held fixed) for 95% percentile CIs.
- **Leave-one-class-out skill.** Baseline fitted once per period with free kick dummies for every class (so kick rows do not bias it), giving an offset per row. For each held-out class c:
  1. fit the one-lever model on the other classes (all days) → θ, K, their triples, and a pooled (κ, h) for R_delay;
  2. on c's exposed rows (any lag 0–30 bit set), 5 interleaved day folds: fit c's parameters on 4 folds, score the log-likelihood on the fifth. M0: none. R_delay: none (pooled amplitude). **H59:** (κ_c, h_c). R_dir: (κ_c, h_c, θ_c). R_free: 36 β's (ridge λ = 1).
  3. **Skill** S_m = LL_m − LL_0 on held-out days (nats, summed over folds); per-day contributions are kept for a day-block bootstrap of differences.
  4. **Transfer ratio** T_c = S_H59 / S_free (reported when S_free > 0).
- **Shared kernel** K̂_ℓ (lag profile) and **pre-read term** (lag −1 β's, R_free fit; sender selection, descriptive).
- **Inbox decay check:** a multiplier on the lag-0 amplitude for stale reads (age above the class's median) vs fresh ones, fitted with θ, K fixed.
- **H39-style translation (descriptive):** the implied idle-escape log-ratio κ + h·(u_W,T)/2 and the occupancy tilt, for comparison with the lever table.

## Null / baseline
- **N1 synthetic (axis F):** the identical pipeline on simulated outcomes. The real design is kept (from-states, covariates, kick exposures at G51 and G38 counts); outcomes are drawn from a planted baseline (marginal transition rates, agent and day heterogeneity SD 0.5 and 0.3, run-length aging) plus planted kick terms. Worlds: **one-lever** (shared θ = 60°, K = 1, 0.3, 0.1, 0.05, 0, 0; triples N (0.4, 1.0), Hu (0, 0.15), Hm (0.1, 0.8), A (0.1, 1.0)); **direction-violated** (N's field toward work, θ_N = 0°, the others toward talk, θ = 90°); **delay-only** (every class (0.2, 0.8)); **null** (no kick terms). Because the GLM conditions on the from-state, drawing each transition given the real from-state is an exact parametric bootstrap of the conditional model.
- **N2 day-block bootstrap** (200 draws) for triples and for skill differences.
- **N3 out-of-sample scoring** on held-out days protects R_free and R_dir from overfitting wins; R_delay and M0 need no fit on the held-out class.
- **Rivals:** R_free, R_delay, R_dir, R0 (Model section).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness". Scored after round 1 (2026-10-04).
**Rival models:** R_free (class-specific response), R_delay (read-out delay alone), R_dir (class-specific direction), R0 (inert).
**Locked holdout used for confirmation:** none. `analysis/confirm.py` (C1–C5 on the #51 tail) is written and dry-run on stand-ins; **not run**.
**Faithfulness lever (HH251 aimed at I and D):** I did not move (0: the triple does not transfer across classes). D reached 1, through the read-out-only transfer and the dose signature.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | States come from `call_windows` kinds and talk flags; kicks are timed at the DQ1 receiving call; nudge targets use the leading @. Assumptions are listed. Not invariant across regimes: "idle" is a pause in regime III and a wait in regime I (646 idle transitions in G04), and a regime-I mention acts on the work ↔ wait edge |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Markov-2 state plus run-length aging in the baseline; agent and day fixed effects. The baseline is fitted once and held fixed in the bootstraps. A pre-read term absorbs sender selection on the current state. Stationarity of the triples holds across NE43; within-period stationarity otherwise untested; sequential ignorability is untestable |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | On held-out days (5 day folds) the one-lever model beats the inert model for every informative class and the read-out-delay rival for every message class (G51 A [620, 1,305] nats; Hu [12, 130]; G04 Hu, A). It loses to class-specific fits. Day effects and the agent's own aging are in the baseline; no family-field null |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The held-out class is the unfitted statistic: it fails over the full window and transfers at the read-out (post hoc, G51 0.77–0.80, G04 humans 0.84–1.0). The G05 dose saturates as predicted (≥ 3 vs 1 message: −0.02 [−1.2, 1.2]). Inbox decay is absent for nudges and mentions (G51) but present for broadcast humans and G38 mentions |
| E interventional | predicts the change across a natural experiment | 1 | NE43: fitted before the nudger stop, the model predicts the post days (ratio 1.01 [1.005, 1.025]), and the A/Hu triples are unchanged. This is an invariance prediction, not a predicted change in sign or size |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | κ, h and θ are recovered at G51 counts (h within 12%, θ within 1°). A direction violation is not detectable when the deviant class is read only at idle calls (0/2 at G51; 2/2 at G38). The delay rival is separated in 50–67% of cells; null coverage is 83–88% (target 90%) |
| G ground truth | agrees with known structure | 1 | Signs match the lever table: nudges both (κ 0.33, h 3.97); naming carries the larger field (h_A 3.77, h_Hm 4.39 > h_Hu 1.77). Read-out delays reproduce RE-V1/H43 (nudge 107 s). NE38's operator message raises talk as the Hm lever predicts (n = 1). The broadcast-human field is larger than predicted (h 1.77 vs < 0.3) |
| H comparative | beats the named rivals | 1 | H59 beats R0 everywhere and R_delay for message classes. It ties R_delay for nudges and loses to R_free in every period; R_dir wins for G38 nudges |
| I transfer | holds in other same-mode periods, including the holdout | 0 | The claim (one triple per class, shared shape) fails in G51, G38, G04 and G05. Only the read-out regularity recurs (G51; G04 humans). Holdout not used |

## Prediction
*Written 2026-10-04 (UTC), before fitting any outcome model to real data and before the synthetic validation.* Seen: the lever table, the round-1b cards it cites, and the structural counts above.

- **P1 (the claim, leave-one-class-out; G51).** For every powered class, the one-lever model with θ and K from the other classes and only (κ_c, h_c) fitted on c predicts c's held-out-day transitions nearly as well as a class-specific free fit: **T_c ≥ 0.8**, and S_H59 > 0 with the day-bootstrap 95% CI excluding 0. **Counts against:** T_c < 0.5 with S_free − S_H59 > 0 (CI excluding 0) for any powered class: that class needs its own response shape, and one lever does not describe it.
  - *Expectation stated in advance:* the message classes (A, Hm, Hu) transfer among themselves; **nudges are the likeliest failure**, because a nudge acts on idle agents as an escape-only kick (H39: half field, half catalyst on the idle edges only), which a uniform catalyst plus a talk-leaning field cannot represent.
- **P2 (rival R_delay).** Read-out delay alone does not explain the class differences: S_H59 − S_delay > 0 (CI excluding 0) for nudges and for at least one message class. Counts for R_delay: S_delay ≥ S_H59 − (its CI half-width) for every class.
- **P3 (read-out gating, shared kernel).** The response is concentrated at the receiving call: K̂_ℓ ≤ 0.3 for every lag bin ℓ ≥ 1. Counts against: a lag bin ≥ 1 with K̂ > 0.5 (a delayed response the read-out does not explain).
- **P4 (no inbox decay).** The lag-0 amplitude does not depend on how long the message waited: stale/fresh multiplier in [0.7, 1.3] with its CI overlapping 1. Counts against: multiplier < 0.7 with CI excluding 1 (messages go stale in the inbox, so d is not just timing).
- **P5 (lever-table signs, axis G).** N: κ > 0 and h > 0 (field away from idle). A and Hm: h > 0, with the shared direction θ̂ > 45° (toward talk), and h_A > h_Hu, h_Hm > h_Hu (naming is the content lever). Hu: |κ| < 0.2 and |h| < 0.3 in regime III (broadcast human messages barely move behavior; H39, H30).
- **P6 (replication: G38, G04).** P1 in each with its powered classes (G38: N, Hu, A; G04: Hu, Hm, A). Templated per-period verdict: supported if every powered class has T ≥ 0.8 and S_H59 CI > 0; failed if any powered class has T < 0.5 with S_free − S_H59 CI > 0; else mixed; descriptive if S_free CI includes 0 for every class.
- **P7 (synthetic, axis F).** At G51 counts: (a) κ, h of classes with ≥ 300 receiving calls recovered with median relative error ≤ 25% and θ within 10°; (b) one-lever world: T ≥ 0.8 in ≥ 90% of powered class × replicate cells; (c) direction-violated world: the violating class (N) gets T < 0.5 in ≥ 80% of replicates; (d) delay-only world: S_delay − S_H59 CI includes 0 in ≥ 80% of cells; (e) null world: S_H59 CI includes 0 in ≥ 90% of cells.

**What would count against H59 as a whole:** any powered class failing P1 in G51 with its failure reproduced in G38 or G04 (the triple is not enough), or R_delay matching H59 everywhere (the triple collapses to one number, d).

### Amendment A1 (2026-10-04, after the synthetic validation, before any real-data outcome model)
- **Planted sizes.** The card's planted amplitudes (h ≈ 1, giving ≈ 0.3 log-odds on W→T) carried only ~3 nats of information at G38 and are far below the observed mention response (reply lnHR ≈ 1.4, H43). Re-planted: θ = 75°; N (0.8, 2.0), Hu (0, 0.3), Hm (0.3, 2.0), A (0.2, 2.5); delay world (0.3, 2.0) for all.
- **Ridge 0.1** on lever parameters (prior SD ≈ 3): with 1e-3, an 85-read class ran to h = −9.5.
- **P7c rephrased:** a direction violation is "detected" if *any* powered class fails LOCO. One class's failure shows up wherever the shared direction is borrowed from a class with a different one.
- **Synthetic outcome** (`synthetic/summary.json`; 8 G51-scale and 8 G38-scale replicates). (a) recovery: h median relative error 12% (G51) / 11% (G38), θ error 1° / 3°; (b) one-lever world: every informative cell passes at G51 (N T = 1.22, 1.23; A 0.91, 0.97), 2 of 4 at G38; (c) **direction violation detected 0/2 at G51, 2/2 at G38**; (d) delay world: lever − delay CI includes 0 in 67% / 50% (target 80%); (e) null: S_H59 CI includes 0 in 88% / 83% (target 90%).
- **What (c) means:** nudges are read almost only at idle calls (557 of 720 G51 receiving calls). There, (κ_N, h_N) fit the two idle exit rates (I→W, I→T) whatever θ is, so **a nudge "pass" does not test the shared direction.** LOCO tests the direction only for classes read in several from-states: A everywhere, and Hu/Hm in regime I. Hm (92 reads) and Hu at planted h = 0.3 are uninformative at G51 even when real. P1's reading is amended accordingly: a G51 nudge pass is weak evidence; the informative cells are A (G51, G38) and the human classes in G04.

### Native predictions (dated in each folder before running)
- **NE43 (G51, nudger stop 2026-08-21):** the A and Hu triples are the same before and after (Δκ, Δh 95% CIs include 0), and a one-lever model fitted on the pre days predicts the post days' kicked transitions with ≥ 80% of a post refit's skill. The lever is a property of the input class, not of the drive context.
- **G05 (#5, human dose):** the per-read lever saturates. Lag-0 amplitude for reads carrying ≥ 3 human messages ≤ 2× that of a single message (the linear-dose rival predicts ≥ 3×); and P1 among Hu, Hm, A.
- **NE38 (G51, 2026-07-29, operator reassigns Claude Opus 5's role):** descriptive. The receiving-call transition of the named agent is scored against the one-lever Hm prediction (fitted with that message's days left out); n = 1.

## Results by goal period
Replication verdicts are templated (P6): supported if every informative class has T ≥ 0.8 with S_H59 CI > 0; failed if any has T < 0.5 with S_free − S_H59 CI > 0. Native folders carry their own predictions.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | failed | N T 0.47 (free − H59 [136, 325]); A T 0.72; Hu, Hm uninformative; θ 72.7°; read-out-only T: N 0.80, A 0.77 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | failed | N T 0.12, own direction recovers all skill; A T 0.41 (uninformative); K₁ 0.65 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | A T 0.06 (edge catalyst W ↔ wait); Hu 0.75, Hm 0.59; read-out-only Hu 0.84, Hm 1.0 |
| [G05](goalperiod-subhypotheses/G05/README.md) | native | mixed | dose saturates (≥ 3 vs 1 msg: −0.02); LOCO Hu T 0.16, A ≈ 0 |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | supported | A Δh −0.40 [−0.87, 0.82], Δκ +0.03 [−0.06, 0.16]; pre → post transfer 1.01 [1.005, 1.025] |
| [NE38](goalperiod-subhypotheses/NE38/README.md) | native | descriptive | Opus 5's receiving call: P(talk) 0.06 → 0.14 under the Hm lever; +0.87 nats |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only)
- **Scripts:**
  - `scheme/build.py`: transitions and read-out delays;
  - `analysis/h59lib.py`: the estimator (baseline GLM, lever family, LOCO, bootstrap);
  - `analysis/synthetic.py` and `synthetic_summary.py`: synthetic validation;
  - `analysis/run_period.py`: replication;
  - `analysis/loco_split.py`: post hoc read-out vs tail;
  - `analysis/natives.py`: NE43, G05, NE38;
  - `analysis/write_outputs.py`: estimates and figures;
  - `analysis/confirm.py`: frozen, not run.
- **Numbers:** `data/processed/H59-one-lever-model/` (`G51/`, `G38/`, `G04/` results and loco_split; `native/`; `synthetic/`; `confirm_dryrun/`; 11 MB). 70 rows in the shared `per_period_estimates`: κ, h, θ, d, T and H59 − delay per class and period, plus the NE43 transfer.
- **Figures:**
  - `figures/summary_obs.pdf`: LOCO skill relative to the free fit, and the read-out vs tail split;
  - `figures/synthetic_validation.pdf`.

### The triples (one-lever fit on all classes, G51)
| Class | κ catalytic (log-odds/call) | h field (along θ = 72.7°) | d read-out (median) | Implied at the receiving call |
| --- | --- | --- | --- | --- |
| nudge | 0.33 [0.01, 0.55] | 3.97 [2.99, 5.05] | 107 s | I→T +2.2, I→W +0.9, W→T +1.6 |
| @-mention | 0.14 [0.11, 0.18] | 3.77 [3.47, 4.05] | 21 s | I→T +1.9, W→T +1.4, T→I −1.7 |
| human, named | 0.60 [−0.11, 1.31] | 4.39 [2.16, 5.46] | 20 s | – (92 reads) |
| human, broadcast | −0.12 [−0.39, 0.06] | 1.77 [0.82, 2.54] | 51 s | I→T +0.7, W→T +0.5 |

Kernel over lag bins 0 / 1 / 2 / 3–5 / 6–10 / 11–30 calls: 1, 0.44, 0.17, 0.10, 0.06, 0.09. In the call-level state space every class is mostly a field toward talk at the read-out, with small catalysis.

### Why one triple is not enough
- **Tails, not read-outs (G51).** At the receiving call, nudges and mentions have nearly the same free response (I→T +2.9 for both). The shared shape keeps 80% / 77% of the free fit's skill on rows read 0–2 calls ago and ~0 on rows read 3–30 calls ago. The nudge's tail is a persistent tilt (W→I and W→T up, T→W down for 30 calls). With the nudger's pre-read term (W→I +3.3: it fires at agents that just went idle), this reads as selection of idle-prone agents rather than a lever effect; H43 and H35 reached similar conclusions about re-fires.
- **Edge-specific catalysis (G04 mentions).** A regime-I mention speeds up work ↔ wait in both directions (W→I +1.85, I→W +0.72). A uniform κ cannot express this, and neither can a talk field.
- **Direction (G38 nudges).** A class-specific θ recovers all the free fit's skill. A single θ is set by whichever class dominates the data.
- **Read-out delay alone.** Rejected for message classes (their amplitudes differ from the pooled one), not for nudges. Nudges add nothing beyond "a kick read now" with the pooled amplitude.

### Outcome vs prediction
| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 LOCO, G51: T ≥ 0.8 for every powered class | N 0.47 (fail, as expected in advance, but the loss is in the tail, not at the read-out); A 0.72; Hu, Hm uninformative | **failed** |
| P2 R_delay loses for nudges and ≥ 1 message class | message classes yes (A, Hu in G51; Hu, A in G04); nudges no (tie) | **mixed** |
| P3 shared kernel K_ℓ ≤ 0.3 for ℓ ≥ 1 | G51 K₁ 0.44 (≤ 0.5, not counted against); G38 0.65 (against); G04 −0.32 (rebound) | **mixed** |
| P4 no inbox decay (stale/fresh in [0.7, 1.3]) | G51 N 1.09, A 1.03 ✓; G51 Hu 0.57 ✗; G38 A 0.52 ✗; G04 Hu 1.25 ✓ | **mixed** |
| P5 lever-table signs | N κ, h > 0 ✓; θ 72.7° > 45° ✓; h_A, h_Hm > h_Hu ✓; Hu \|κ\| < 0.2 ✓ but h 1.77 ≫ 0.3 ✗ | **mostly supported** |
| P6 replication G38, G04 | both failed | **failed** |
| P7 synthetic | (a) ✓; (b) ✓ at G51; (c) 0/2 at G51, 2/2 at G38; (d) 50–67%; (e) 83–88% | **mixed** |
| NE43 invariance + transfer | Δ CIs include 0; ratio 1.01 | **supported** |
| G05 dose saturates + LOCO | dose −0.02 ✓; LOCO fails | **mixed** |
| NE38 descriptive | +0.87 nats for the Hm lever | **descriptive** |

### Caveats
- **Post hoc pieces:** the read-out vs tail split (`loco_split.py`) was added after seeing the replication results, so "one lever at the read-out" is an exploratory finding, frozen for the holdout as C1.
- **The state space is coarse.** Content fields (H39 O6, H30 χ_con) are not in it, and the lever table's "naming is the content lever" is not tested here. "Field" here means a tilt toward talk calls.
- **Offsets.** The baseline is fitted once with free kick dummies, on all days, so day effects of held-out days are estimated from mostly unkicked rows (mild leakage into LOCO scoring). Bootstraps hold it fixed (CIs are conditional on the baseline).
- **Power.** Hm (92 reads in G51, 8 in G38) and G38's Hu are uninformative; G38 is marginal even in the synthetic. Kickoffs (≤ 32 reads per period) are not testable at call level.
- **Sender selection.** Nudges and mentions arrive at agents in particular states. The pre-read term and past-only baseline handle the current state, not the nudger's trigger (H43-R2).
- **Multiplicity:** 3 replication periods × 2–4 classes × 4 models; the inference rests on G51 (N, A) and G04 (Hu, A).

## Confirmatory plan (frozen 2026-10-04; `analysis/confirm.py`, not run)
Frozen from the G51 head: θ = 72.7°, K = (1, 0.44, 0.17, 0.10, 0.06, 0.09), triples A (0.141, 3.774), Hu (−0.125, 1.770), Hm (0.595, 4.394). Target: **the #51 tail** (2026-09-07 → 09-21; classes A, Hu, Hm).
- **C1** read-out transfer for A: θ, K frozen; refitting (κ_A, h_A) keeps ≥ 0.7 of the free fit's early-row skill.
- **C2** the frozen head model predicts the tail with ≥ 0.8 of a tail CV refit.
- **C3** h_A ∈ [2.5, 5.0], κ_A ∈ [−0.05, 0.35].
- **C4** A stale/fresh ∈ [0.8, 1.25].
- **C5** full-window A transfer T < 0.8 (tails are class-specific).

"One lever at the read-out" is confirmed if C1–C3 pass.
- **Dry run on non-holdout stand-ins** (2026-08-24 → 09-06, in-sample): C1 0.91 ✓, C2 1.01 ✓, C3 (0.05, 2.83) ✓, C4 0.90 ✓, C5 T 0.87 ✗ (the stand-in has no nudges). Output: `data/processed/H59-one-lever-model/confirm_dryrun/confirm_results.json`.
- **Guards:** `--confirm`, `H59_CONFIRM=1`, `--disclosed`, and `holdout_ledger.check("H59", "#51-tail", …)`.
- **Reuse:**
  - The #51 tail has no executed runs, but 25 planned uses, including H39 (behavior states) and H30 (kick response), which are the closest statistics. Whoever runs first makes the others second users; disclose in those cards and in LOG.md before running.
  - #45 (nudges) is **not** used: H04's executed run there is in the same kick-response family, so policy item 2 blocks it.

## Round 2 redirects
**What the direction is really after:** a compact, portable description of what an operator input does. Round 1 says the portable part is the read-out response, and what differs between classes is their tails and, in some regimes, which edge they act on.
- **H59-R1. Run `confirm.py`** on the #51 tail after commit and disclosure.
- **H59-R2. Separate tail from selection.** Re-fit the nudge tail with the nudger's trigger state (H35 classes, idle age at firing) and within-agent first-vs-re-fire contrasts. If the tail vanishes, the one lever holds for nudges too.
- **H59-R3. Two-component lever.** Add an edge-specific catalyst (work ↔ idle) and a second field direction, and re-test LOCO in G04 and G38 (a "two-lever" model with 4 numbers per class).
- **H59-R4. Content layer.** Put H39's drift-toward-message (O6) on the same receiving-call clock so that "field" covers content as well as talk.
- **H59-R5. Kickoffs** across regime-III periods with partial pooling (exception d), as the fifth class.

## Notes

- 2026-10-04: round 1 started. No other hypothesis's code is modified; H30's `leading_targets` is imported read-only (text read in memory only, never written).
- 2026-10-04: the API stream stalled mid-round; work on disk was intact and the round resumed from the library step. Synthetic results and amendment A1 precede every real-data outcome fit.
- 2026-10-04: holdout: all loaders use H43's non-holdout calls (holdout_mask re-asserted in `scheme/build.py`). No held-out row was read; `confirm.py` was only dry-run on non-holdout stand-ins and guard-checked.
- 2026-10-04: NE44 (pause default 12 h → 5 min, 2026-06-11) is not used as a native: its date lies inside the locked NE21+NE23 window, so a clean before/after needs held-out days.
