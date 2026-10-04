# H106: A finite magnet's magnetization wanders as 1/N: the slow mode's decay time should grow with village size

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only). Inconclusive: the 1/N law cannot be tested in one village. The slope estimator has power 0.00 against α = −1 on the real regime-I panel (even a noiseless oracle has SD 0.45), and the real slopes are uninformative (α_k +0.40 / +1.22, CIs ±2).**
- **Finite-size exponent:** α_k = +0.40 [−1.62, 2.41] (bge), +1.22 [−1.45, 3.88] (gte); likelihood ratio magnet/drift 0.90 / 0.65.
- **Natives:** NE27 (N 4 → 7) Δln k +0.41 / +0.38 vs magnet −0.55, power 0.06–0.09; #51 joins power ≤ 0.21. Both inconclusive.
- **Post hoc:** the slow mode's near-lag similarity drops from 0.25–0.28 (N < 8, May–Oct 2025) to 0.00–0.11 (N ≥ 8, mid-Nov 2025 on); the gte drop lies outside both the drift and magnet worlds. Bears on H81 R1 (see Results).
- Card and predictions written 2026-10-04 21:27 UTC before any real-data statistic; synthetic first (Amendment A3: unpowered, before real data). `analysis/confirm.py` frozen and dry-run, **not run**. Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH335.
**Question (GOALS.md):** **Q3** (is there collective order beyond fields?). H81 found a regime-I content slow mode beyond members and measured fields (τ_u ≈ 23–28 d). Its open rival is a slow exogenous drift. H106 asks whether the slow mode has the inertia of an ordered finite magnet: does its decorrelation rate fall as 1/N?
**Fields:** stat mech (finite-size ordered phases, rotational diffusion of the order parameter), sociophysics
**Literature:** none filed. The finite-N rotational diffusion of an ordered O(n) magnet (D_rot ∝ 1/N; Anderson's tower of states, Hasenfratz & Leutwyler 1990†) is quoted from memory. Project cards used: H81 (slow mode, two-way FE composition null, size-matched m = 4 subsets O5b), H82 (boundary trace carried by members' own content), H85 (regime-I talk volume nearly conserved across N; active population), H89 (no persistent attractor within periods).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; **Population N(t)**, variant **active population** (H85: agents with ≥ 1 record on the day, Claude Code excluded); Regime (never pooled); Driving / external field; Agent state, variant *vector* (H01's **agent state (vector), whitened statement mean**, DQ5 `style_resid`); **Size-matched grouping** (H81 form: random 4-agent subsets). H81's proposed variants are used as H81 defines them: **personal vector (leave-goal-out, two-way FE)**, **culture residual (composition null)**. New named variants proposed for DEFINITIONS.md (defined under Observables): **active-day index a(d)**, **slow-mode decorrelation rate k (per active day)**, **finite-size exponent α_k**, **split-half block reliability R_b**.
**From:** HH335 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (primary: rotational diffusion of a finite ordered magnet), `physics-models/14-scaling-and-fluctuations/` (tool: size-matched subsets, finite-size scaling)
**Data inputs (shared tables first):** `infra/shared/culture_vectors.py` outputs (`data/processed/shared/culture_vectors/`: eligible agent-days, DQ5 vectors of both models and three variants, exogenous directions, blocks) and its functions `projectors`, `personal_vectors(method="fe")`; `activity_bins_fixed` (active population); `calendar` (active-day index); `roster`; `holdout_mask`.

## Source HH (verbatim from the HH list, including refinements)
- **HH335 · A finite magnet's magnetization wanders as 1/N: the slow mode's decay time should grow with village size.** In a finite ordered magnet with no pinning field, the direction of the total magnetization diffuses, and the rotational diffusion constant is ∝ 1/N (more spins, more inertia). An outside drift has no reason to depend on how many agents are present.
  - *Prediction:* across regime-I blocks (N 4–12), the per-active-day decorrelation rate of the culture direction u_b falls with N_present, with a log-log slope near −1. An outside drift gives slope 0.
  - *Check:* compute the decorrelation from random 4-agent subsets in each block (H81 O5b). The estimation noise is then the same at every N, and only the real N can set the inertia. Use split-half (odd/even days) disattenuation for the remaining noise. Both models.
  - *Kill:* the slope's CI includes 0 and excludes −0.5.
  - *Impostors:* estimation noise is the main fake ∝ 1/N, and the size-matched subsets remove it. Exogenous and priors: as in H81. Scheduler: n/a.
  - *Models:* 11, 14 · *Builds on:* H81, H89 (no persistent attractor), H85

## Question
Does the decorrelation rate of H81's regime-I culture direction fall with the number of agents present, as k ∝ N^α with α ≈ −1 (a finite ordered magnet), or is it independent of N (α ≈ 0, an outside drift)?

## Design: two layers (Vivian, 2026-10-04)
- **Replication** (role `replication`): per regime-I goal period, the local near-lag culture similarity and its active population N (points on the phase diagram), and the card-level finite-size exponent α_k across those periods. Exceptions: **(c)** the slow mode is a cross-period object (H81: the pairs of blocks in different goals are the object), and **(d)** one period has one or two blocks, too few for its own rate, so α_k is estimated jointly from all cross-goal block pairs with period-specific N. Per-period values are reported next to it.
- **Natives** (role `native`): **NE27** (2025-08-18, N 4 → 7 at the #10 kickoff: N jumps at a fixed calendar time, a partition contrast against outside drift) and **G51 with NE32 + NE33** (batch joins inside #51 with one goal and one scaffold: does the #51 common mode decorrelate more slowly after N jumps?).
- **Regime III** (#36–#44, #51 weekly blocks; N 12–32) is a separate phase-diagram point, descriptive only (H81: regime-III slow mode marginal, power ≤ 0.42). Never pooled with regime I.
- **Coordination with H81 round 2** (running in parallel): H106 does not edit H81. It bears on H81's rival R1 (exogenous slow drift); see "What this means for H81" below once results exist.

## Model
**From:** `physics-models/11-vector-spins/`.
H81's composition model with a collective slow field: v_{i,d} = a_i + h_{G(d)} + w_{b(d)} + u(t_d) + e_{i,d} (agent personal vector, goal field, block field, slow culture mode, agent-day noise). H106 adds the finite-magnet law for the dynamics of u:

  du = −k(t) u dt + √(2 k(t) σ_u²) dW,  k(t) = k_6 · (N(t)/6)^{α_k}

- u is stationary with fixed variance σ_u² (a magnet's |m| is fixed; only its direction wanders). Its autocorrelation between times t and t′ is exp(−Λ(t, t′)), Λ = ∫ k dt over active days.
- **Finite magnet (HH):** α_k = −1. More agents, more inertia, slower wandering.
- **Outside drift (H81 R1):** α_k = 0. The drift rate does not know N.
- Time runs on the **active-day index** (village run days), as the HH asks; calendar days are a variant.
- Parameters: k_6 (rate at N = 6, per active day), α_k, amplitude A (the slow-mode share of the disattenuated block similarity), and s_∞ (the far-lag baseline; negative because H81 centers block vectors).

**Rivals (the slope each predicts for the size-matched estimator).**
- **R1, exogenous slow drift:** α_k = 0.
- **R2, conserved-flux record:** a stigmergic record (village sites, docs, chat history) refreshed by the room's talk. H85 found regime-I room talk throughput nearly flat in N (β_msg 0.09). The record then turns over at an N-independent rate, so α_k ≈ 0. R2 is endogenous but looks like R1 in this test.
- **R3, member-carried persistence (H82):** each agent continues its own content. Independent random 4-subsets of two blocks share fewer agents when N is large (expected shared ≈ 16/N for a stable roster), so the similarity falls faster with lag at large N: α_k > 0 for the primary estimator; ≈ 0 after the overlap adjustment (V4).
- **R4, estimation noise ∝ 1/N:** a full-roster block vector has noise ∝ 1/N, so it looks more stable at large N: fake α_k < 0. Removed by the 4-subsets (V3 shows its size).
- **R5, sampling depth falls with N:** H85 found each agent's talk share falls as N^−0.89 in regime I, so agent-day vectors get noisier at large N. With a fixed amplitude this fakes α_k > 0. Removed by split-half disattenuation (V1) and the free-amplitude variant (V2).
- **R6, calendar trend in persistence:** N rises with calendar time in regime I (4 until 08-12, 6–8 to mid-November, 9–12 after), and so do model generations and scaffold steps (NE03 08-20, NE04 09-05, NE08 12-10). Any calendar trend in τ aliases into α_k. Partition contrast: NE27 (N jumps at fixed time); scaffold-segment intercepts (V5).

## Data scheme (`scheme/`)
Script: `scheme/build.py` (shared tables only; no text read or written; held-out rows dropped with `common.holdout_mask` and asserted).
- **Inputs:** `data/processed/shared/culture_vectors/` (agentdays, vecs, dirs, blocks); `activity_bins_fixed`; `calendar`; `roster`.
- **Transform:**
  1. Panel per regime (I, III) as `culture_vectors` builds it: eligible agent-days (n_chat + n_intent ≥ 5; agents 19, 28, 30 excluded), blocks = goal × ISO week.
  2. **Active population N_d** per non-holdout PT day: agents (Claude Code excluded) with ≥ 1 record in `activity_bins_fixed` that day (H85's rule over the whole day). Block N_b = mean N_d over the block's days. Variant: N_b = eligible members (`blocks.n_agents`).
  3. **Active-day index a(d):** the rank of PT day d among village run days (`calendar` rows, all regimes). Only the existence of a run day is used, never content or counts of a held-out day. Block mid a_b = mean a(d) over the block's eligible days.
  4. N(a) between blocks: linear interpolation of N_b in a (no held-out day is read).
- **Output:** `data/processed/H106-slow-mode-finite-size/` (`blocks_<regime>.parquet`: block, goal, N_b, n_members, a_b, mid_day, n_days; `nday.parquet`; analysis outputs in `synthetic/`, `replication/`, `natives/`; `_provenance.json`).

## Observables
*Written 2026-10-04 21:27 UTC. Sampling facts already seen: the regime-I and III block tables of `culture_vectors` (dates, eligible member counts: N = 4 for all 20 blocks of #2–#8, 6–8 for #10–#19, 9–12 for #20–#31), the NE catalog rows. No content statistic has been computed.*

**Residuals.** As H81 (Amendment A1): exogenous directions projected (kickoff, goal text, room kickoffs, human-message centroid of the goal, #51 agent goals); personal vectors from `culture_vectors.personal_vectors(method="fe")`, the **two-way agent + goal fixed effect** on the agent's other goals of the regime (not the leave-goals-out mean, which manufactures cross-period structure; infra Known issues). r_{i,b} = Π(v̄_{i,b} − μ_i^{(−G)}).

**O1. Size-matched culture vectors (the HH's check).** In each block, D = 50 random 4-agent subsets of the members with residuals (blocks with < 4 dropped). Subset culture vector u_b^{(d)} = mean of the 4 residuals, centered on the goal-equal-weight mean of the draw's block vectors (H81 A1). Pair similarity s̄_{bb′} = mean over d of cos(u_b^{(d)}, u_{b′}^{(d)}) with independent draws in the two blocks.

**O2. Split-half block reliability R_b.** For each draw, the 4 agents' residuals averaged over the odd and over the even active days of the block (≥ 2 agents per half): rel_b = mean_d cos(u_b^{odd}, u_b^{even}); Spearman–Brown R_b = 2 rel_b / (1 + rel_b). Smoothed R̂_b: WLS fit of R_b on [1, ln N_b, ln n_days_b] over blocks with ≥ 2 days, clipped to [0.05, 1]. Disattenuated similarity s̃_{bb′} = s̄_{bb′} / √(R̂_b R̂_{b′}).

**O3. Finite-size exponent α_k (primary, card level).** Weighted NLS over all cross-goal block pairs of the regime:
  s̃_{bb′} = A · exp(−Λ_{bb′}) + s_∞,  Λ_{bb′} = k_6 ∫_{a_b}^{a_{b′}} (N(a)/6)^{α_k} da
with goal-pair weights (each goal pair counts once; H81 A1). Bounds: A ∈ [0, 3], k_6 ∈ [0.002, 2] per active day, α_k ∈ [−4, 4], s_∞ ∈ [−0.5, 0.5]. **CI:** delete-one-goal jackknife (t quantile, n_goals − 1 df). τ_6 = 1/k_6 active days is reported.

**O4. Per-period points (replication rows).** For each goal period G: N_G (mean N_b of its blocks) and ρ_G, the goal-pair-weighted mean s̃ between G's blocks and other goals' blocks within 10 active days. Its SE is the SD of the pair values / √(n pairs). Descriptive.

**O5. Variants (robustness, each with its own synthetic calibration where noted).**
- V2 free amplitude: no disattenuation; A(N̄) = A (N̄_{bb′}/6)^β, N̄ the geometric mean of the two blocks' N.
- V3 full roster (no subsets; all members), disattenuated: the size of the R4 impostor.
- V4 overlap-adjusted: + β_J · J̄_{bb′}, J̄ the mean over draws of (shared agents between the two subsets)/4 (separates R3).
- V5 calendar control: ln k gets a free intercept per scaffold segment (split at NE04 2025-09-05 and NE08 2025-12-10); α_k from within-segment N variation and NE27.
- V6 N = eligible members. V7 calendar days instead of active days. V8 without Gemini 2.5 Pro (agent 6). V9 variants `white32` and `style_resid_period`. Both models throughout.

**O6. Natives.**
- **N1 NE27 (regime I, 2025-08-18; #9 held out and masked).** Window: blocks of #2–#8 (before, N 4) and #10–#18 (after, N 6–8). Same NLS with two rates: k_pre for the active days before 08-18 and k_post after (Λ integrates each part). Statistic Δln k = ln(k_post/k_pre). Magnet: Δln k = −ln(N̄_post/N̄_pre) (≈ −0.5 for 4 → 6.8). Drift: 0. Null and power: the synthetic worlds below on the same window. Placebo: the same two-rate fit at fake boundaries inside the N ≥ 6 era (2025-10-20, 2025-11-17, 2026-01-05), where N changes little.
- **N2 G51 with NE32 + NE33 (regime III, #51 non-holdout days 07-06 → 09-04).** Day residuals as H81's native (Π_{51,i}(v_{i,d} − m_i), m_i the agent's own #51 mean). Cross-agent lagged alignment L(k) = mean over i ≠ j of r_{i,d}·r_{j,d+k} / mean |r|² (pairwise, so its expectation does not depend on N; no subsets needed). Per window W, φ_W = L_W(1)/L_W(0⁺) with L(0⁺) the equal-time cross-agent alignment, and k_W = −ln φ_W. Windows: NE32 pre 07-06 → 07-08 vs post 07-10 → 07-17; NE33 pre 08-27 → 09-02 vs post 09-03 → 09-04. Statistic Δln k per event; magnet: −ln(N_post/N_pre). Placebo: the same contrast at every other #51 day boundary with the same window lengths. Within-#51 slope: weekly k_w vs weekly N (9 weeks), descriptive.

## Null / baseline
*Written 2026-10-04 21:27 UTC, before any real-data content statistic.*
- **Synthetic worlds on the real regime-I panel** (real presence, blocks, exogenous directions; H81's planted covariances: agent, goal and block parts from the real projected vectors as sampling facts; real agent-day residuals permuted across rows). The full pipeline runs unchanged.
  - **S0:** no slow mode (H81's composition null).
  - **D (outside drift):** an OU slow mode with share s = 0.5 of the goal-field covariance (H81's matched scenario) and a constant rate, τ = 25 calendar days converted to active days. α_true = 0.
  - **M (finite magnet):** the same share, k(a) ∝ N(a)^{−1}, normalized so that its mean rate over regime I equals D's. α_true = −1.
  - **H:** as M with α_true = −0.5.
  - **D+R3:** D plus H81's individual drift S2 (share 0.25): member-carried persistence.
  - **D+R5:** D with agent-day noise SD scaled by (N_b/6)^{0.45} (variance ∝ N^0.89, H85's talk-share law).
  - D and M at share 0.25 (sensitivity).
- **Size and power:** the share of replicates whose jackknife CI excludes 0 (size under D, power under M); the kill rule's firing rate under D (true kill) and under M (false kill); CI coverage.
- **Natives:** the same worlds restricted to the NE27 window; placebo boundaries (empirical). #51: planted common mode with τ_d ∝ N on the real #51 day panel.

## Impostor table (STANDARDS.md §1)
| Impostor | How it could fake this result | How H106 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | day length and agent counts change the statement mix; a block's number of days changes its noise | one vector per agent-day (each agent counts once); split-half reliability per block with ln n_days in the smoother; cross-goal pairs only (weeks apart), so day-edge synchrony cannot carry a lagged similarity | removed (HH: n/a) |
| Exogenous field (goal, kickoff, operator) | themed goal runs or a slow outside drift make nearby blocks alike | H81's projections (kickoff, goal, room kickoffs, human-message centroid); the test is the N-dependence of the rate, which an outside drift does not have; NE27 compares rates on both sides of an N jump 1 week apart (partition contrast); scaffold-segment intercepts (V5) | partly (an outside drift whose rate changes on 08-18 or with model generations remains; R6) |
| Shared model priors (family, style) | a changing family mix with N fakes a drift in persistence | DQ5 `style_resid`; two-way FE personal vectors remove each agent's prior; without Gemini 2.5 Pro (V8); `white32` (V9) | removed (agent level); family-level persistence partly |
| Contemporaneous convergence | agents in one block write alike without reading | only cross-goal (lagged) block pairs enter O3; random subsets in the two blocks are drawn independently; the #51 native uses i ≠ j lagged pairs | removed for O3/N2; n/a for equal time (not used) |
| **Estimation noise ∝ 1/N** (the HH's main fake) | a full-roster block vector is more reliable at large N and looks slower | fixed m = 4 subsets at every N; split-half disattenuation; V3 shows the fake | removed (V1) |

## Prediction
*Written 2026-10-04 21:27 UTC, before running the analysis on real data.*

My prior for α_k ≈ −1 is low (about 0.15). H82 found the boundary trace carried by members' own content, H89 found no persistent attractor, and H85 found regime-I talk throughput flat in N, which gives a record-borne mode an N-independent refresh rate (R2). N is also almost collinear with calendar time in regime I (R6).

- **P1 finite-size exponent (headline, HH):** regime-I α_k (V1) has a 95% CI that excludes 0 and includes −1, in both models. *Against (kill, HH):* the CI includes 0 and excludes −0.5 in both models. A CI that excludes 0 on the positive side (α_k > 0) also counts against (R3 or R5). Anything else: **inconclusive**.
- **Power rule:** if the synthetic power of V1 to exclude 0 under M (α = −1) is < 0.8, a non-negative result is reported as "inconclusive for α = −1", not "failed", unless the kill clause fires with size ≤ 0.1 under M.
- **P2 NE27 partition contrast (native N1):** Δln k < 0 with the placebo percentile ≤ 0.10 and the point estimate within ±0.5 of −ln(N̄_post/N̄_pre), both models. *Against:* Δln k ≥ 0, or inside the placebo band. Prior 0.15.
- **P3 subsets matter (impostor check, descriptive):** V3 (full roster) gives a more negative α_k than V1. If V3 ≈ V1, estimation noise was not an impostor here.
- **P4 robustness:** α_k keeps its sign and stays within its V1 CI under V2, V4, V6, V7, V8 and V9. V5 (calendar control) is reported; its CI is expected to be wide.
- **N2 G51 + NE32 + NE33 (native):** Δln k < 0 at both joins, placebo percentile ≤ 0.10 for at least one. *Against:* both ≥ 0.5. Prior 0.1; likely unpowered (N rises only ×1.1–1.2), in which case **inconclusive**.
- **Regime III:** α_k reported descriptively; no verdict.
- **Overall reading (fixed now).** **Supported:** P1 passes in both models and P2 does not contradict it (Δln k < 0). **Failed:** the P1 kill fires in both models (with power ≥ 0.8 under M), or α_k > 0 with CI excluding 0. **Mixed:** P1 passes in one model, or P1 passes and P2 contradicts it. **Inconclusive:** otherwise.
- **What each outcome means for H81's R1.** α_k ≈ −1 with NE27 agreeing: the slow mode has agent inertia, which an outside drift lacks; R1 loses ground. α_k ≈ 0: consistent with R1 *and* with the conserved-flux record R2; it does not decide H81's carrier. α_k > 0: member-carried persistence (R3), which H81's overlap adjustment was meant to exclude.

## Amendments (dated; all before any real-data statistic unless marked)
- **A1 (2026-10-04 21:41 UTC; design, before the synthetic results).** Only two placebo breaks fit inside the N ≥ 6 era of regime I (2025-11-03, 2025-12-15), so a placebo percentile ≤ 0.10 is impossible. P2's null becomes the drift-world (synthetic D) distribution of Δln k on the same NE27 window: pass if Δln k < its 5th percentile and within ±0.5 of the magnet value, both models. The two placebo breaks are reported descriptively.
- **A2 (2026-10-04 21:41 UTC; design, before the synthetic results).** N2 uses Δφ = φ_post − φ_pre instead of Δln k, because k = −ln φ is undefined when φ falls outside (0, 1) in windows of 2–6 days. The magnet predicts Δφ > 0, so the pass needs a placebo percentile ≥ 0.90 (the mirror of ≤ 0.10 for Δln k). Power: a planted day-level OU common mode (τ = 3 active days × N_d/N̄, share 0.05 as H81 PH3, and 0.2) on the real #51 panel.

## Synthetic validation (axis F; run 2026-10-04 21:31–21:57 UTC, before any real-data statistic)
`analysis/synthetic.py` → `data/processed/H106-slow-mode-finite-size/synthetic/` (replicates.parquet, synthetic.json). Real regime-I panel (42 blocks, 24 goals, 824 cross-goal pairs), both models; 300 replicates for D and M, 200 for the others; V1 with the delete-one-goal jackknife CI.

| World (α_true) | median α̂ (bge / gte) | SD | median jackknife SE | CI excludes 0 (neg / pos) | P1 pass | kill fires | α̂ below D's q05 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S0 (no mode) | +0.93 / +0.59 | 2.7 / 2.5 | 3.6 | 0.04 / 0.10 | 0.01 / 0.04 | 0.03 / 0.01 | 0.34 / 0.29 |
| D drift (0) | +0.42 / +0.39 | 0.66 / 0.77 | 1.06 / 1.00 | 0.00 / 0.00–0.01 | 0.00 | 0.04 / 0.03 | 0.05 |
| M magnet (−1) | **+0.22 / +0.25** | 0.74 / 0.74 | 1.05 / 1.10 | **0.00** / 0.00–0.01 | **0.00** | 0.01 / 0.02 | **0.09 / 0.06** |
| H (−0.5) | +0.21 / +0.19 | 0.64 / 0.71 | 1.04 | 0.00 | 0.00 | 0.01 / 0.03 | 0.07 / 0.05 |
| D+R3 member drift (0) | +0.40 / +0.45 | 0.52 / 0.50 | 0.85 | 0.00–0.01 | 0.00 | 0.04 / 0.08 | 0.01 / 0.00 |
| D+R5 depth (0) | +0.49 / +0.37 | 0.68 / 0.89 | 1.0 | ≤ 0.01 | 0.00 | 0.06 / 0.04 | 0.06 / 0.07 |
| D, M at share 0.25 | +0.38–0.44 / +0.16–0.33 | 1.3–1.5 | 1.7–2.2 | ≤ 0.03 | ≤ 0.01 | 0.01 | 0.10–0.21 |

- **NE27 contrast (two-rate):** median Δln k +0.29 / +0.32 under D and +0.11 / +0.16 under M (magnet value −0.55); SD 1.3–1.4. Power of the D-world 5% test under M: **0.06 / 0.09**.
- **Variants:** V3 (full roster) has the same attenuation (D +0.37 / +0.33, M +0.17 / +0.21); V2 and V4 are noisier (SD 1.2–1.8); V5 (segment intercepts) has SD 2.5–2.7.
- **Regime III** (#36–#44, #51): SD ≈ 2.8, median SE 3.9–5.3. No information.
- **Oracle check (scratch, not saved):** fitting the noiseless planted slow-mode path itself (no agents, no noise) gives α̂ −0.53 ± 0.45 for α = 0 and −0.88 ± 0.42 for α = −1. The limit is one OU trajectory: regime I spans about 13 decay times, and the N contrast compares two segments of that one path.

Readings: (1) V1 is unbiased in neither world: it is shifted by about +0.4 and attenuated to about 0.2 of the true slope (M − D: −0.20 / −0.14 for a true −1). (2) Power to exclude 0 under the magnet is 0.00 in both models; a synthetic-calibrated one-sided test reaches 0.06–0.09. (3) The kill clause fires in 1–2% of magnet worlds and 3–4% of drift worlds: it does not discriminate. (4) Coverage of the jackknife CI is 0.87–0.99, so the CI is honest but wide (±2). (5) Member-carried drift (R3) and falling sampling depth (R5) do not move α̂ much beyond the common +0.4 shift. (6) Even a perfect estimator would have SD ≈ 0.45 on regime I: the HH's test needs several independent trajectories (more villages, or many more decay times), not better denoising.

- **A3 (2026-10-04 21:58 UTC; after the synthetic, before any real-data statistic).** (a) P1 and P2 are **unpowered** (power ≤ 0.09 against α = −1). By the card's power rule their verdict is **inconclusive** whatever the real estimate, and a kill outcome does **not** count as failed (the kill fires as often under the magnet as under drift). (b) The real α̂ and Δln k are still computed with the frozen V1 and reported as percentiles of the D and M distributions, with the synthetic likelihood ratio p(α̂ | M)/p(α̂ | D) (Gaussian kernel density over the replicates) as the evidence measure. (c) One outcome remains informative: α̂ above the 97.5th percentile of D (bge 0.42 + 2·0.66 ≈ 1.8) would point to an estimator or member-carried artifact beyond the synthetic worlds. (d) Natives N2 stays as specified (its own planted power decides). (e) No change of estimator is made after seeing these numbers: every estimator tried (V1–V5) has the same information limit.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | descriptive | regime I, N 3.5: ρ_G +0.34 / +0.45 (bge / gte; 3 pair(s) ≤ 10 active days) |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | descriptive | regime I, N 4.0: ρ_G +0.40 / +0.55 (bge / gte; 3 pair(s) ≤ 10 active days) |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | descriptive | regime I, N 4.0: ρ_G +0.30 / +0.33 (bge / gte; 9 pair(s) ≤ 10 active days) |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | regime I, N 4.0: ρ_G +0.39 / +0.24 (bge / gte; 8 pair(s) ≤ 10 active days) |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | descriptive | regime I, N 4.0: ρ_G +0.25 / +0.19 (bge / gte; 11 pair(s) ≤ 10 active days) |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | descriptive | regime I, N 4.0: ρ_G +0.18 / +0.23 (bge / gte; 5 pair(s) ≤ 10 active days) |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | descriptive | regime I, N 4.0: ρ_G -0.12 / -0.07 (bge / gte; 9 pair(s) ≤ 10 active days) |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | descriptive | regime I, N 7.0: ρ_G +0.27 / +0.21 (bge / gte; 4 pair(s) ≤ 10 active days) |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | descriptive | regime I, N 7.0: ρ_G +0.42 / +0.35 (bge / gte; 3 pair(s) ≤ 10 active days) |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | descriptive | regime I, N 7.0: ρ_G +0.26 / +0.24 (bge / gte; 4 pair(s) ≤ 10 active days) |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | descriptive | regime I, N 6.0: ρ_G +0.22 / +0.23 (bge / gte; 3 pair(s) ≤ 10 active days) |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | descriptive | regime I, N 7.0: ρ_G +0.03 / +0.17 (bge / gte; 2 pair(s) ≤ 10 active days) |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | descriptive | regime I, N 7.0: ρ_G +0.20 / +0.34 (bge / gte; 3 pair(s) ≤ 10 active days) |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | descriptive | regime I, N 7.5: ρ_G +0.28 / +0.35 (bge / gte; 6 pair(s) ≤ 10 active days) |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | descriptive | regime I, N 7.1: ρ_G +0.31 / +0.34 (bge / gte; 6 pair(s) ≤ 10 active days) |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | descriptive | regime I, N 9.2: ρ_G +0.11 / +0.14 (bge / gte; 5 pair(s) ≤ 10 active days) |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | descriptive | regime I, N 8.4: ρ_G +0.08 / +0.00 (bge / gte; 3 pair(s) ≤ 10 active days) |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | descriptive | regime I, N 10.0: ρ_G +0.07 / -0.04 (bge / gte; 3 pair(s) ≤ 10 active days) |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | descriptive | regime I, N 10.0: ρ_G -0.10 / -0.15 (bge / gte; 3 pair(s) ≤ 10 active days) |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | descriptive | regime I, N 9.8: ρ_G +0.07 / +0.04 (bge / gte; 4 pair(s) ≤ 10 active days) |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | descriptive | regime I, N 10.0: ρ_G +0.12 / -0.04 (bge / gte; 4 pair(s) ≤ 10 active days) |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | descriptive | regime I, N 10.0: ρ_G +0.01 / -0.13 (bge / gte; 3 pair(s) ≤ 10 active days) |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | regime I, N 11.0: ρ_G +0.32 / +0.10 (bge / gte; 1 pair(s) ≤ 10 active days) |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | descriptive | regime I, N 11.2: ρ_G +0.32 / +0.10 (bge / gte; 1 pair(s) ≤ 10 active days) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | descriptive | regime III, N 12.0: ρ_G +0.15 / +0.06 (bge / gte; 3 pair(s) ≤ 10 active days) |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | regime III, N 12.0: ρ_G +0.11 / +0.09 (bge / gte; 3 pair(s) ≤ 10 active days) |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | descriptive | regime III, N 12.4: ρ_G +0.01 / -0.00 (bge / gte; 7 pair(s) ≤ 10 active days) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | regime III, N 14.8: ρ_G +0.01 / +0.04 (bge / gte; 4 pair(s) ≤ 10 active days) |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | descriptive | regime III, N 15.0: ρ_G -0.04 / +0.04 (bge / gte; 4 pair(s) ≤ 10 active days) |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | descriptive | regime III, N 15.0: ρ_G -0.15 / -0.12 (bge / gte; 3 pair(s) ≤ 10 active days) |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | regime III, N 15.6: ρ_G -0.04 / -0.03 (bge / gte; 3 pair(s) ≤ 10 active days) |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | descriptive | regime III, N 16.8: ρ_G +0.07 / +0.11 (bge / gte; 1 pair(s) ≤ 10 active days) |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | n/a | #51 common mode φ = L(1)/L(0⁺) 0.54 / 0.54; NE32 Δφ −0.09 / −0.38 (placebo pct 0.37 / 0.03); NE33 +0.44 / −0.07 (0.86 / 0.27); planted power ≤ 0.21: inconclusive |
| [NE27](goalperiod-subhypotheses/NE27/README.md) | native | descriptive | Δln k +0.41 [−3.37, 4.19] / +0.38 [−1.60, 2.36] vs magnet −0.55; drift-world percentile 0.53 / 0.53; power 0.06 / 0.09: inconclusive |
| local: regime I span | replication | descriptive (inconclusive, unpowered) | α_k +0.40 [−1.62, 2.41] / +1.22 [−1.45, 3.88]; LR magnet/drift 0.90 / 0.65; power 0.00 |
| local: regime III span | replication | descriptive | α_k +0.33 [−9.4, 10.0] / −0.54 [−7.3, 6.2]; no information |

## Outcome vs prediction
*Run 2026-10-04 21:58–22:03 UTC (`analysis/replication.py`, `analysis/natives.py`, then the labelled `analysis/posthoc.py`). Non-holdout only. Decision rules: the card's, with Amendments A1–A3.*

| Prediction | Observed (bge / gte) | Verdict |
| --- | --- | --- |
| P1 α_k CI excludes 0 and includes −1, both models | α_k **+0.40 [−1.62, 2.41] / +1.22 [−1.45, 3.88]** (delete-one-goal jackknife, 24 goals); k_6 0.044 / 0.087 per active day (τ_6 23 / 12 active days); A 0.37 / 0.49 | **inconclusive** (unpowered, A3: power 0.00) |
| P1 kill: CI includes 0 and excludes −0.5 | both CIs include −0.5 | does not fire (and would not count, A3) |
| A3 evidence: percentile in D / M, LR p(α̂ \| M)/p(α̂ \| D) | percentiles D 0.49 / 0.92, M 0.62 / 0.93; LR **0.90 / 0.65** | the data barely move the odds (toward drift, ×0.65–0.90) |
| A3(c) artifact flag: α̂ above D's 97.5th percentile | +0.40 / +1.22 (D 97.5th ≈ +1.8 / +1.9) | not flagged |
| P2 NE27: Δln k < D q05 and near −0.55 | **+0.41 / +0.38** (D q05 −1.85 / −1.34; magnet −0.55); placebo breaks −0.24, −0.46 / +1.38, +2.62 | **inconclusive** (power 0.06 / 0.09); point estimate has the drift sign |
| P3 subsets matter (V3 more negative than V1) | V3 +0.32 / +1.11 vs V1 +0.40 / +1.22 | weakly yes (−0.1); the full roster is not the impostor here |
| P4 robustness (sign kept, inside V1 CI) | V6 members +0.33 / +1.10; V7 calendar +0.36 / +1.18; V9 white32 +0.47 / +0.71; style_resid_period +0.13 / +0.18; V8 no Gemini +1.79 / **+3.18 [0.62, 5.74]**; V2 −0.13 / −0.75; V4 −0.84 / +1.41; V5 −3.86 / −0.53 | sign not stable (V2, V4, V5 flip; all are noisier, SD 1.2–2.7 in the synthetic) |
| N2 #51 joins: Δφ > 0, placebo pct ≥ 0.90 | NE32 −0.09 / −0.38 (0.37 / 0.03); NE33 +0.44 / −0.07 (0.86 / 0.27) | **inconclusive** (planted power ≤ 0.21) |
| Regime III (descriptive) | +0.33 [−9.4, 10.0] / −0.54 [−7.3, 6.2] | no information |

**Overall (pre-registered reading with A3): inconclusive.** P1 and P2 are unpowered, so neither a pass nor a kill could decide. The real estimates sit in the overlap of the drift and magnet worlds.

## Post hoc checks (labelled; written after the replication result, `analysis/posthoc.py`)
- **PH1, era drop of the near-lag similarity.** The per-period points ρ_G fall with N (Spearman −0.30, p 0.15 / −0.61, p 0.002; 24 periods). Mean ρ_G is 0.25 ± 0.04 / 0.28 ± 0.04 in the 15 periods with N_G < 8 (#2–#19, May–Oct 2025) and 0.11 ± 0.05 / 0.00 ± 0.03 in the 9 periods with N_G ≥ 8 (#20–#31, mid-Nov 2025–Feb 2026). Contrast d_ρ = −0.14 / −0.28. Calibration on the real panel (150 replicates each): drift world D median −0.02 (real percentile 0.11 / **0.00**), magnet world M median −0.01 (0.09 / **0.01**), era-collapse world E (slow mode planted only in N < 8 blocks) median −0.14 (0.52 / 0.07). The lag profile agrees: pairs within the N ≥ 8 class have s̃ 0.07 / −0.03 at ≤ 10 active days, against 0.27–0.30 in the two smaller classes.
- Reading: in gte, and weakly in bge, the slow mode is strong in the small-village era and weak or absent after mid-November 2025. Neither a constant-rate drift nor magnet inertia produces that in the synthetic. N is collinear with calendar time here, so "N ≥ 8" and "after 2025-11-17" (and NE08, 12-10, inside the late era) cannot be separated.

## Results
**1. The finite-size test is not identifiable in one village.** The synthetic on the real regime-I panel shows that the HH's estimator moves by only −0.2 for a true slope change of −1, with SD 0.7. Its power to exclude 0 under the magnet is 0.00 in both models. Even the noiseless planted slow-mode path gives α̂ with SD 0.45. Regime I holds one trajectory of about 13 decay times, and its N takes three levels (4, 6–8, 8–12) in calendar order. A 1/N law in a timescale needs several villages of different size, or a much longer record.

**2. The real estimates are uninformative, as A3 predicted.** α_k = +0.40 [−1.62, 2.41] (bge) and +1.22 [−1.45, 3.88] (gte). Both sit inside the drift and the magnet distributions; the likelihood ratio magnet/drift is 0.90 and 0.65. The decay time at N = 6 is 23 / 12 active days (k_6 0.044 / 0.087), consistent with H81's τ_u ≈ 23–28 calendar days.

**3. The natural experiments have no power either.** NE27 (N 4 → 7 in one day): Δln k = +0.41 / +0.38 against a magnet value of −0.55; the CIs span ±2–4 and the drift-world test has power 0.06–0.09. #51 joins (NE32, NE33): N rises only ×1.1–1.2; planted power ≤ 0.21. The #51 cross-agent common mode keeps 54% of its equal-time alignment after one active day (φ 0.54 in both models, τ ≈ 1.6 active days), in line with H81's ≈ 3-day estimate.

**4. Post hoc: the slow mode belongs to the small-village era.** The near-lag culture similarity is 0.25–0.28 before mid-November 2025 (N ≤ 7.6) and 0.00–0.11 after (N 8.4–11.2). The gte drop is outside the drift and magnet worlds (percentile 0.00 / 0.01) and matches a world in which the mode stops. This is post hoc, one model is marginal (bge percentile 0.09–0.11), and N is confounded with date.

**What this means for H81's exogenous-drift rival (R1).** H106 cannot weigh against R1 through N-scaling: the 1/N signature is not measurable in this record. Two things do bear on R1. (a) The NE27 point estimates have the drift sign (no slowdown when N jumps 4 → 7), but with power 0.06–0.09 that is no evidence. (b) The post hoc era result says the regime-I slow mode is concentrated in May–October 2025 and weak or gone from mid-November. A constant-rate outside drift does not do that; an outside drift that stopped, a scaffold change (NE08, 2025-12-10, falls inside the late era), or a record channel that weakened as each agent's talk share fell (H85: N^−0.89) all could. H81 round 2 should split its slow-mode contrast at 2025-11-17 and at NE08 and run its drift probe and carrier test separately on each side.

Figures: `figures/summary_obs.pdf` ((a) lag profile by N class; (b) real α_k with CI against the drift and magnet distributions), `figures/summary_obsb.pdf` ((a) ρ_G vs N_G per period; (b) NE27 real vs drift and magnet). Data: `data/processed/H106-slow-mode-finite-size/` (`synthetic/`, `replication/`, `natives/`, `posthoc/`, `confirm_dryrun*/`; 0.7 MB). Estimates: 138 rows in `per_period_estimates` (hypothesis H106).

## Faithfulness scorecard
*Round 1, 2026-10-04.*
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 exogenous drift (α 0); R2 conserved-flux record (α ≈ 0); R3 member-carried persistence; R4 estimation noise; R5 sampling depth; R6 calendar trend.
**Locked holdout used for confirmation:** none (`analysis/confirm.py` frozen and dry-run, **not run**; C2 targets #9, #14, #15 vs #22, #28, #29).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | N (active population), active-day clock, culture vectors and reliabilities come from shared tables; assumptions (fixed σ_u, rate law in N only) listed; both models; regime invariance untestable (regime III has no information). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | OU-like decay in the N < 8 classes (s̃ 0.27 → 0.09 → 0.06 → −0.03 over 0–80 active days); stationarity of the amplitude fails post hoc (era drop). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | Magnet and drift are not separable (LR 0.65–0.90). |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The NE27 jump size (−0.55) is unfitted, but the test has power ≤ 0.09; point estimate +0.4. |
| E interventional | predicts the change across a natural experiment | 0 | NE27 and #51 joins unpowered (≤ 0.21). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 0 | Done before real data, and it shows α_k is not recoverable on this panel (power 0.00; oracle SD 0.45). |
| G ground truth | agrees with known structure | 0 | No labelled ground truth for inertia. |
| H comparative | beats the named rivals | 0 | R1/R2 vs magnet undecided; R4 is not an impostor here (V3 ≈ V1); R3 and R5 give the same +0.4 shift as drift. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Regime III uninformative; holdout not run. |

## Confirmatory predictions (written 2026-10-04 22:05 UTC after round 1, before any holdout use; `analysis/confirm.py`, dry-run only, **not run**)
Targets: regime-I held-out goals #9, #14, #15 (N < 8) and #22, #28, #29 (N ≥ 8), as new blocks in the full regime-I panel.
- **C1 (HH, descriptive):** α_k on the full panel is uninformative: LR magnet/drift within [1/3, 3]. Holdout adds six goals to the same single trajectory, so this is not a test of HH335; running C1 alone is not worth a holdout use.
- **C2 (post hoc era result):** d_ρ (held-out N ≥ 8 periods minus held-out N < 8 periods) < 0 and below the drift-world 5th percentile on the same panel, in both models.
- Dry runs: stand-ins #10, #13, #17 vs #23, #26, #30 (explored periods): C2 passes in gte and not in bge (d_ρ −0.25 / −0.06 vs D q05 −0.16 / −0.17, 20 replicates); the in-memory build path (`--exercise-build`) reproduces the shared-build α to 1e-7.
- **Reuse disclosure:** H81's frozen confirm uses the same held-out regime-I goals and the same culture-residual family (D_adjg, D_adj on new pairs); H20 and H54 target the same goals with day-level content statistics. C2 is a different statistic (an era contrast of near-lag similarity), but it reads the same blocks: coordinate with H81 before either runs, or fold C2 into H81's confirm.

## Caveats
- **N is collinear with calendar time in regime I.** Three N levels in date order; model generations, NE03, NE04 and NE08 fall inside the span.
- **The synthetic assumes a stationary σ_u and one OU mode.** The real amplitude changes by era (PH1), which the worlds D and M do not contain.
- **The estimator is biased (+0.4) and attenuated (×0.2)** on this panel; the jackknife CI covers the truth in 87–99% of worlds, so CIs are honest but wide.
- **Per-period ρ_G rests on 1–11 pairs** and uses neighbours in other goals, so adjacent periods share pairs.
- **#51 windows are 2–6 days**; φ in short windows is noisy.
- The era result is post hoc, in one model clearly and one marginally.

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **Where round 1 went sideways:** the HH treated the decay rate as a per-block observable. One village gives one trajectory of the slow mode, so a rate-vs-N slope compares two pieces of one path. No estimator fixes that (oracle SD 0.45).
- **What the direction is really after:** whether the slow mode has inertia that scales with the number of carriers (endogenous) or not (outside drift).
- **H106-R1. Era split (feeds H81 round 2).** Re-run H81's D_adjg / D_adj and the drift probe separately before and after 2025-11-17 and around NE08, with S0 calibrations per era. If the mode exists only early, ask what changed: N ≥ 8, per-agent talk share (H85), or a scaffold step.
- **H106-R2. Many trajectories instead of one.** Rooms in regime III (#38, #44: rooms of different size on the same days) give parallel content trajectories; a room-level slow mode with τ vs room size is a cross-sectional finite-size test (links to H108, Goldstone room wandering).
- **H106-R3. Transfer (Q7).** The 1/N law is testable across villages of different N (other swarm logs), not inside one.

**Claim that stands:** In regime I (24 goals, N 4–12) the slow mode's finite-size exponent is not identifiable: α_k = +0.40 [−1.62, 2.41] (bge) and +1.22 [−1.45, 3.88] (gte), with power 0.00 to exclude 0 under the magnet's α = −1 and SD 0.45 even for a noiseless path; the data move the magnet:drift odds by ×0.65–0.90. Excluded: the post hoc era drop (d_ρ −0.14 / −0.28; unreplicated, one model marginal), NE27 and #51 joins (unpowered), the V8 gte variant (one variant).

## Notes
- 2026-10-04: H106 uses `infra/shared/culture_vectors.py` with `personal_vectors(method="fe")` (the two-way agent + goal fixed effect, H81 Amendment A1), not the leave-goals-out mean (`prior_mean`, H82). H81's simulator and residual code are re-implemented in `analysis/h106lib.py` (no import from H81's folder; STANDARDS §8). A suggested shared-file change is to move them into `culture_vectors.py`.
- 2026-10-04: timestamps are UTC clock times from the shell (`date -u`) and file modification times: card 21:27, period folders 21:39, A1/A2 21:41, synthetic 21:31–21:57, A3 21:58, replication and natives 21:58–21:59, post hoc 22:01, confirm dry runs 22:03.
- 2026-10-04: real-data runs use 200 subset draws per block; the synthetic used 50 (Monte Carlo noise only; the jackknife CI is computed on the real data). One process at a time, ≤ 2 workers for the synthetic, BLAS/polars at 2 threads.
- 2026-10-04: `write_estimates` rejected the first NE27 row because its first/last day span #9 (held out); it is now written as a `local:NE27` span with `holdout = False` and the window stated in the notes.
