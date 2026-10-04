# H113: Read-out channel capacity: information per call grows as k^(1−β) ≈ k^0.34

**Status:** exploratory round 1 done (2026-10-04, non-holdout only). **Failed by the pre-set kill, but the read-out channel has a measured, intermediate capacity.** Content taken up from a batch of k peer messages grows as k^(a_U): on #51 timer-wake batches, where k is set by others (H18's identified design D2), a_U = 0.31 [0.25, 0.37] (bge) and 0.29 [0.24, 0.34] (gte). On talk calls pooled over the 6–7 periods identified against a topic field, a_U = 0.23 [0.16, 0.31] / 0.22 [0.14, 0.30], which excludes HH345's 0.34 (the kill) and, everywhere, H18's corrected 0.50. Neither a hard one-message capacity (a_U = 0) nor linear superposition (a_U = 1) fits any period. The exponent is the same in both embedding models (34/34 within 0.2) and does not move across the NE42 room merge while k rises ×1.5. Caveat: a topic field alone yields b̂ ≈ 0.8 on synthetic skeletons, so only periods with a positive read − in-flight contrast are scored. `analysis/confirm.py` is frozen and dry-run, not run. Card written 2026-10-04 21:33 UTC before any uptake statistic; A1 (pre-data), Note N1 (coordinator correction of H18's exponent, pre-data). Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH345.
**Fields:** information theory (channel capacity, Gaussian channels), stat mech (linear response at the read-out), sociophysics (attention budgets)
**Literature:** [Kolchinsky & Wolpert 2018, semantic information](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (κ = ΔV/I, information per channel); [Barrett 2015](../../literature/barrett-2015-synergy-redundancy-gaussian-systems.md) (Gaussian information of a linear channel); [Lizier 2008](../../literature/lizier-2008-framework-local-information-dynamics.md) (transfer into a destination). Classical background named, not filed (†): Shannon (1948)† (Gaussian channel C = ½ log(1 + SNR)); Cover & Thomas, ch. 9–10† (parallel Gaussian channels); Kahneman, *Attention and Effort* (1973)† (capacity models of attention).
**Definitions used** (`physics-models/DEFINITIONS.md`): *Pending set (talk-call backlog, ledger k)* and *Dilution exponent (population, ledger)* (H18, RE-V1; shared `pending_sets.py`); *Exposure (ledger receiving call)* (RE-V1); *Influence coupling (content pull)* (H29) in an orthogonalized variant; *In-flight placebo (matched-lag)* (H67) and *Unread (in-flight) exposure placebo* (RE-D1); *Identified κ row* (H87 A1) as the rule for ordering information values; *Channel information I_c* (H70) for the discrete check; *Regime*. New named variants proposed here (not edited into DEFINITIONS.md; see the report): **per-message uptake slope γ(k) (H113)**, **total uptake U(k) and capacity exponent a_U (H113)**, **read-out information per call I(k) and exponent a_I (H113)**, **batch redundancy exponent r (H113)**, defined under Model and Observables.
**From:** HH345 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/04-semantic-information/` (information per read-out call; channel capacity), `physics-models/12-information-dynamics/` (transfer at the read-out with an in-flight placebo source)
**Question served:** **Q1** (what couples agents: the shape of the read-out channel at the receiving call). **Q4** is secondary (how much content information one call carries).

## Source HH (verbatim from the HH list, including refinements)
- **HH345 · Read-out channel capacity: information per call grows as k^(1−β) ≈ k^0.34.** H18's dilution (per-sender uptake ∝ k^−0.66) implies that the total uptake from a batch of k messages read at one call grows as k^0.34. H59 instead found that one read acts as one kick: dose saturates in #5. These two results disagree on the shape of the read-out channel's capacity curve.
  - *Prediction:* the Gaussian mutual information between the batch's message directions and the reader's next statement grows as k^(0.34 ± 0.1). Per-message information falls as k^−0.66.
  - *Check:* receiving calls from the ledger, with k the new items read; content projections orthogonalized to the reader's previous statement; the in-flight placebo at matched age; both models.
  - *Kill:* the exponent's CI excludes 0.34. Flat (exponent ≈ 0) means a hard capacity of one message per call; linear means no bottleneck.
  - *Impostors:* convergence: in-flight placebo. Exogenous: goal directions projected out. Priors: style_resid. Scheduler: n/a (call level).
  - *Models:* 04, 12 · *Builds on:* H18, H59, H08, H70

## Question
When an agent reads k new peer messages and then speaks, how does the content it takes up from the batch grow with k? Three shapes compete: no bottleneck (uptake ∝ k), H18's dilution (∝ k^0.34) and a hard capacity of one message per call (flat; H59's dose saturation).

## Model
**From:** `physics-models/04-semantic-information/` (information per call through a channel) and `physics-models/12-information-dynamics/` (transfer measured against an in-flight placebo source).

**H113 variant: a linear read-out channel with a k-dependent gain.** For a talk call c of reader i with batch B_c (the agent messages in i's pending set, k_c = |B_c|):
- x_m: the DQ5 statement vector (32-d, `style_resid32`) of batch message m; y_c: the vector of i's statement at call c; p_c: i's previous statement (same PT day).
- P_c projects out span{p_c, ĝ (goal and kickoff directions of the period, room kickoff where it exists), f_c (the out-of-batch window field: the unit mean of other agents' statements in i's room within ±30 min, excluding i, the batch and the in-flight set)}. y⊥ = P_c y_c, x⊥_m = P_c x_m.
- **Channel:** y⊥_c = γ(k_c) s_c + γ_F s^F_c + ε_c, with s_c = Σ_{m∈B_c} x⊥_m and s^F_c the same sum over the in-flight set F_c (others' messages in i's room posted after c's t_call and before y_c: unreadable by c).
- **Per-message uptake slope γ(k) = γ₁ k^(−b)** (H113 variant of H29's content pull).
- **Total uptake U(k) = k γ(k) ∝ k^(a_U), a_U = 1 − b** (H113's capacity exponent). Shapes: no bottleneck b = 0 (a_U = 1); H18 dilution b = 0.66 (a_U = 0.34); hard capacity b = 1 (a_U = 0).
- **Read-out information per call I(k)** (Gaussian, in bits): I(k) = −(D/2) log₂(1 − R²(k)), with R²(k) the day-cross-fitted share of |y⊥|² explained by γ̂ s in calls with k items, D = 32. At low SNR, I(k) ∝ γ(k)² E|s|²_k, so **a_I = 1 − 2b + r**, with **r = d ln E|s|²_k / d ln k − 1** the batch redundancy exponent (0 for independent messages, 1 for identical ones).

**Specification note (written before data).** HH345 states its exponent for the Gaussian mutual information, but its derivation (k × k^−0.66) is the total uptake U(k). In a linear Gaussian channel the two differ: if b = 0.66 and r ≈ 0, U ∝ k^0.34 but I ∝ k^−0.32. Both are scored: P1a scores the intended uptake exponent a_U; P1b scores the literal information exponent a_I. The identity a_I = 1 − 2b + r is used as an unfitted consistency check (P5).

**What would make HH345 true:** a_U's CI includes 0.34 in the pooled estimate and in most testable periods, with b's CI excluding both 0 and 1, the in-flight placebo pull well below the read pull, and the same shape in both embedding models.

## Data scheme (`scheme/`)
`scheme/build.py --period G<NN>` writes `data/processed/H113-readout-channel-capacity/G<NN>/` from shared tables only (no text; vectors are stored as float16 arrays of projected coordinates, not raw embeddings of text).
- **Inputs:** `pending_sets/G<NN>/` (talks, pending; wakes, wake_pending for the D2 native), `chat_core` (message rows, rooms, times), `embeddings/statements.parquet` + `chat_index.parquet` (statement row per message), `statements_style_resid32_<model>.npy` for bge_small and gte_modernbert (variant `white32`), `goal_vectors_<model>.npy` + `goals.parquet` (kinds goal, kickoff, kickoff_room) whitened with `embed_models.load_whitener(regime, 32, model)`, `producing_calls` and `context_ledger_items` (one-call batch variant), `chat_mentions_clean` (named items). Holdout: `pending_sets` already drops held-out days; every other table is filtered with `common.holdout_mask`.
- **Unit rows:** one row per scored talk call (pending_sets `talks`) with a statement vector for the talk message and a previous same-day statement by the reader. k = the number of agent-kind pending items with a statement vector (primary: pending set since the previous talk call, H18's ledger k); variant k_1 = the items new at the producing call only (HH345's "new items read" at one call).
- **Batch sums and placebo:** s_c, s^F_c and per-item projections are computed after P_c; per-item rows keep age (talk time − post time), rank (1 = newest), sender, named flag.
- **Output:** `G<NN>/calls_<model>.parquet` (call id, agent, day, room, k, k_1, k_F, ⟨y⊥, s⟩, |s|², ⟨y⊥, s^F⟩, |s^F|², ⟨s, s^F⟩, |y⊥|², newest-item terms), `G<NN>/items_<model>.parquet` (per item: call id, ⟨y⊥, x⊥⟩, |x⊥|², age, rank, named, read/in-flight), `counts.json`, `_provenance.json`.
- **Regimes covered:** every non-holdout period with pending sets (regimes I–III). Regime I/II calls are scheduled chat-mode calls (ledger `start_conf` low): regime is reported per period.

## Observables
1. **b̂ and a_U = 1 − b̂ (primary):** profile least squares of y⊥ on (k^−b s, s^F) over b ∈ [−0.5, 1.5]; cluster bootstrap over agent-days (300 draws; percentile CI).
2. **Binned γ_k:** per-message slopes in k bins {1, 2, 3–4, 5–8, 9–16, ≥ 17} (for the figure and a binned WLS check of b).
3. **I(k) and a_I:** day-cross-fitted Gaussian information per call in each k bin (bits), and the WLS slope of ln I on ln k over bins with I identified (lower CI bound > 0.02 bits, H87's rule; otherwise the bin is "n.i." and not ordered).
4. **r̂:** the slope of ln E|s|²_k on ln k, minus 1.
5. **Convergence placebo:** γ_F (per in-flight message) and the matched-age contrast: per-item slopes of read items with age ≤ 120 s vs in-flight items, in age bins 0–30, 30–60, 60–120 s, weighted by in-flight counts.
6. **Recency (rival R4):** the newest item's slope vs the other items' slope (rank 1 vs rank ≥ 2).
7. **Discrete check (`infra/shared/semantic_kappa.py`):** per item, X = k-means cluster (K = 8, fitted on the period's y⊥) of the reader statement, S = cluster of x⊥_m; `mi_corrected` with within-(agent) permutation floor, per k bin. Rows identified only when the lower interval bound exceeds 0.02 bits (H87 A1; the interval under-covers, Known issues).

## Null / baseline
- **No uptake:** γ ≡ 0; the cross-day surrogate (each call's batch replaced by a batch of the same k from another day of the same period) gives the null distribution of γ̂ and I.
- **Convergence (rival R3):** in-flight items share every time-local field with the read batch; a field-only world gives γ_F ≈ γ_read.
- **Shape nulls:** b = 0 (no bottleneck) and b = 1 (hard capacity); the kill compares b̂'s CI with 0.66.

## Rivals and impostors
- **Rivals:** (R1) hard capacity, one read = one kick (H59 G05): b = 1, U flat; (R2) no bottleneck, linear superposition: b = 0; (R3) common field (contemporaneous convergence): pull exists for unread items too, and its k-curve mimics dilution (a shared topic makes s grow ∝ k while y⊥ takes it up once); (R4) recency-led selection (H18 P3): the newest item is taken up at a fixed rate, older items ≈ 0, which also gives b ≈ 1.

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | n/a | Call-level design: each row is one receiving call; no time-binned synchrony statistic. | n/a |
| Exogenous field (kickoff/goal/operator) | yes | Goal, kickoff and room-kickoff directions projected out of y and x (P_c); human and nudge items excluded from s. | removed |
| Shared model priors | yes | `style_resid32` vectors in both models (b̂ agrees within 0.2 in 34/34 periods). No same- vs cross-family item split was run. | partly |
| Contemporaneous convergence | yes | The in-flight term in the fit (γ_F/γ₁ median 0.31) and the matched-age read − in-flight contrast (pooled +0.014 [0.006, 0.022]); A1 scores only periods where the contrast has CI > 0 and r < 0.7, because a time-local field alone gives b̂ ≈ 0.8. In-flight items co-respond to the same batch, so the contrast is conservative. | partly |

## Synthetic validation (axis F; before any real uptake statistic)
Simulator `analysis/synthetic.py`: the period's real call skeleton (every scored talk call with its real k, k_F, reader, day and the real batch membership), with synthetic 32-d vectors: messages x = field(room, t) + noise; reader statements y = Σ γ(k) x⊥ + field + own drift + noise, with the real SNR range calibrated so that |y⊥|² matches the data (no real y⊥·s is used). Worlds: **W0** no uptake, no field; **W1** field only (room topic random walk, τ = 30 min, no read uptake); **W2** b = 0; **W3** b = 0.66; **W4** b = 1 (select one item at random); **W5** recency selection (newest item only); **W6** W3 + W1's field. 40 runs per world on the skeletons of G18, G31, G38, G51. Report bias and 95% coverage of b̂ (W2–W4, W6), the false "b̂ finite and CI excludes 0" rate under W0 and W1, and whether field removal (P_c with f_c) is needed. **Decision rule fixed now:** the estimator counts as a test of b only if its coverage is ≥ 0.80 in W2–W4 and W6 and |bias| ≤ 0.15; if the field world W1 yields a b̂ with CI excluding 0 in > 10% of runs, the card reads b̂ only together with the placebo-corrected variant.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** hard capacity (R1), no bottleneck (R2), common field (R3), recency selection (R4).
**Locked holdout used for confirmation:** #43, #45–#50 talk calls and the #51 tail (51m), frozen in `analysis/confirm.py` (dry-run on stand-ins only, not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Batches are ledger pending sets, content is DQ5 vectors orthogonalized to the reader's previous statement and the goal; the same mapping runs in regimes I–III and both models. Limit: a linear channel sees only linearly decodable uptake. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | One γ₁ and b per period; per-call independence given the batch; the low-SNR identity for information holds only where per-bin R² < 0.05 (A1). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Excludes b = 0 and b = 1 in every identified period; information is day-cross-fitted. The field world is excluded only through the placebo rule. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The cross-fitted information curve saturates as the capacity fit implies (a_I near 0–0.3); the low-SNR identity a_I ≈ 1 − 2b + r holds within 0.2 in 7/11 low-SNR periods (tolerance post hoc). |
| E interventional | predicts the change across a natural experiment | 1 | NE42: b̂ invariant (|Δb̂| ≤ 0.09) while k rises ×1.5; D2 wakes (exogenous k) give a_U 0.29–0.31. NE03 underpowered. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Raw estimator: |bias| ≤ 0.045, coverage 0.7–1.0 in four uptake worlds on four skeletons. A field alone gives b̂ 0.79–0.87; the placebo rule separates it (0/50 vs 50–100%). The window-field variant is biased (A1). |
| G ground truth | agrees with known structure | 1 | Regime III (computer-use, items read across calls) has a stronger bottleneck (b 0.80) than regime I chat (0.69); the newest item is taken up more (recency +0.034), as H18 found for addressing. |
| H comparative | beats the named rivals | 1 | Beats R1 (hard capacity) and R2 (linear) everywhere; R3 (field) excluded only in identified periods; R4 (recency) is present but does not make b = 1. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. Talk-call b̂ 0.6–0.9 in 34/34 periods. |

## Prediction
*Written 2026-10-04 21:33 UTC, before running the analysis on real data.*

**What I had seen when writing this:** the cards of H18 (β 0.66 ± 0.02 on mentions; replies 0.85 with a one-parent budget; saturating 1/(k₀ + k) shape; recency explains as much in half the periods), H59 (one lever at the read-out; #5 dose saturates), H29 (content pull and the matched-age boundary test), H67, H70/H87 (κ estimator, identified rule), H50 and H40; the shared-module docs. To check feasibility I counted, per non-holdout period, talk calls with a statement vector and the new agent items at the producing call (e.g. #51: 40,956 talk calls, 18,195 with ≥ 1 new item, 1,082 with ≥ 10; #38: 4,558, 858 and 4; regime I periods have median one-call k 1–2, regime III median 0) and the pending-set k (median 1–7). No uptake slope, information or exponent was computed.

**Periods and roles.** Replication (`replication`): every non-holdout period with pending sets that passes the testability rule (expected: most of #3–#33 in regimes I/II, and #36–#44 and #51a–l in regime III). Natives (`native`): **G51** (D2 timer-wake batches: k set by others' talk while the reader slept, so k is not chosen by the reader), **NE03** (#10a vs #10b: the 2025-08-20 chat fetch limit caps what can reach the context), **NE42** (#39 → #40 → #41: the room merge doubles the batch size and the split undoes it).

**Testability rule (fixed now).** A period is testable if it has ≥ 300 scored talk calls with k ≥ 1 and ≥ 30 with k ≥ 8. Otherwise descriptive.

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1a (HH345 as derived: uptake) | pooled a_U CI includes 0.34, and a_U ∈ [0.24, 0.44] (point) in ≥ 1/2 of testable periods | pooled a_U CI excludes 0.34 (**kill**, both models) | 0.30 |
| P1b (HH345 as written: information) | pooled a_I CI includes 0.34 | a_I CI excludes 0.34 | 0.15 |
| P2 (a bottleneck exists) | b̂ CI excludes 0 (b > 0) in ≥ 2/3 of testable periods | b̂ CI includes 0 in > 1/3 | 0.70 |
| P3 (not a hard one-message capacity) | b̂ CI excludes 1 (b < 1) in ≥ 1/2 of testable periods | b̂ CI includes 1 in > 1/2 | 0.40 |
| P4 (read-out, not convergence) | pooled γ_F ≤ ½ γ₁ and the matched-age read − in-flight contrast > 0 with CI > 0 | γ_F ≥ γ₁, or the contrast CI includes 0 | 0.50 |
| P5 (unfitted consistency) | a_I (measured) within its CI of 1 − 2b̂ + r̂ (computed from the uptake fit and batch redundancy) in ≥ 2/3 of periods | disagreement in > 1/3 | 0.60 |
| P6 (both models) | bge and gte b̂ differ by ≤ 0.2 in ≥ 2/3 of testable periods | > 1/3 differ by more | 0.60 |
| P7 (rival R4) | the newest item's slope exceeds the older items' slope (pooled CI > 0) | CI includes 0 or reverses | 0.65 |
| P8 (discrete check) | per-item discrete information at k = 1 is identified (lower bound > 0.02 bits) in ≥ 1/2 of testable periods | identified in < 1/2 | 0.25 |

**Verdict rules (fixed now).** Per period: *supported* if a_U's CI includes 0.34 and b̂'s CI excludes 0 and 1; *failed* if a_U's CI excludes 0.34 in both models; *mixed* otherwise; *descriptive* if not testable. Card: *supported* if P1a and P4 hold; *failed* if the kill is met (the pooled a_U CI excludes 0.34 in both models); *mixed* otherwise.

Per-period predictions are in each `goalperiod-subhypotheses/G<NN>/README.md` (and `NE<NN>/`), written before that unit is run.

**Amendment A1 (2026-10-04 22:51 UTC, after the synthetic validation, before any real uptake statistic).** What I had seen: the synthetic summaries (`data/processed/H113-readout-channel-capacity/synthetic/summary.json`: skeletons G18 with 20 runs per world; G31, G38 and G51 13–15 Jul with 10 runs, cut from 20 because the machine load reached 138) and the real skeleton counts (talk calls, k ≥ 1, k ≥ 8, in-flight items). No real γ, b, I or contrast.
- **Primary estimator changed to the raw projection** (P_c = span{p_c, G}, no window field). In W2–W5 it has |bias| ≤ 0.045 and coverage 0.7–1.0 on all four skeletons. The window-field projection of the card (variant F) biases b̂ by up to +0.26 (W2) and covers 0–0.5 in W5; it is kept as a sensitivity row.
- **A topic field alone produces a bottleneck exponent.** W1 (field only, no uptake) gives b̂ 0.79–0.87 with a CI that excludes both 0 and 1 in every run; W6 (b = 0.66 plus the field) gives b̂ 0.73–0.74 with coverage 0. So b̂ ≈ 0.75–0.9 is not identified against a time-local field.
- **Field discriminators, fixed now:** (a) the matched-age read − in-flight contrast has CI > 0 in 0/50 field-only runs and in 50–100% of uptake runs (W3–W5); (b) the redundancy exponent r is 0.86–1.12 under a field and 0.30–0.51 under uptake alone. **Rule:** a period's b̂ counts as a read-out capacity only if its placebo contrast has CI > 0 and r < 0.7; otherwise the period is "not identified (field)" for P1–P3 and is reported, not scored. A pooled kill requires the identified periods.
- **The placebo-subtracted exponent fails** (subtracting the in-flight pull per item: W4 bias +0.28, W6 −0.7, because in-flight messages co-respond to the same batch). Dropped.
- **P5 holds only at low SNR.** The identity a_I = 1 − 2b + r is close in W3/W4 (low per-call R²) but fails in W2 (a_I −0.3 to 1.5 against 1.0), where R² is large. P5 is scored only on periods whose per-bin R² stay below 0.05.
- Not amended: the periods, the testability rule, the credences, the kill.

**Note N1 (2026-10-04 22:43 UTC, coordinator correction to the source exponent; before any real-data uptake statistic).** H18 has been re-scored: its all-talk-call exponent 0.66 (design D1) cannot be separated from H18's own reactive-timing null, which gives 0.75–0.80 with no budget. The identified value is #51's timer-wake design D2: per-sender uptake ∝ k^−0.50 [0.45, 0.56] (null ≈ 0); D2 is weak or contradictory in the small two-room periods. So H18 now predicts total uptake ∝ k^0.50, not k^0.34. The predictions above are not rewritten. Consequences: (i) every a_U result is reported against both values, **0.34 as pre-registered (P1a, kill)** and **0.50 as the corrected H18 value**; (ii) the G51 D2 wake batches (k set by others' talk while the reader slept) are promoted from a native to a co-primary design, because reply-driven batch sizes on talk calls can fake dilution; the talk-call exponent is read as D1-type (possibly reactive) evidence.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | descriptive | b̂ 0.77 [0.67, 1.06] bge, 0.76 gte; not identified |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | descriptive | b̂ 0.66 [0.55, 0.73] bge, 0.65 gte; not identified |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | descriptive | b̂ 0.67 [0.61, 0.73] bge, 0.70 gte; not identified |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | b̂ 0.64 [0.53, 0.75] bge, 0.67 gte; not identified |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | descriptive | b̂ 0.54 [0.43, 0.65] bge, 0.62 gte; not identified |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | descriptive | b̂ 0.61 [0.49, 0.76] bge, 0.65 gte; not identified |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | descriptive | b̂ 0.76 [0.68, 0.85] bge, 0.80 gte; not identified |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | descriptive | b̂ 0.74 [0.68, 0.82] bge, 0.74 gte; not identified |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | supported | b̂ 0.67 [0.60, 0.75] bge, 0.70 gte; identified |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | mixed | b̂ 0.75 [0.63, 0.86] bge, 0.79 gte; identified |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | descriptive | b̂ 0.78 [0.67, 0.88] bge, 0.79 gte; not identified |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | descriptive | b̂ 0.69 [0.63, 0.76] bge, 0.72 gte; not identified |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | descriptive | b̂ 0.73 [0.69, 0.79] bge, 0.75 gte; not identified |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | descriptive | b̂ 0.73 [0.66, 0.80] bge, 0.75 gte; not identified |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | descriptive | b̂ 0.78 [0.69, 0.86] bge, 0.80 gte; not identified |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | descriptive | b̂ 0.56 [0.46, 0.67] bge, 0.57 gte; not identified |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | descriptive | b̂ 0.66 [0.58, 0.73] bge, 0.64 gte; not identified |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | descriptive | b̂ 0.74 [0.69, 0.80] bge, 0.76 gte; not identified |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | descriptive | b̂ 0.75 [0.70, 0.80] bge, 0.75 gte; not identified |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | descriptive | b̂ 0.60 [0.52, 0.66] bge, 0.63 gte; not identified |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | b̂ 0.69 [0.65, 0.73] bge, 0.71 gte; not identified |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | descriptive | b̂ 0.71 [0.66, 0.76] bge, 0.74 gte; not identified |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | descriptive | b̂ 0.72 [0.68, 0.77] bge, 0.76 gte; not identified |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | supported | b̂ 0.68 [0.63, 0.73] bge, 0.70 gte; identified |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | mixed | b̂ 0.67 [0.61, 0.73] bge, 0.73 gte; identified |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | failed | b̂ 0.82 [0.75, 0.88] bge, 0.85 gte; identified |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | failed | b̂ 0.77 [0.72, 0.82] bge, 0.78 gte; identified |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication (also NE42 side) | mixed | b̂ 0.81 [0.65, 0.96] bge, 0.85 gte; identified |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication (also NE42 side) | descriptive | b̂ 0.78 [0.70, 0.89] bge, 0.76 gte; not identified |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication (also NE42 side) | descriptive | b̂ 0.81 [0.74, 0.88] bge, 0.85 gte; not identified |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | b̂ 0.78 [0.70, 0.86] bge, 0.85 gte; not identified |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | descriptive | b̂ 0.78 [0.73, 0.83] bge, 0.83 gte; not identified |
| [G51](goalperiod-subhypotheses/G51/README.md) | native (also replication) | failed | b̂ 0.86 [0.84, 0.88] bge, 0.90 gte; identified |
| [NE03](goalperiod-subhypotheses/NE03/README.md) | native | descriptive | #10a 288 calls (< 300); b̂ 0.60 → 0.63 (bge), 0.76 → 0.69 (gte): no steepening |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | supported | mean k 7.5 → 11.0 → 7.8; b̂ 0.81 → 0.78 → 0.81 (bge), 0.85 → 0.76 → 0.85 (gte) |

## Results
*Exploratory round 1, 2026-10-04 23:11 UTC, non-holdout days only.*
- **Code:** `scheme/h113scheme.py`, `scheme/build.py`; `analysis/h113lib.py` (profile-LS exponent, binned slopes, cross-fitted information, redundancy, placebo, recency, discrete check via `semantic_kappa.mi_corrected`), `synthetic.py`, `run.py`, `natives.py`, `score.py`, `confirm.py` (frozen, dry-run only).
- **Data:** `data/processed/H113-readout-channel-capacity/` (`G<NN>/` per-call and per-item terms for both models, raw and window-field variants, k-means labels; `synthetic/`; `results/`; `confirm_dryrun/`; `_provenance.json`; 94 MB).
- **Figures:** [`figures/summary_obs.pdf`](figures/summary_obs.pdf) (b̂ per period and the D2 wakes; total uptake U(k) on D2 batches), [`figures/summary_synth.pdf`](figures/summary_synth.pdf) (b̂ by synthetic world).
- **Estimates:** 216 rows in `per_period_estimates` (`readout_capacity_b`, `readout_placebo_contrast`, `readout_batch_redundancy_r`).

**Outcome vs prediction** (identified periods: bge #13, #36, #37, #38, #39, #51; gte #13, #16, #35, #36, #37, #38, #51)

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1a pooled a_U CI includes 0.34 (kill if excluded in both models) | bge 0.23 [0.16, 0.31], gte 0.22 [0.14, 0.30]; in band [0.24, 0.44] in 2/6 and 3/7 periods | **failed (kill met)** |
| P1a′ vs corrected H18 value 0.50 (Note N1) | excluded in both pools and in every identified period | failed |
| P1b a_I includes 0.34 | no pooled CI; identified a_I median 0.17 (range −0.48 to 0.61) | failed (descriptive) |
| P2 b > 0 (CI) in ≥ 2/3 | 6/6, 7/7 (and 34/34 testable) | supported |
| P3 b < 1 (CI) in ≥ 1/2 | 6/6, 7/7 | supported |
| P4 γ_F ≤ ½ γ₁ and contrast > 0 | γ_F/γ₁ median 0.31; contrast +0.014 [0.006, 0.022] (bge), +0.017 [0.009, 0.026] (gte) | supported |
| P5 low-SNR identity a_I ≈ 1 − 2b + r in ≥ 2/3 | 7/11 low-SNR periods within 0.2 (tolerance post hoc) | failed (narrowly) |
| P6 bge and gte within 0.2 in ≥ 2/3 | 34/34 | supported |
| P7 newest item > older items | +0.034 [0.025, 0.043] (bge), +0.035 [0.025, 0.045] (gte) | supported |
| P8 discrete information at k = 1 identified in ≥ 1/2 | 31/34 (bge), 30/34 (gte); 0.03–0.31 bits per item; intervals under-cover | supported (caveat) |
| N1 G51 D2 wakes within ±0.15 of talk calls | wakes 0.69 / 0.71 vs talk 0.86 / 0.90 (Δ −0.17 / −0.19) | failed |
| N2 NE03 steeper after the fetch limit | #10a 288 calls (< 300): Δb̂ +0.03 / −0.07 | descriptive |
| N3 NE42 invariance | |Δb̂| ≤ 0.09 while k ×1.5 | supported (weak: one side identified) |

**Synthesis.**
1. **The read-out channel is a bottleneck of intermediate strength.** Per-message content uptake falls as k^−b with b ≈ 0.7 (D2 wakes) to 0.8 (talk calls pooled). Total uptake per call grows as k^0.2–0.3: a call that reads 10 messages takes up about 2× the content of a call that reads one, not 10× and not 1×.
2. **Exogenous batches give the cleanest number.** On #51 timer-wake batches (k set by others while the reader slept), a_U = 0.29–0.31, inside HH345's 0.34 ± 0.1 and below H18's corrected 0.50. Talk calls give a steeper curve (b higher by 0.17–0.19), the same direction as H18's reactive-timing inflation of its talk-call exponent.
3. **It is not one message per call.** Every identified period excludes b = 1. The newest item is taken up more than older ones, but older items still carry content. H59's "one read = one kick" holds for activity dose, not for content.
4. **Fields are the main threat.** On real skeletons a topic field alone gives b̂ ≈ 0.8. Only 6–7 of 34 testable periods pass the placebo rule; the other 27 sit at b̂ 0.6–0.85 and are reported, not scored.
5. **Information per call saturates.** The cross-fitted Gaussian information rises from k = 1 to k ≈ 5–8 and then flattens or falls (e.g. #38: 1.07 → 1.70 → 1.13 bits; #51: 0.59 → 0.10 bits at k ≥ 17).

**Claim that stands:** Content uptake per read-out call grows sublinearly with batch size, total uptake ∝ k^a_U with a_U = 0.31 [0.25, 0.37] on #51 timer-wake batches (exogenous k) and 0.23 [0.16, 0.31] pooled over 6 field-identified periods (bge; gte agrees), excluding both a one-message capacity and H18's corrected 0.50. Exclusions: HH345's 0.34 is excluded by the talk-call pool (kill met); P1b and P5 not established; NE03 underpowered; NE42 weak (one side identified); 27 testable periods are not identified against a field.

## Confirmatory design (frozen 2026-10-04 in `analysis/confirm.py`; dry-run on stand-ins only, NOT RUN)
Targets: talk calls of #43, #45–#50 (held-out days) and the #51 tail (51m: talk calls and D2 wakes). **C1:** #51-tail D2 wake a_U has a 95% CI inside (0, 0.50). **C2:** the DL pool of talk-call a_U over testable targets (bge) has a CI inside (0, 0.50). **C3:** pooled matched-age contrast > 0 with CI > 0. **C4:** bge and gte b̂ within 0.2 in ≥ 2/3 of testable targets. **C5:** pooled newest − older slope > 0 with CI > 0. Dry run (stand-ins #38, #41, #44 and units 51h–51l): C2–C5 pass; C1 fails narrowly (stand-in tail a_U 0.39 [0.28, 0.51], 1,302 wakes): a pipeline check, not evidence, but it shows C1 is underpowered on ~8 days. Guard: `--confirm --i-understand-this-uses-the-locked-holdout`, a committed H113 folder, `holdout_ledger.check()` (family `readout_capacity`). Held-out pending sets are built in memory through `pending_sets.build_period(..., include_holdout=True)` into the confirm folder, never under `data/processed/shared/`. Reuse: H18 and H68 (`dilution_addressing`), H85 and H70/H84/H87 (`semantic_kappa`) plan the same targets with other statistics; disclose.

## Round 2 redirects (proposed by the round-1 agent, 2026-10-04)
- **H113-R1. A field-robust exponent.** Estimate b from within-period variation in k that is exogenous to topic (D2 wakes in every regime-III period; NE44's pause change is held out), or from a matched-age contrast binned by k.
- **H113-R2. Selection vs averaging.** A linear channel cannot tell whether the reader averages the batch or picks one item; a mixture model on per-item alignment (one item taken up vs all diluted) separates them.
- **H113-R3. Capacity as an agent constant.** Fit b per agent (exception (b)) and test whether it tracks H68's per-agent dilution σ_β.

## Notes
- 2026-10-04 21:33 UTC: round-1 agent (H113 together with H112). Card written before any uptake statistic; feasibility counts listed above.
- 2026-10-04 22:43 UTC: Note N1 (H18 re-scored by the coordinator). 22:51 UTC: A1 after the synthetic (runs cut to 10 per world on three skeletons because of machine load). 23:03 UTC: period predictions; real run 23:05–23:09 UTC.
- Storage: projected vectors are not stored (k-means labels only) to stay within ~100 MB. Compute: ≤ 2 threads, one heavy job at a time.
