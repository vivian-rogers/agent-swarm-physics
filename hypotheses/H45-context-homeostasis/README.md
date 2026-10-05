# H45: Context homeostasis: each agent keeps its context near a set point

**Status:** round 1 done (2026-10-04; exploratory, non-holdout). **Refuted as posed: the room share of an agent's context is not regulated.** It follows inflow as passive accumulation predicts (regulation index RI ≤ 0.22 in 32/32 periods, pooled 0.02 ± 0.01; NE42 and the #51 N sweep move set points at 1.06 and 0.90 × the passive slope). After forced erasures (NE41, 21k) agents talk *less* (k-adjusted 0.74 [0.69, 0.80], τ ≈ 10 calls) and reply more per talk, with replies per call unchanged: no import overshoot. Reply-based dilution is steeper than H18's (β pooled 0.82; 0.98 in regime III, about one reply per talk), and engagement falls with own content, not with the room share (post hoc: context competition, HH158). The scaffold sets the composition: 41-call resets, a bounded chat-mode window (NE03), a 200-event cap that binds in 0.05% of calls. Predictions and the synthetic validation (axis F) came before real data; amendments A1–A5 are dated. `confirm.py` written, dry-run only, **not run**.
**Fields:** control theory / physics of life (homeostasis, nonequilibrium steady states), information theory, dynamics
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (viability, maintained states); [Bartlett et al. 2025](../../literature/bartlett-2025-physics-of-life-information-roadmap.md) (physics of life: homeostasis as regulated information import); [Sowinski et al. 2023](../../literature/sowinski-2023-semantic-information-resource-gathering-agents.md) (plateau-then-collapse under scrambling)
**Definitions used** (`physics-models/DEFINITIONS.md`): Regime; Memory state; Exposure (turn read-out) (implemented by the DQ1 context ledger); Context fill (H30: `ctx_pos`); Interaction (broadcast). New named variants, defined under "Operational definitions" and proposed for DEFINITIONS.md: **context segment**, **room tokens (calibrated)**, **context share (room, token-calibrated)**, **own content**, **regulation index**, **engagement (reply parent, pending)**.
**From:** HH166 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/04-semantic-information/`, `physics-models/05-replicator-dissipation/` (as the import/degradation bookkeeping), plus a set-point controller defined below
**Data inputs (shared tables first):** DQ1 context ledger (`call_windows`, `context_ledger_turns`, `context_ledger_items`), DQ2 `reply_pairs` (`pair_set = cand`, `parent`), `actions` / `events_core` token fields, `chat_core`, `roster`, `period_units`. Not used: `activity_bins` (join bug, 2026-10-04) and the ledger's `outage_s` / `outage_off` (derived from it).

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H45 has no round-1b section; round 1 already ran on the corrected inputs.*

**Question served:** Q4. The card asks whether agents regulate how much of their context window holds room information.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | no | The share is a per-call composition inside one agent's segment; no synchrony statistic. | n/a |
| Exogenous field (kickoff/goal/operator) | partly | RI is a within-agent × period slope at fixed position. NE42 is goal-confounded (Caveats). The pooled γ_W < 0 is confounded with task phase. Close γ with DQ3 behavior-state controls (R1). | partly |
| Shared model priors | partly | Lab share of set-point variance tested against a label permutation (P7: η² 0.14, p 0.41); agent fixed effects throughout. | removed |
| Contemporaneous convergence | no | Engagement counts replies to items already read (pending set); no influence claim. | n/a |

**Inputs:** round 1 uses the context ledger, DQ2 replies and measured prompt tokens. It never reads `activity_bins` or the ledger's `outage_*` columns. Still old: none of the listed inputs. Embeddings, work and failures are not inputs.

**Two layers:** 31 replication folders. Native tests: 4 (`G51` N sweep, `NE41`, `NE42`, `NE03`), all failed.

**Confirm script:** `analysis/confirm.py` exists, dry-run only, built on the corrected inputs (C1–C6). No re-freeze needed.

## Question
Do agents regulate the share of their context taken by room messages around a set point, reading less per message when the room floods (the k^−0.6 dilution as a homeostat) and overshooting, then returning, after an erasure?

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator on every eligible goal period (comparable phase-diagram points). Period README role: `replication`.
- **Period-native tests:** 2–4 goal periods (or NEs) whose setup gives special leverage for this question, each with its own observable, null, ground truth or intervention, its own dated prediction, and period-specific tooling where needed. Period README role: `native`.

## What can and cannot be regulated (written before data)
The scaffold pushes every unseen room event into the next call's context (DQ1), so an agent cannot refuse to receive room messages. In computer-use mode a context segment accumulates until a reset (the forced 41-call consolidation, NE41, or a voluntary one). The room share of a call's context is therefore set by:
- the **inflow** of room content per call (other agents' traffic times the agent's call interval);
- the **own content** the agent adds per call (its outputs, tool results, screenshots);
- **segment length** (when the agent consolidates voluntarily; the 41-call cap otherwise);
- the **scaffold**: what a reset re-shows (memory, a room-state snapshot since 2026-02-27), the 200-event cap per call (NE22, from 2026-06-11), and in regime-I/II chat mode a recent-chat window with a fetch limit (NE03, 2025-08-20).

An agent can regulate the share only through its own content, its call cadence and its consolidation timing. "Reading less per message" is an attention allocation (engagement), not a change of context composition. H45 is tested on both: the context share (does it hold a band?) and engagement (does it depend on the share, as a controller's output would?).

## Model
**From:** `physics-models/04-semantic-information` (an agent maintaining a nonequilibrium state by importing information) and `05-replicator-dissipation` (import vs degradation bookkeeping: room content enters per call and is degraded at resets). H45 adds a **set-point controller** for the room share.

**State in one context segment** (calls j = 1, 2, … after a reset): room content R_j = Σ_{j′≤j} r_{j′} (calibrated room tokens of the new items), own content W_j = P_j − R_j (P = prompt tokens), share s_j = R_j / P_j.

**Three agent classes (the synthetic validation runs all three, plus one rival, on real call schedules and message streams):**
1. **Set-point controller (H45):** own content per call responds to the share, g_j = g₀ exp(κ_W (s_{j−1} − s*)/s*); voluntary consolidation hazard rises when s_j exceeds a ceiling; per-item engagement u_j = u₀ (s*/s_j)^{κ_e}. Dilution in k arises because a large batch raises s_j. After a reset s is low, so engagement overshoots and relaxes as s rebuilds.
2. **Passive accumulation:** g_j = g₀ (agent constant with noise); consolidation at the 41-call cap or at a constant voluntary hazard; per-item engagement u = u₀ k^−0.6 (H18's dilution, but stateless).
3. **Scaffold-capped:** the context is a sliding window of the last 15 calls (old content truncated by the scaffold); u = u₀ k^−0.6. The share is bounded by the window, not by the agent.
4. **Context competition (rival for the engagement test; HH158):** passive context, u = u₀ k^−0.6 (P_j / P̄)^−1: attention falls with total context, not with the room share.

**Signatures that separate them:**

| Statistic | Controller | Passive | Scaffold-capped | Competition |
| --- | --- | --- | --- | --- |
| share elasticity ε = d ln s / d ln λ at fixed position (λ = inflow per call) | ≈ 0 | ≈ 1 − s̄ | ≈ 1 − s̄ (window on both R and W) | ≈ 1 − s̄ |
| regulation index RI = 1 − ε/(1 − s̄) | ≈ 1 (0.38–0.49 for the synthetic's moderate gain) | ≈ 0 | ≈ 0 | ≈ 0 |
| own-content response η_W = d ln W / d ln λ | ≈ 1 | ≈ 0 | ≈ 0 | ≈ 0 |
| P growth through a segment, P(j 30–35)/P(j 8–12) | > 1 | > 1 | ≈ 1 | > 1 |
| engagement on old room content γ_R, own content γ_W (fixed k, position) | γ_R < 0, γ_W > 0 | 0, 0 | 0, 0 | γ_R < 0, γ_W < 0 |
| k-adjusted engagement after a forced reset, calls 1–3 vs 20–40 | overshoot > 1 | ≈ 1 | ≈ 1 | > 1 |

## Data scheme (`scheme/`)
- **Script:** `scheme/build.py` (one pass, all non-holdout days; the holdout is dropped with the ledger's calendar flag, asserted equal to `common.holdout_mask`).
- **Inputs:** `call_windows` + `context_ledger_turns` (one row per model call: new items by kind, `k_new`, `chars_new`, `n_ev`, `k_since_talk`, `ctx_pos`, reset flags, `cap_hit`, `n_omitted`); `actions` (`tok_in`, `tok_cache_read`, `tok_cache_write`) and `events_core.tokens_in`; `chat_core` (talk messages → calls); `context_ledger_items` (who received which item, at which call); `reply_pairs` (`pair_set = cand`, `parent`); `roster`; `period_units`.
- **Transform:**
  1. **P per call:** max total input over the call's action rows (Anthropic: input + cache read + cache write; Google: input, already inclusive), else the call's agent-event `tokens_in`. Structural check (2026-10-04): Anthropic event counts are uncached-only outside chat mode (median 10 vs 48k on the same call's action rows), so they are dropped there. Coverage of cu calls: Anthropic and Google ≈ 100% (action rows); other labs 3–26% (event calls only: talk, pause, search, consolidate).
  2. **Segments:** an agent's cu-mode receiving calls between resets (`ctx_pos` restarts at 1); each segment's opening and closing reset type (forced = the 41-call cap, NE41; voluntary consolidation; session marker; next day).
  3. **Cumulative room content in the segment:** Σ `k_new`, Σ `chars_new`, Σ other-room events (`n_ev − k_new`).
  4. **Engagement:** a talk call's message → its DQ2 reply parent (p_reply ≥ 0.5, visible candidates) → whether that parent is among the items received since the agent's previous talk call (`eng_pending`), or any parent (`eng_any`); per receiving call, how many of its new items the recipient later replies to.
- **Output:** `data/processed/H45-context-homeostasis/calls.parquet` (1.89M calls, 48 MB, no text) with `_provenance.json`; per-period results in `G<NN>/`, natives in `NE<NN>/`, synthetic in `synthetic/`.
- **Regimes covered:** I (cu sessions + chat mode), II, III; non-holdout days only.

### Operational definitions (written 2026-10-04, before any real-data outcome statistic)
- **Context segment:** a maximal run of one agent's cu-mode receiving calls between context resets (`ctx_pos` = 1 opens one). Position j = `ctx_pos` (= H30's context fill).
- **Room tokens (calibrated):** r_c = a_L·k_new + b_L·chars_new + e_L·n_oev, with lab-L coefficients from a robust (Huber) regression of the within-segment prompt growth ΔP_c on the call's new items, characters and other room events, with agent intercepts (own-content growth), on consecutive Anthropic / Google calls with action-row tokens. Labs without action-row tokens use the mean of the Anthropic and Google coefficients (sensitivity: × 0.5 and × 2). Fitted before any outcome statistic, as part of the ruler.
- **Context share (room, token-calibrated):** s_c = R_c / P_c, R_c = Σ r over the segment's calls up to and including c. It omits the room snapshot a reset re-shows and `search_history` results (both counted in P, not R), so it is a lower bound; the reset snapshot is measured separately (NE41).
- **Own content:** W_c = P_c − R_c.
- **Inflow per call:** λ_σ = mean over the segment's band calls of R_c / j.
- **Set point s\*:** the median of s_c over positions j ∈ [15, 35] for one agent in one goal period (the band avoids the reset transient and the cap).
- **Regulation index:** RI = 1 − ε/(1 − s̄), with ε the within-agent × period slope of ln s̄_σ (band mean share per segment) on ln λ_σ, controlling mean band position. Passive accumulation gives ε = 1 − s̄ exactly (s = λj/(W + λj)), so RI = 0; perfect regulation gives RI = 1. Identity: at fixed position RI = η_W, the elasticity of own content to inflow, so a share can only be held by changing own content.
- **Engagement (reply parent, pending):** at a talk call, 1 if its message's DQ2 parent is among the items received since the agent's previous talk call. Per-item exponent β from P(E1 = 1) = 1 − exp(−θ_{agent-day} k^{1−β}), k = `k_since_talk` (H18's model aggregated over items; β = 0 constant per-item uptake, β = 1 fixed budget).
- **Talk propensity (E2):** P(a cu receiving call talks).

## Observables
1. **Set point and band:** s\* per agent and period; the distribution of s_c; the coefficient of variation of segment band shares vs the passive synthetic's on the same streams.
2. **Regulation (test a):** ε, RI and η_W per period; segment-length lever (voluntary consolidations): slope of ln L_σ on ln λ_σ.
3. **Engagement (test b):** β per period (E1); share dependence γ_R (old room content in context, excluding the pending batch), γ_W (own content) from a linear probability model with agent × day and position-band fixed effects, controlling ln(1 + k).
4. **Post-erasure dynamics (test c):** after forced resets (exogenous timing), position profiles of s_j, E2 and E1, k-adjusted (ln(1 + k_new) and agent-day fixed effects), relative to j ∈ [20, 40]; overshoot ratio over j ∈ [1, 3]; relaxation τ (calls) from an exponential fit; the same after voluntary resets.
5. **Heterogeneity (test d):** lab, agent and period shares of the variance of agent-period s\*, with a lab-label permutation; regime I cu sessions vs regime III; cap-hit calls.
6. **Scaffold rival:** P growth through a segment (truncation plateau or not); reset snapshot (P at j = 1 vs room chars posted in the 30 min before the reset); chat-mode P vs messages earlier that day around NE03.

## Null / baseline
- **Passive accumulation** is the primary null: ε = 1 − s̄, RI = η_W = 0, no share dependence of engagement, no k-adjusted overshoot. It is also run as a synthetic agent on each period's real streams, so every statistic has a passive reference computed on the same calls.
- **Scaffold-capped** (truncation) and **context competition** are the rivals that can fake regulation (bounded share) or state dependence (engagement falls with context).
- Day-block bootstrap (B = 200) for all CIs; agent-label permutation for the lab share.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** passive accumulation; scaffold-capped context (truncation, fixed caps); context competition (HH158).
**Locked holdout used for confirmation:** none (planned in `analysis/confirm.py`, written and dry-run only: #45, #46, #47, #49, #50 scored; #43, #48 reported; the #51 tail 51m; NE22 within #46).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Share = calibrated room tokens (ledger items: ≈ 50 tokens per message + 0.3 per character + 116–163 per other room event; Anthropic and Google fits agree) over measured prompt tokens. Assumptions listed (R omits `search_history` results and any reset snapshot; the latter measured ≈ 0, NE41). Not invariant: dense prompt tokens only for Anthropic and Google; other labs only on event calls with a borrowed calibration (× 0.5 / × 2 checked); chat mode is not measurable on the same footing. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Within-segment accumulation confirmed (P(j 30–35)/P(j 8–12) 1.86–2.45 in 32/32; no truncation plateau); band positions 15–35 and 8–20 agree; k-adjustment checked against the passive synthetic. No Markov-order or update-order audit. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | The controller does not beat passive accumulation anywhere: RI CI upper bound < 0.5 in 32/32 periods (pooled 0.02 ± 0.01); CV ratio 0.84–1.32 (median 0.99) vs ≤ 0.5 predicted. Passive fits; no held-out likelihood. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | Every controller signature failed: no band (CV ratio ≈ 1), no own-content response (η_W −0.09 to 0.19), no γ_W > 0 (pooled −0.10 [−0.16, −0.06]), no post-erasure overshoot (undershoot 0.74), no hump in the share trajectory. Passive's unfitted predictions (ε = 1 − s̄, monotone share) hold. |
| E interventional | predicts the change across a natural experiment | 0 | Four interventions, all against H45: NE41 (talk dip, not import burst), NE42 (set point follows the merge flood at 1.06 × passive), #51 roster steps (0.90 × passive), NE03 (no visible change; chat-mode prompts already bounded). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Four classes on real schedules (6 units × 20 reps): RI, η_W, CV ratio, P growth, lever sign and β place every class correctly in ≥ 95%; the overshoot needs its CI (passive spread ±0.15); γ_R/γ_W are **not identified** per period. RI robust to 7 preprocessing variants (medians −0.04 to 0.06; 32/32 below 0.5 in each). |
| G ground truth | agrees with known structure | 1 | Known scaffold structure recovered: the 41-call cap, roll-over of arrivals during the memory call (k_new 5.8 at j = 1 vs ≈ 0.5), the 200-event cap firing only above 200 events (after pauses), bounded chat-mode prompts (≈ 8–10k tokens). These validate the instrument, not the controller. |
| H comparative | beats the named rivals | 0 | Passive accumulation beats the controller on every composition statistic; context competition fits the engagement pattern better post hoc (γ_W < 0; γ_R < 0 once momentum is controlled); the scaffold-capped class is rejected for computer-use mode (P keeps growing) but describes chat mode (NE03). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | The claim holds in none of 32 periods across three regimes (the negative transfers perfectly). Holdout not used. |

## Prediction
*Written 2026-10-04 06:21 UTC, before running any outcome analysis on real data. Looked at before this: schemas, row counts, token-field coverage and magnitudes by lab, regime and call kind (to fix the P rule), segment counts per goal period, talk-message mapping coverage, the CHANGELOG around NE03. No share, engagement, or k relation was computed.*

**Eligible periods (replication layer):** non-holdout goal periods with ≥ 3 agents having ≥ 30 cu-mode segments with prompt tokens: #4, #5, #6, #8, #10–#13, #16–#21, #23–#27, #30, #31, #33, #35–#42, #44, #51 (32 periods). Tests needing cu-mode talk (γ_R, γ_W) run on regimes II–III (#33 on); forced-erasure tests on #36–#51 (regime III).

**Verdict rule per period (fixed now):** *supported* if RI ≥ 0.5 with the 95% CI excluding 0 and, where testable, γ_R < 0 and γ_W > 0 (both CIs excluding 0); *failed* if the RI CI's upper bound is below 0.5 and the engagement test does not show the controller's sign pattern; *mixed* otherwise.

| # | Prediction (H45 as stated) | Counts against | Credence |
| --- | --- | --- | --- |
| P1 (primary, regulation) | RI ≥ 0.5 (CI excludes 0) in ≥ 2/3 of eligible periods; η_W agrees with RI within 0.2 | RI CI upper < 0.5 in ≥ 2/3: the share tracks inflow as passive accumulation predicts | 15% |
| P2 (consolidation lever) | among segments that end in a voluntary consolidation, ln L_σ falls with ln λ_σ (slope ≤ −0.3, CI excludes 0) in ≥ 2/3 of regime-III periods | slope ≈ 0 | 25% |
| P3 (band) | CV of segment band shares ≤ 0.5 × the passive synthetic's CV on the same streams, in ≥ 2/3 of periods | ratio ≈ 1 | 15% |
| P4 (dilution reproduced) | β (E1, reply-based) ∈ [0.4, 0.9] with CI excluding 0 in ≥ 70% of eligible periods; pooled within ±0.2 of H18's 0.63 | β ≈ 0, or ≈ 1 everywhere | 60% |
| P5 (dilution is a homeostat; discriminating) | γ_R < 0 and γ_W > 0 (both CIs exclude 0) in ≥ 50% of regime II–III periods | γ_R ≈ 0 (stateless dilution), or γ_W < 0 (context competition) | 15% |
| P6 (post-erasure overshoot) | after forced resets, k-adjusted E2 in calls 1–3 exceeds the j 20–40 baseline by ≥ 20%, relaxing with τ ≤ 10 calls, in ≥ 2/3 of regime-III periods | no excess once k is adjusted | 35% |
| P7 (heterogeneity) | lab explains ≥ 30% of the variance of agent-period s\*, above the permutation 95th percentile; regime-I cu-session s\* differs from regime III by ≥ × 1.5 | lab share at chance | 60% |
| P8 (scaffold rival, cu mode) | no truncation plateau: median P(j 30–35)/P(j 8–12) ≥ 1.3 in every regime-III period | ratio ≈ 1 (the scaffold caps the context) | 70% |
| P9 (200-event cap) | binds in < 0.1% of non-holdout calls and does not set any period's s\* | cap-hit calls common | 90% |

**My expectation, stated before data:** the share follows inflow (RI near 0) and the dilution exponent replicates as a stateless attention property; the homeostasis claim fails on context composition. The post-erasure question is open.

**Native tests (each with its own README and dated prediction):**
- **NE41 forced erasures** (regime III, thousands of events; exogenous timing): the overshoot and relaxation of P6 per period and pooled; forced vs voluntary; the reset snapshot (does P at j = 1 rise with the room volume of the 30 min before the reset? a scaffold-set floor of the share).
- **NE42 merge A-B-A** (#39 → #40 → #41, fixed roster): inflow per call jumps at the merge and falls at the split. Leak φ = Δ ln s\* / ((1 − s̄) Δ ln λ): passive φ ≈ 1, homeostat φ ≈ 0.
- **G51 N sweep** (units 51a–51l, N 21 → 32 at fixed goal and room): within-agent slope of ln s\* on ln λ across units vs 1 − s̄; plus the 200-event cap hits (descriptive).
- **NE03 chat fetch limit** (2025-08-20; the scaffold rival in its purest form): in chat mode the scaffold rebuilds the prompt from recent chat. After NE03, chat-mode P should stop growing with the day's message count (a scaffold ceiling); before, it should grow.
- NE32 (GPT-5.6 trio in isolated rooms) is not run: three OpenAI agents have prompt tokens only on event calls (≈ 9%), for one to two days.

## Synthetic validation (axis F)
*Design written 2026-10-04 06:21 UTC, before real-data outcomes.* `analysis/synthetic.py` runs the four agent classes on the real call schedules and room streams of G38, G41 and four #51 units (real `k_new`, `chars_new`, other-room events, call order, talk calls, day boundaries; resets re-simulated per class), with agent-level base context and own-content growth set to each real agent's median scale. Each class is fed to the same estimators as the real data (RI, η_W, the segment-length lever, CV ratio, β, γ_R/γ_W, the k-adjusted overshoot, P growth). Pass criterion: every statistic places each class in its column of the signature table at real counts, in ≥ 80% of 20 replicates; the passive class gives RI within ±0.25 of 0 and overshoot within ±0.15 of 1.

### Synthetic result (run 2026-10-04 ~06:27–06:45 UTC, before any real-data outcome)
`analysis/synthetic.py`, 6 units (38a, 41, 51c, 51e, 51f, 51h) × 4 classes × 20 replicates, on real schedules and streams; pass rates in `data/processed/H45-context-homeostasis/synthetic/synthetic_passrates.json`; figure `figures/synthetic.pdf`.

| Statistic | Controller (median) | Passive | Scaffold | Competition | Placed in its column (≥ 80% of reps) |
| --- | --- | --- | --- | --- | --- |
| RI | 0.38–0.49 | 0.00–0.07 | −0.06–0.00 | 0.00–0.07 | 100% every class and unit |
| η_W | 0.38–0.49 | 0.00 | −0.10–−0.03 | 0.00 | 100% |
| CV ratio (W-permutation; 41, 51f × 5 reps) | 0.53–0.60 | 0.96–1.01 | 1.08–1.12 | 0.96–0.97 | separates; controller ≈ 0.55 at RI ≈ 0.4 |
| lever slope | −0.08 to −0.10 | 0.00 | 0.00 | 0.00 | 100% on sign; the card's −0.3 threshold is beyond the synthetic controller |
| P growth | 2.0–2.1 | 1.9–2.1 | 1.23–1.28 | 1.9–2.1 | 100% |
| β (true 0.6 for stateless classes) | 0.22–0.31 | 0.58–0.60 | 0.55–0.59 | 0.62–0.68 | ≥ 95% |
| forced-reset talk overshoot | 1.6–1.8 | 0.94–1.06 | 0.95–1.04 | 2.3–2.5 | controller, competition 100%; passive within ±0.15 in 60–100% per unit (spread, not bias) |
| γ_R < 0 and γ_W > 0 (point estimates) | 0% (38a), 50% (41), 65–85% (#51) | 15–45% | 10–25% | 0% (γ_W < 0 in 100%) | **fails**: does not separate controller from passive at single-period counts |

**Reading:** the context-composition tests (RI, η_W, CV ratio, P growth) identify the classes at village counts with wide margins. The forced-reset overshoot identifies a burst but needs its CI per period. The share-dependence test is not identified per period; it only begins to separate at #51 scale, and is confounded with competition in the smallest units.

### Amendments (2026-10-04 06:46 UTC, after the synthetic validation, before any real-data outcome statistic)
- **A1 (P2):** the segment-length lever is judged by sign: slope < 0 with the day-bootstrap CI excluding 0. The synthetic controller gives −0.08 to −0.10, never −0.3.
- **A2 (P5, verdict rule):** per-period γ_R/γ_W are reported but do not enter the per-period verdict, which uses P1 (RI) alone: supported if RI ≥ 0.5 with the CI excluding 0; failed if the CI's upper bound is < 0.5; mixed otherwise. P5 is assessed on the pooled regime-III talk calls and on G51, with day-bootstrap CIs.
- **A3 (P6):** a period meets P6 only if the overshoot is ≥ 1.2 *and* its CI's lower bound is > 1 (passive spread ±0.15 in the synthetic). The pooled NE41 estimate is the primary erasure test.
- **A4 (P3 statistic):** the band test uses a within-agent permutation of own content across the agent's segments (keeps each segment's inflow, breaks any own-content–inflow coupling) instead of a passive synthetic per period; the synthetic shows it separates controller (≈ 0.55 at RI 0.4) from passive (≈ 1).
- **A5 (signature table):** the scaffold-capped class (a 15-call window on room and own content) gives RI ≈ 0, not > 0; it is identified by P growth ≈ 1.25.

## Results by goal period
*Exploratory, non-holdout. Verdict rule (Amendment A2): P1 alone. All per-period numbers: `data/processed/H45-context-homeostasis/G<NN>/results.json`.*

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | s\* 0.128; RI -0.02 [-0.05, 0.01]; β 0.74 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | failed | s\* 0.114; RI -0.04 [-0.06, 0.01]; β 0.76 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | failed | s\* 0.069; RI -0.07 [-0.10, -0.05]; β 0.73 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | failed | s\* 0.065; RI -0.07 [-0.08, -0.05]; β 0.70 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | failed | s\* 0.057; RI 0.00 [-0.03, 0.04]; β 1.07 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | failed | s\* 0.132; RI -0.08 [-0.14, -0.02]; β 0.72 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | s\* 0.166; RI -0.07 [-0.10, -0.03]; β 0.54 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed | s\* 0.156; RI -0.03 [-0.05, -0.01]; β 0.66 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | failed | s\* 0.075; RI -0.04 [-0.07, -0.01]; β 0.71 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | failed | s\* 0.098; RI -0.07 [-0.15, 0.04]; β 0.74 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | s\* 0.105; RI -0.05 [-0.10, -0.00]; β 0.61 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | s\* 0.084; RI -0.05 [-0.08, -0.03]; β 0.60 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | failed | s\* 0.112; RI -0.02 [-0.06, 0.02]; β 0.77 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | s\* 0.099; RI 0.02 [-0.04, 0.05]; β 0.83 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | failed | s\* 0.101; RI -0.02 [-0.08, 0.05]; β 0.96 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | failed | s\* 0.087; RI 0.10 [0.02, 0.15]; β 0.84 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | failed | s\* 0.135; RI -0.05 [-0.10, 0.04]; β 0.70 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed | s\* 0.148; RI 0.00 [-0.04, 0.05]; β 0.62 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | s\* 0.101; RI 0.03 [-0.03, 0.07]; β 0.77 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | failed | s\* 0.143; RI 0.10 [0.06, 0.13]; β 0.88 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | failed | s\* 0.137; RI 0.22 [0.14, 0.28]; β 0.78 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | failed | s\* 0.169; RI 0.08 [0.01, 0.11]; β 0.92; γ_W -0.37 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | failed | s\* 0.067; RI 0.08 [0.04, 0.11]; β 0.97; γ_W -0.34 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | failed | s\* 0.061; RI 0.05 [-0.02, 0.13]; β 1.12; γ_W -0.47; talk after erasure 0.51 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | failed | s\* 0.058; RI 0.01 [-0.01, 0.07]; β 1.12; γ_W -0.30; talk after erasure 0.81 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | failed | s\* 0.051; RI 0.05 [0.02, 0.07]; β 0.97; γ_W -0.29; talk after erasure 0.69 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | failed | s\* 0.066; RI 0.13 [0.08, 0.17]; β 1.01; γ_W -0.53; talk after erasure 0.86 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | failed | s\* 0.113; RI 0.20 [0.19, 0.23]; β 0.89; γ_W 0.09; talk after erasure 0.70 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | s\* 0.130; RI 0.07 [0.01, 0.11]; β 0.91; γ_W -0.44; talk after erasure 0.49 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | s\* 0.067; RI 0.07 [0.05, 0.09]; β 1.10; γ_W 0.03; talk after erasure 0.81 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | failed | s\* 0.102; RI 0.06 [0.03, 0.08]; β 0.79; γ_W -0.27; talk after erasure 0.79 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native + replication | failed | s\* 0.178; RI 0.04 [0.02, 0.05]; β 0.91; γ_W -0.06; talk after erasure 0.77; N-sweep slope 0.90 [0.77, 0.99] × passive; cap hits 0.05% |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native | failed | 21,165 forced erasures: talk 0.74 [0.69, 0.80] (τ 10 calls), reply share 1.21 [1.15, 1.27], replies per call 0.92 [0.82, 1.05]; share monotone from 0.093 (j 1) to 0.121 (j 41); reset snapshot ≈ 0 |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | failed | merge flood: λ ×2.6 (#39 → #40); leak φ 1.07 [0.51, 1.20]; within-agent slope 1.06 [0.95, 1.11] × passive |
| [NE03](goalperiod-subhypotheses/NE03/README.md) | native | failed | chat-mode prompt flat in the day's traffic before (3.9 [−3.1, 7.0] tokens/msg) and after (4.6 [0.8, 8.6]); no change at the documented limit; chat mode scaffold-capped throughout |

**36 folders: 32 replication (31 failed + G51 native/replication failed), 3 further natives failed. 0 supported, 0 mixed.**

## Results
*Scripts in `analysis/`: `h45lib.py` (estimators), `synthetic.py`, `run_periods.py` (replication), `natives.py`, `summarize.py`, `robustness.py`, `posthoc.py` (labelled post hoc), `figures.py`, `write_period_folders.py`, `confirm.py` (not run). Numbers: `data/processed/H45-context-homeostasis/` (`summary.json`, `replication.json`, `robustness_summary.json`, `posthoc.json`, `<period>/results.json`, `<NE>/native.json`, `synthetic/`). Figures: `figures/summary_obs.pdf`, `summary_obs2.pdf`, `synthetic.pdf`, `setpoints.pdf`.*

### Outcome vs prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| P1 | RI ≥ 0.5 (CI excl. 0) in ≥ 2/3 of 32 periods | **0/32**; CI upper < 0.5 in 32/32; RI −0.08 to 0.22; pooled 0.02 ± 0.01 (I −0.01, II 0.08, III 0.08 ± 0.02); \|RI − η_W\| ≤ 0.08 | **failed** (passive) |
| P2 (A1) | lever slope < 0 in ≥ 2/3 of regime-III periods | 3/9 (G51 −0.044 [−0.057, −0.030]); 12/32 overall, median −0.03 (synthetic controller −0.10) | **failed** (a weak lever exists in some periods) |
| P3 | CV ratio ≤ 0.5 in ≥ 2/3 | 0/32; 0.84–1.32, median 0.99 | **failed** |
| P4 | β ∈ [0.4, 0.9] in ≥ 70%; pooled within ±0.2 of 0.63 | 21/32 (66%); pooled 0.82 (I 0.73, III 0.98); vs H18 ρ 0.71, +0.28 steeper | **narrowly failed** (dilution replicates, steeper: one reply per talk in regime III) |
| P5 (A2) | γ_R < 0 and γ_W > 0, pooled regime III | γ_R **+0.081** [0.063, 0.102], γ_W **−0.10** [−0.16, −0.06] (42,168 talk calls); per period 0/11 controller pattern | **failed**; post hoc with a momentum control γ_R −0.04 [−0.07, −0.004], γ_W −0.12: competition pattern |
| P6 (A3) | forced-reset talk overshoot ≥ 1.2 in ≥ 2/3 | 0/9; 0.49–0.86, 5/9 with the CI below 1; pooled 0.74 [0.69, 0.80] | **failed (reversed)** |
| P7 | lab ≥ 30% of s\* variance; regime I vs III ≥ × 1.5 | lab η² 0.14 (permutation q95 0.23, p 0.41); agent 0.56, period 0.44; s\* median 0.114 (I), 0.121 (II), 0.099 (III): ratio 0.87 | **failed** |
| P8 | no truncation plateau, P growth ≥ 1.3 | 32/32 (1.86–2.45) | **supported** (no scaffold truncation in computer-use mode) |
| P9 | 200-event cap < 0.1%, sets no s\* | 443 of 928k #51 calls (0.048%), after timer pauses (68%) | **supported** |
| Natives | NE41, NE42, G51, NE03 | see the table above | 4/4 against H45 |

### Findings
1. **No context homeostat: the share is passive.** At fixed segment position the room share s = R/P scales with inflow per call at the passive slope (ε ≈ 1 − s̄), because own content does not respond to inflow (η_W ≈ 0). Set points (median share at j 15–35) run 0.05–0.18 per period (#51, one big room, highest) and differ more by agent and period than by lab. When the room floods (NE42 merge, #51 roster growth) set points move with the flood at 1.06 and 0.90 × passive. Regime III shows a sliver of compensation (pooled RI 0.08, voluntary consolidation ~3–4% sooner per doubling of early inflow in a third of the periods), an order of magnitude below a controller.
2. **The scaffold, not the agent, bounds context.** Computer-use contexts grow monotonically (P roughly doubles from j ≈ 10 to j ≈ 33) until a reset; the 41-call cap bounds segment length. Regime-I chat-mode prompts stay at ≈ 8–10k tokens whatever the day's traffic, before and after NE03. The 200-event cap almost never binds. The reset context carries no measurable recent room traffic.
3. **Dilution is real and steeper with reply labels, but it is not a homeostat.** β 0.82 pooled (0.73 in regime I, 0.98 in regime III): in regime III a talk call replies to at most about one pending message whatever the backlog. Per-period β correlates with H18's mention-based β (ρ 0.71) but is 0.28 steeper; DQ2 parents are one per message, so this is a per-talk budget measure. Engagement depends on context content the wrong way for a share controller. It rises with room content already in context (conversational momentum: the agent already talked in this segment) and falls with own content. Post hoc, with momentum controlled, both coefficients are negative: context competition (HH158), confounded with task phase.
4. **Erasure: a talk dip, not an import burst.** After a forced (or voluntary) reset, agents talk 26% (34%) less for about ten calls, and the talks they make are 21% (29%) more often replies. Replies per call are unchanged. The share does not need restoring: arrivals during the ~3-min memory call land on the first post-reset call (share 0.093 at j = 1 vs 0.12 at j = 41). This fits H39 (erasure pushes toward work) and H15 (≈ 10-turn output dip).
5. **Physics-of-life reading.** In Kolchinsky's terms the agent does not maintain its context state by regulated import; the room content in its context is an open-loop, driven variable, degraded by the scaffold's resets. The homeostatic set points in this system are the scaffold's (41-call cap, chat window) and memory size (H09), not context composition.

### Post-hoc analyses (not pre-registered; `analysis/posthoc.py`)
- PH1 momentum: adding "previous talk in this segment" (+0.38 [0.30, 0.44]) turns γ_R to −0.04 [−0.07, −0.004]; within-segment talks only: γ_R −0.10, γ_W −0.16 (both CIs below 0).
- PH2 replies per call after a reset: 0.92 [0.82, 1.05] (forced), 1.00 (voluntary).
- PH3 β with the pending set restricted to the current segment: 0.86 [0.84, 0.89] vs 0.91 [0.89, 0.94] (ledger pending), regime III.

### Robustness (`robustness.json`)
RI medians across the 32 periods: baseline 0.006; action-row labs only 0.015; other labs' calibration × 0.5 0.030 and × 2 −0.037; a generic 0.25-tokens-per-character ruler 0.061; low-confidence call starts dropped 0.007; band j 8–20 −0.002. In every variant 32/32 periods have the RI CI upper bound below 0.5.

### Caveats
- R is a lower bound on room content (omits `search_history` results; the reset snapshot measured ≈ 0). A share sitting partly in search results would be invisible.
- s and λ share R, so measurement error in R pulls ε toward the passive value. The synthetic shows a moderate controller (RI ≈ 0.4) is still recovered, but a weak one (RI < 0.15) would be hard to see.
- Prompt tokens are dense only for Anthropic and Google; other labs contribute event calls only, with a borrowed calibration.
- The reply-parent outcome allows one parent per talk message, so β ≈ 1 partly reflects the measurement; it is not comparable one-to-one with H18's per-sender mentions.
- γ is not identified per period (synthetic); the pooled γ_W < 0 is confounded with task phase (deep in work = much own content = status talk).
- The post-erasure talk dip may be re-orientation (reading memory, screenshots); the mechanism is not identified. NE41's timing is exogenous, but forced segments are those that ran 41 calls without a voluntary consolidation (selection on the preceding segment).
- NE42 is goal-confounded and its inflow did not return at the split (A-B-B′). NE03's limit is undocumented.
- Multiplicity: 32 periods × 9 predictions plus 4 natives; the headline (0/32, 32/32 below 0.5) survives any correction. Holdout not used.

## Confirmatory design (written 2026-10-04 after round 1, before any holdout use; `analysis/confirm.py`, dry-run only, NOT run)
Targets: held-out regime-III periods #45, #46, #47, #49, #50 (scored), #43, #48 (one day each: reported), the #51 tail (51m), and NE22 (the 200-event cap, 06-11, inside #46). Frozen predictions: C1 RI < 0.5 with the CI upper bound < 0.5 and ε within 0.25 of passive in every scored target [0.85]; C2 \|η_W\| < 0.25 in ≥ 4 [0.8]; C3 β ∈ [0.6, 1.2] in ≥ 4 [0.7]; C4 no controller pattern in pooled γ [0.75]; C5 pooled forced-reset talk ratio in [0.5, 0.95] with the CI upper < 1 [0.65]; C6 NE22: cap hits < 0.5% of #46c calls and set points move less than the passive prediction + 0.2 [0.7]. Safeguards: refuses without `--confirm --i-understand-this-uses-the-locked-holdout` or with modified files; the dry run on stand-ins (#41, #42, #44, 51l; NE22 analogue 51k → 51l) reproduces round 1 (C1–C5 pass on stand-ins). Reuse policy: #45 (H02, H23), #46/#47 (H26, H47 content statistics), NE22 (H08, H18 backlog response). H45's statistic (prompt-token context composition, reply-parent engagement) is a different statistic and modality. Disclose in the cards and LOG.md before running.

## Notes
- 2026-10-04: promoted from HH166 (Vivian, 2026-10-04).
- 2026-10-04 06:21 UTC: operational definitions, predictions, verdict rule, natives and the synthetic design written before any real-data outcome statistic. The P rule was fixed after the structural token check (Anthropic event counts are uncached-only outside chat mode).
- 2026-10-04: the coordinator flagged `activity_bins` (join bug). H45 never reads it; the ledger's `outage_*` columns, which derive from it, are not used in any filter.
- 2026-10-04: round 1 run (exploratory, non-holdout): replication on 32 periods, natives NE41, NE42, G51, NE03, robustness, post hoc PH1–PH3; card, period folders and summary written. Every per-period verdict failed (Amendment A2 rule; the original rule gives the same verdicts because no period shows the controller's γ pattern).
- Read-only imports: shared tables (`call_windows`, `context_ledger_turns`, `context_ledger_items`, `actions`, `events_core`, `chat_core`, `reply_pairs`, `roster`, `period_units`, `calendar`) and `infra/shared/common.py` (`holdout_mask`, `load_goals`, `REVISION`). H18's per-period β values are quoted from its card. No code is imported from other hypothesis folders.
- Data findings for shared files: Anthropic `events_core.tokens_in` is uncached-only in computer-use mode (use action rows with cache fields); `call_windows` carries no prompt tokens (H45's `calls.parquet` has P per call); DQ2 reply parents are one per message (a per-talk cap on engagement); arrivals during a consolidation land on the first post-reset call (NE41: k_new 5.8 at j = 1).

## Round 2 redirects (2026-10-04)
- **Where round 1 went sideways:** nowhere methodologically; the premise failed. Agents cannot refuse room messages and do not compensate for them, so context composition is a scaffold and room-design variable.
- **What the direction is really after:** whether agents manage their information intake at all, or the scaffold does it for them.
- **H45-R1.** Context competition (HH158): does reply engagement fall with own-content fill once DQ3 behavior states control task phase? Also test whether the dilution exponent steepens with fill.
- **H45-R2.** Cadence as the agents' only intake lever: do call intervals shorten when the room's per-minute rate rises? NE44 (pause default) gives a contrast.
- **H45-R3.** What fills the post-erasure talk dip? Use DQ3 behavior states and the work ledger at NE41, jointly with H44.
- **H45-R4.** Run `confirm.py` on the holdout (#45–#50, 51m, NE22) after the reuse disclosures.

## Round 2 (2026-10-05): do agents manage their intake at all?
*Design, predictions, nulls and kill rules drafted 2026-10-05 04:27–04:37 UTC and written here at 04:37 UTC, before any round-2 statistic on real data. Looked at before this: schemas of `behavior_states_v3`, shared `calls`, `call_windows`, `pending_sets`; coverage only (DQ3 labelled share of non-reserved windows 0.50–0.92 per regime-II/III period; early wakes 0.004% of regime-III calls; `pause_s` present on pause calls only; rooms per period: one in G30–G33, three in G35–G44, ten in G51). No engagement, interval or post-reset relation was computed. R4 (the reserved-data confirmation) is not run.*

**Question served:** Q4 (where the swarm's information lives) and Q5 (what an operator can set). Round 1 showed that the scaffold, not the agent, sets context composition. Round 2 asks whether agents manage their information intake in any other way: by attention (R1), by cadence (R2), or by what they do after an erasure (R3).

**Common rules.** Non-reserved days only (`holdout_mask`; the H45 `calls.parquet` already excludes reserved days, asserted again). Fits are within one goal period. The pooled value is a DerSimonian–Laird random-effects pool of the per-period estimates (CLAUDE.md exception (d): per-period γ was not identified in round 1), always shown next to the per-period values. CIs: bootstrap over 1-h blocks within PT days (Known issue: day-cluster bootstraps under-cover in 5-day periods), B = 200 (B = 100 in G51). **Task-phase control** = the DQ3 v3.1 probability vector (10 of 11 states; `p_execute_task` is the reference) of the agent's 5-min window *before* the window that holds the call. The same-window vector is partly defined by the outcome (a window with replies is labelled communicative), so it is a sensitivity check only. Calls without a labelled previous window are dropped.

### R1 · Context competition once task phase is controlled
*Model:* round 1's rival 4 (HH158): per-talk engagement falls with own content W = P − R (own tool output, screenshots, own text) at fixed backlog k. *Rival:* task phase. Deep in work, an agent holds much own content and posts status, not replies; then γ_W < 0 is phase, not competition.
- **Sample:** computer-use talk calls (round 1's `talk_rows`: not the first talk of the agent-day, k ≥ 1, W > 0) in regime-II/III periods with ≥ 500 such calls and a labelled previous window.
- **M0** (round 1, PH1): cloglog for E1 (`eng_pending`) on ln k, ln(1 + R_old/500), ln(W/1000), previous talk in this segment, 5-call position bands, agent-day effects. **M1** = M0 + the lagged DQ3 vector. γ_W = the ln(W/1000) coefficient; retention ρ_W = γ_W(M1)/γ_W(M0).
- **Steepening:** per (talk call, scored pending sender) units from the shared `pending_sets` (H18's rule): mention response `resp` ~ ln k + w̃ + ln k × w̃ + the item names the recipient + ln(1 + the sender's pending items) + lagged DQ3 + agent-day effects, cloglog; w̃ = ln W − the agent × period mean of ln W. Per-sender exponent β(w̃) = −(b_k + b_kW w̃); steepening = b_kW < 0. The mention outcome is used because reply parents carry a one-parent budget (Known issue). Talk-call k is not separable from reactive timing (H18 correction), so the identified check is G51's timer-wake batches (exogenous k; `wake_pending.resp5`).

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| R1-P1 | DL-pooled γ_W(M1) < 0, CI below 0 | CI includes 0: own-content competition was task phase | 0.55 |
| R1-P2 | retention ρ_W ≥ 0.5 | ρ_W < 0.5: most of round 1's γ_W was phase | 0.55 |
| R1-P3 | \|γ_W(M1)\| above the 95th percentile of M1's γ_W in the phase-only synthetic world (leftover confounding from a lagged, imperfect phase control) | inside that band: not distinguishable from residual phase | 0.45 |
| R1-P4 | b_kW < 0, DL CI below 0 (talk calls, mention outcome) | CI includes 0 at synthetic power ≥ 0.8 for b_kW = −0.15: a powered null | 0.25 |
| R1-P5 | G51 timer wakes: b_kW < 0, the same sign as R1-P4 | opposite sign or CI includes 0 | 0.25 |

**Kill rules.** R1-P1 fails *or* ρ_W < 0.5 → "own-content competition is task phase" (round 1's post hoc HH158 reading is withdrawn). R1-P4 fails with power ≥ 0.8 → "dilution does not steepen with fill".

### R2 · Cadence as the only intake lever
*Model:* an agent that manages its intake shortens its call interval when the room speeds up, to keep each batch small. A batch-holding controller gives ζ = d ln Δ / d ln(room rate) = −1; a passive agent gives ζ = 0 for read traffic. *Rivals:* (i) **common drive**: busy stretches are fast stretches for everyone (scheduler or task field), so read and unread traffic predict short intervals alike; (ii) **address gating** (Q1): only messages that name the agent shorten its interval; (iii) **talk composition**: reads cause talk calls, and talk calls are short (H40 r2: long tool calls lower talk propensity); (iv) **chatter hold** (H72 r2): undirected traffic *lengthens* pause chains in G51.
- **Unit:** consecutive computer-use receiving calls of one agent in one PT day, regimes II–III. Interval Δ_c = t_call(c+1) − t_call(c); dropped if c+1 opens a segment by consolidation, if Δ ≤ 0 or Δ > 2 h.
- **Exposures** (others' agent and human messages from `chat_core`; the automated speaker is excluded): *read* = posted in the call's room in [t_call − 10 min, t_call) (all of it is visible at c or earlier, by the ledger rule); *in flight* = posted in the room in [t_call, t_call + 10 min) (unseen at the decision), excluding messages that name the agent or are DQ2 reply children of its messages; *cross-room* = messages in the period's other rooms in [t_call − 10 min, t_call), per other room (periods with ≥ 2 rooms). Each is split into **directed** (names the agent; indicator ≥ 1) and **undirected** (ln(1 + n)).
- **Model:** OLS of ln Δ_c on the six exposure terms, 5-call position bands, 30-min bins of active-day time, the lagged DQ3 vector, agent-day effects. ζ_u = the undirected read coefficient. **Partition contrasts:** Δζ_u = ζ_u − ζ_u(in flight); Δζ_u^× = ζ_u − ζ_u(cross-room); the same for directed. Non-talk subsample: calls c that do not talk.
- **Call-length selection** (H50 Known issue): the design is anchored on call starts (the decision) with fixed clock windows, so it never samples the call in flight at a message. Per-call weighting over-represents fast stretches; a time-weighted fit (weights ∝ Δ) is a sensitivity check.
- **NE44** (pause default 12 h → 5 min, 2026-06-11) sits inside #46, which is reserved data. The only non-reserved contrast is across periods: before (G35–G44) vs after (G51). It is confounded with NE21 (hours), NE43 (nudger off), N and the room design, so it is descriptive.

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| R2-P1 (H45-R2 as posed) | DL Δζ_u < 0 with CI below 0 and ζ_u ≤ −0.1; same sign in ≥ 2/3 of periods | Δζ_u CI includes 0 or is positive: no read-gated intake lever | 0.20 |
| R2-P2 (batch controller) | ζ_u CI includes −1 | CI lower bound > −0.5: no batch holding | 0.03 |
| R2-P3 (address rival) | directed read − directed in flight < 0, CI below 0 | CI includes 0 | 0.60 |
| R2-P4 (talk composition) | on non-talk calls \|Δζ_u\| < 0.05 and CI includes 0 | Δζ_u < 0 (CI) on non-talk calls: a lever beyond talk | 0.55 |
| R2-P5 (chatter hold, G51 pause calls) | Δζ_u ≥ 0 at pause calls | Δζ_u < 0 (CI) | 0.50 |
| R2-P6 (NE44, descriptive) | the sign class of Δζ_u is the same before (G35–G44 pool) and after (G51), difference < 0.1; pause calls ≥ 5× more common after | — | 0.50 |

**Kill rule.** R2-P1 fails in the DL pool *and* in ≥ 2/3 of periods → "agents do not use cadence as an intake lever" (the scaffold's call clock sets intake).

### R3 · What fills the post-erasure talk dip?
*Round 1:* after a forced reset (NE41), talk falls to 0.74 × baseline for about ten calls; replies per call do not change. *Cited, not redone:* H44 r2 (a one-call re-reading spike with an ≈ 8-call tail, Θ_c +0.106; writes −20% to −32%; re-reading is working-set habit); H15 r2 (the first reads carry 4% [−23, +26] of the output dip). *Rivals:* (a) **work push** (H39: erasure pushes toward work); (b) **re-orientation** (the agent spends the calls reading itself back in); (c) **idle** (more pauses and waits); (d) **status talk follows in-context output**: agents post status about work they can see in context, the wipe removes that, and new status waits for new output.
- **Sample:** regime-III segments opened by a forced reset, positions j = 1–40, non-reserved periods with forced resets (G36–G44, G51).
- **R3-A kind accounting:** round 1's k-adjusted profile (position dummies j = 1–19, k bins, agent-day effects, baseline j 20–40) for the indicator of each call kind: talk, cu action, pause or wait, search, other. With one design for all kinds, the excess shares sum to zero at every j, so the fill shares φ_kind = mean δ(kind, j 1–10) / (− mean δ(talk, j 1–10)) sum to 1.
- **R3-B behavior state:** the same profile for DQ3 groups of the call's own window, only for windows that hold no consolidation (the consolidation itself would mark the window as maintenance): orientation = self_maintenance + research_browse; communication = communicate_external + social + plan_coordinate; work = execute_task + debug_recover + verify_report; idle = idle + monitor_wait (+ meta in "other").
- **R3-C work ledger:** the same profile for a DQ4 work commit at the call (shared `calls.n_work > 0`).
- **R3-D status talk follows in-context output:** talk ~ the R3-A design + w_in (write calls among the previous five calls that are in the current segment) + w_out (write calls among the previous five that came before the reset, so are erased; non-zero only at j ≤ 5). Linear probability; absorption A = 1 − D_talk(with w)/D_talk(without w), D_talk = mean δ(talk, j 1–10).

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| R3-P1 | φ_cu ≥ 0.7; φ_pause+wait ≤ 0.3 (DL pool) | φ_pause+wait > 0.3: idle fills the dip | 0.60 |
| R3-P2 | orientation excess > 0 and communication excess < 0 (CIs), work excess ≤ 0 | work excess > 0 (CI): work push | 0.45 |
| R3-P3 | work commits per call at j 1–10 below baseline (CI < 0) | ≥ baseline: work push | 0.65 |
| R3-P4 | b_in > 0 and b_in − b_out > 0 (CIs): talk follows writes still in context, not erased ones | b_in − b_out CI includes 0 | 0.40 |
| R3-P5 | A ≥ 0.5 | A < 0.2: the dip is not an output gap | 0.20 |
| R3-P6 | the talk dip's exponential τ (G51) lies inside H44's re-reading tail CI, ℓ₂ 8.2 [5.8, 11.8] calls | outside | 0.45 |

**Kill rules.** R3-P2's work excess > 0 (CI) or R3-P3 ≥ baseline → work push stands and re-orientation fails. R3-P4 fails → status talk does not track in-context output.

### Synthetic validation plan (axis F; before any round-2 statistic on real data)
All worlds use the real non-reserved skeleton (calls, positions, k, W, R_old, room message streams, write sequences, DQ3 vectors), with outcomes planted at values fixed here; 20 replicates per world; units G38, G41 and G51 (R1, R2), G38, G41, G51 (R3).
- **R1:** W0 phase only (truth uses the *same-window* DQ3 vector: communicate_external +0.6, social +0.4, plan_coordinate +0.3, idle −0.4 on the cloglog scale; γ_W = 0); W1 = W0 + γ_W = −0.3; per-sender W2 = phase + b_kW = −0.15; W2n = b_kW 0. Pass: M1 recovers W1 within ±0.1 in ≥ 80%; W0's M1 γ_W band gives R1-P3's threshold; b_kW size ≤ 0.10, power at −0.15 reported.
- **R2:** S_drive (ln Δ = agent-day mean − 0.3 ln of the centred ±15-min room rate + N(0, 1); no read coupling); S_read (−0.2 per ln(1 + undirected read)); S_talk (talk probability rises with reads, talk calls 0.7 shorter in ln Δ; no direct effect); S_dir (directed read −0.5). Pass: Δζ_u size ≤ 0.10 in S_drive and S_dir; recovery within ±0.07 in S_read; non-talk Δζ_u size ≤ 0.10 in S_talk.
- **R3:** S_mech (orientation +0.3 in windows that hold a consolidation, no behavior change); S_ctx (talk ∝ exp(0.6 w_in), real write sequences); S_pos (position dip 0.74, τ 6 calls, no write link); S_rec (talk ∝ exp(0.6 × all writes in the previous five calls)). Pass: consolidation-free R3-B excess size ≤ 0.10 in S_mech; b_in − b_out > 0 in ≥ 80% of S_ctx and size ≤ 0.10 in S_rec; A ≥ 0.5 in S_ctx and ≤ 0.2 in S_pos.
