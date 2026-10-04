# H110: Exchange bias: an agent's own artifact shifts its goal-switch loop

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only): mixed; HH340's mechanism signature fails.** Across the 4 transitions with both groups (#36→#37, #37→#38, #40→#41, #41→#42; 26 pinned and 28 unpinned agent-transitions), agents who committed to their own repo in the last 2 days keep more of the old state on day 1: R₁ 0.17 [−0.10, 0.41] vs −0.13 [−0.27, 0.05], difference 0.30 [−0.01, 0.57] (bge; gte 0.22 [−0.03, 0.43]; switcher fixed effects 0.37 [0.05, 0.66], gte 0.23 [−0.07, 0.46]). The decay ratio is 2.2 (gte 1.7) but its CI reaches 1. Neither HH340's rule nor its kill fires. The exchange-bias signature is absent: the offset is not tied to continued commits (pinned excess while still committing 0.00 [−0.10, 0.09]); it is gone by day 2 (difference 0.11); the continuing-vs-stopping native in G40 is null (−0.01 [−0.21, 0.18]); and the any-repo definition reverses the sign (−0.23). Per transition: 2 supported (G37, G38), 2 failed (G41, G42). Card and predictions 21:29–21:30 UTC, Amendment 1 at 21:55 UTC, both before any real-data statistic. `analysis/confirm.py` frozen and dry-run, **not run** (targets NE24 and the held-out regime-III transitions). Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH340.
**Question (GOALS.md):** **Q4** (where does the swarm's information live: does an agent's own artifact carry its old goal state across a goal switch) and **Q2** (what is field and what is coupling at a goal boundary: a self-made pinned layer acting as a field on its maker).
**Fields:** stat mech (exchange bias: a ferromagnet bonded to a pinned antiferromagnet shows a shifted hysteresis loop; remanence after a field step), information theory (the own artifact as a store), dynamics (relaxation after a quench)
**Literature:** none in `literature/` covers exchange bias. Background from memory: Meiklejohn & Bean, "New magnetic anisotropy", Phys. Rev. 102, 1413 (1956)†; Nogués & Schuller, "Exchange bias", J. Magn. Magn. Mater. 192, 203 (1999)†. Project cards: H96 (a goal switch is a quench: day-1 remanence R₁ 0.18–0.27 vs 0.85–0.89 across an ordinary night; a small residual decays over ~1 active day), H97 (kickoff restoring force; overshoot), H70 (89% return to own repo after an erasure; own-artifact pointer carries 0.14 bits but κ_A ≈ 0), H87 (only the context window carries value per bit), H100 (GPT-5.4 kept its old room's content after a move), H58 (agent + own artifact is the unit), H94 (repo ownership; ownership price λ_own).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent (19, 28, 30 excluded); Regime; Driving / external field (kickoff, goal text, room kickoffs); *Old-state direction ê_old*, *Field-orthogonal remanence M_exc*, *Persistence ratio R₁^old*, *Pseudo-switch (ordinary day boundary)* (H96); *Owner* (H94); *Work quantum*-level DQ4 agent work commits (`canonical & ~imported & author_kind == agent & ~automated`). New named variants proposed (defined under Observables; DEFINITIONS.md not edited): **pinned agent (own-repo, boundary)**, **agent remanence m_i**, **group persistence R₁^g and decay ratio ρ_λ**, **own-state remanence o_i**, **pinned offset e_i**.
**From:** HH340 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/01-inverse-ising/` (hysteresis of a bistable order parameter under a stepped field), `physics-models/11-vector-spins/` (the content state as an O(32) vector; the measurement)
**Data inputs (shared tables first):** DQ5 `embeddings/statements.parquet` + `statements_style_resid32_{bge_small,gte_modernbert}.npy` (both models; `white32` variant); `culture_vectors.directions` (whitened kickoff, goal and room-kickoff directions); DQ4 `work_commits` (agent work only, non-holdout); `calendar`; `goals.parquet` (kickoff times); `roster`; `holdout.json` via `holdout_mask`. No text is read. No H96 code or data is used: H96's estimator is re-implemented from its card (STANDARDS §8).

## Source HH (verbatim from the HH list, including refinements)
- **HH340 · Exchange bias: an agent's own artifact shifts its goal-switch loop.** In a ferromagnet bonded to a pinned layer, the hysteresis loop shifts sideways. H100's GPT-5.4 kept its old room's content after a move while it kept its old project, and H70 found that agents return to their own repo after an erasure. If the own artifact is the pinned layer, agents with a live own repo at a goal boundary should carry a constant offset toward the old goal, and the offset should last as long as they still commit to that repo.
  - *Prediction:* at goal boundaries, the old-goal alignment of agents who committed to their own repo in the last 2 days of the old period decays ≥ 2× slower than for unpinned agents. The offset ends within a day of their last commit to that repo.
  - *Check:* H96's old-goal alignment series, split by pinning status from DQ4 `work_commits`. Use agent fixed effects across boundaries, so that the same agent is pinned at some boundaries and not at others. Confirmatory: NE24 (06-29, GitHub → GitLab, inside the holdout window) replaces the pinning layer, so the bias should vanish there.
  - *Kill:* pinned and unpinned decay rates are within 25% of each other.
  - *Impostors:* priors: within-agent contrast. Exogenous: same boundary, same kickoff. Scheduler: n/a. Convergence: n/a (individual carry).
  - *Models:* 01 (hysteresis), 11 · *Builds on:* H96, H70, H100, H58

## Question
At a goal switch, does an agent that was still committing to its own repo keep its content closer to the old state, and for longer, than an agent without a live own repo? Does that offset end when the agent stops committing to the repo? If yes, the own artifact acts as a pinned layer: a self-made field that biases its maker's switching.

## Design: two layers (STANDARDS §4)
- **Transitions.** P−1 → P with both periods non-holdout, the windows inside one regime, and DQ4 work dense (from #30; earlier zeros are ambiguous): **G31** (#30 → #31, regime I), **G37**, **G38**, **G39**, **G40**, **G41**, **G42** (regime III). Excluded: #35 → #36 (crosses the 03-24 regime boundary inside the post window), every transition with a held-out side. The row belongs to the new period P (as in H96).
- **Sampling facts seen before writing** (eligible agents with statements on L and on day 1; pinned = own-repo commit in the last 2 active days): G31 11 eligible / 1 pinned; G37 12 / 8; G38 12 / 5; G39 13 / 1; G40 15 / 14; G41 15 / 4; G42 15 / 9. Any-repo commits: 11, 11, 10, 7, 14, 12, 13. So within-transition contrasts exist in G37, G38, G41, G42; G31, G39 and G40 are nearly one-sided.
- **Replication** (role `replication`): the common estimator (O1–O3) at every transition; the pooled contrast across transitions is a hierarchical partial-pooling estimate (named exception (d): 1–14 agents per group per transition), reported next to the per-transition values. The transition is the object (exception (c)); agent fixed effects use agents seen at several boundaries (exception (b)).
- **Natives** (role `native`):
  - **G40** (#39 → #40, a continuation boundary: NE34 found 78% continuation; 14/15 pinned): the second half of HH340 inside one boundary. Pinned agents who keep committing to their old own repo after the kickoff vs those who stop: the offset should last only for the first group.
  - **G39** (#38 → #39, the 04-27 room reshuffle): H100's movers (Opus 4.6, Sonnet 4.6, GPT-5.4) and stayers, split by whether they kept committing to a #38 repo after 04-27: own-room old-state memory (H96's G39 domain memory) should be larger for those who kept committing. Not blind: H100 reported GPT-5.4's carry.
  - **NE24** (06-29, GitHub → GitLab, the #49 → #50 boundary): confirmatory only (holdout).

## Model
**From:** `physics-models/01-inverse-ising/` (hysteresis), measured with the O(32) content vector of `physics-models/11-vector-spins/`.

Each agent's content state s_i(t) (unit, style-residualized, field-orthogonal) carries a component m_i(t) along the old state ê_old. At the kickoff t₀ the field steps from h_{P−1} to h_P. A free spin relaxes as m_i(h) = m_i(0) e^{−λ_U h} (H96: a quench, R₁ ≈ 0.25 on day 1). A spin bonded to a pinned layer p_i (its own artifact) feels an extra field J_ex p_i that does not switch with h:

  dm_i/dh = −λ (m_i − m_i^∞),  m_i^∞ = J_ex π_i(h) / λ,  π_i(h) = 1 while i still commits to its own repo, else 0

- **Exchange bias (HH340):** the pinned offset m^∞ > 0 while π = 1, so pinned agents' old-state alignment decays slower (λ_eff ≤ λ_U/2 on day 1) and drops to the free curve within a day after their last commit to that repo.
- **R0, no pinning (H87: κ_A ≈ 0; H96: quench):** the own repo stores *where* an agent works (H70), not its content state; pinned and unpinned agents decay alike.
- **R-act, activity confound:** pinned agents commit more and talk less, so their statements are fewer and more work-centred; a difference in noise or topic mix mimics a slower decay. Handled by the within-agent contrast, ratio-of-sums estimators and the pre-level match.
- **R-cont, continuation:** at continuation boundaries the new goal continues the old work, so everyone's old state persists and pinned agents are over-represented there. Handled by the within-transition contrast (same boundary, same kickoff, same field projection).
- **R-comp, agent constant:** agents whose constant lies near the old state look persistent whatever their pinning. Handled by agent fixed effects (switchers) and the leave-agent-out old state.

## Data scheme (`scheme/`)
`scheme/build.py` → `data/processed/H110-exchange-bias-own-artifact/` (≲ 20 MB, `_provenance.json`). Non-holdout rows only, asserted with `holdout_mask` and the table flags.
- **Transitions** (`transitions.parquet`): P, P−1, regime, kickoff time t₀ (`goals.parquet` kickoff `win_start`, else the first active day's window start), L (last active day of P−1), old-state days L−3…L−1, the last 2 active days before t₀, P's first 5 active days.
- **Pinning** (`pinning.parquet`): per agent × transition: owner-rule own repos (H94 owner = author of the earliest non-holdout agent work commit), commits in the last 2 active days (own, any), pinned flags (`pinned_own` primary, `pinned_any` variant), the pinned repos, post-kickoff commits to those repos by day, t_last (last commit to a pinned repo within P's first 5 active days, null if none), continuing flag.
- **Windows** (`windows_<model>.parquet`): per agent × transition × window (pre = L plus day-1 statements before t₀; days 1–5 of P after t₀): statement count, m_i (old-state remanence), o_i (own-state remanence), b_i (new-kickoff alignment), placebo medians.
- **Regimes covered:** I (G31) and III (G37–G42).

## Observables
*Written 2026-10-04 21:29–21:30 UTC, before any H110 statistic on real data. Vectors: DQ5 `style_resid32` statements (unit), bge primary, gte in parallel; chat + intentions (as H96).*
- **O0 Old state, field and placebos (H96's construction).** Agent-day vectors: unit mean of ≥ 3 statements. ê_old^(−i) = unit mean of the other agents' agent-day vectors over days L−3…L−1 of P−1. F_P = span{kickoff, goal-text chunks, room kickoffs of P} (whitened, orthonormalized); P⊥_F projects it out. Placebo old states ê_Q: unit mean of the last 3 active days' agent-days of same-regime non-holdout periods Q ∉ {P−2, …, P+1}.
- **O1 Agent remanence m_i(w)** = v_i,w · P⊥_F ê_old^(−i)/|P⊥_F ê_old^(−i)| − median_Q v_i,w · P⊥_F ê_Q/|·|, with v_i,w = unit mean of agent i's statements in window w (≥ 3 in pre, ≥ 2 in post windows).
- **O2 Group persistence and decay ratio (primary).** For group g ∈ {pinned (P), unpinned (U)} at transition T: R₁^g(T) = Σ_{i∈g} m_i(day 1) / Σ_{i∈g} m_i(pre) over agents with both windows. Pooled over transitions where both groups have ≥ 2 agents: R̄₁^g = Σ_T Σ_{i∈g} m_i(day 1) / Σ_T Σ_{i∈g} m_i(pre). Decay rate λ_g = −ln max(R̄₁^g, 0.02) (per first active day); **decay ratio ρ_λ = λ_U / λ_P**. HH340: ρ_λ ≥ 2. Kill: ρ_λ within [0.8, 1.25]. CI: agent-cluster bootstrap (agents resampled with all their transitions; 2,000 draws). **Agent fixed-effects variant:** only switcher agents (pinned at ≥ 1 and unpinned at ≥ 1 eligible transition); each agent's group sums are divided by its number of transitions in that group, so each switcher weighs equally in both groups. The pre level of each group must be identified (CI > 0).
- **O3 Offset end.** Pinned excess e_i(d) = m_i(day d) − mean over the transition's unpinned agents of m_j(day d), d = 1…5. Pinned agent-days split into *live* (d ≤ day of t_last + 1 active day, or all days if i commits to the pinned repo on every post day) and *after*. HH340: mean e(live) > 0 and mean e(after) ≤ ½ mean e(live).
- **O4 Own-state remanence o_i(w)** = v_i,w · P⊥_F x̂_i^old − mean_{j≠i} v_i,w · P⊥_F x̂_j^old, with x̂^old the unit mean of each agent's own agent-days over L−3…L−1 (the agent-specific part of the old state). O2's group persistence and ratio on o (secondary).
- **O5 Transition-level comparison (phase-diagram, descriptive).** Spearman ρ(pinned share, R₁ of the transition) over the 7 transitions.
- **O6 Robustness.** Both models; `pinned_any` in place of `pinned_own`; white32 vectors; the old state from the last 2 instead of 3 days; post window days 1–2 pooled.

## Null / baseline
*Written 2026-10-04 21:29–21:30 UTC.*
- **N1 Unpinned agents at the same boundary** (same kickoff, same field projection, same old state): the free-spin decay.
- **N2 Within-agent contrast** (switchers): the same agent pinned at one boundary and not at another.
- **N3 Placebo old states** (O1): generic content removed.
- **N4 Synthetic worlds (axis F), run first** on the real skeleton (statement times, agents, transitions, real pinning labels and commit days): S0 no pinning (λ_P = λ_U, R₁^U ≈ 0.25 as in H96), S1 HH340 (λ_P = λ_U/2 while live, free after the last commit), S2 activity confound (pinned agents have 0.6× the statements and 1.3× the noise, no pinning effect), S3 continuation (one transition with high common persistence and most agents pinned, no pinning effect). Amplitude and noise calibrated to the real old-state order q (H96's card values) and to the real within-agent-day statement dispersion (an instrument). Outputs: size and power of the ρ_λ rule, the kill rule's power under S0, and O3's identification.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | no | Windows are whole active days on both sides of the same boundary for both groups. | n/a |
| Exogenous field (kickoff, goal, operator) | yes | Same boundary and kickoff for both groups; the new field span (kickoff, goal, room kickoffs) is projected out; placebo old states. Operator messages are not regressed. | partly |
| Shared model priors (family, style) | yes | DQ5 `style_resid` vectors; leave-agent-out old state; within-agent (switcher) variant with agent fixed effects. | removed (switcher variant) / partly (pooled) |
| Contemporaneous convergence | no | The statistic is an individual carry of a state built days before the switch; no co-movement is used. | n/a |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0 no pinning (quench for all), R-act (activity confound), R-cont (continuation), R-comp (agent constant).
**Locked holdout used for confirmation:** none run. `analysis/confirm.py` (frozen, dry-run only): NE24 (#49 → #50, the pinning layer replaced) and the held-out regime-III transitions #42 → #43 … #48 → #49 and #50 → #51.

| Axis | Test (plan) | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | pinning from DQ4 owner rule; remanence from H96's construction; both models | 1 | Shared tables; H96's estimator re-implemented; both models agree in sign; the result depends on the pinning definition (own vs any repo reverses). |
| B assumptions | single-exponential day-1 decay; pinning exogenous to content (activity audit) | 1 | Activity matched; the decay ratio is unresolved when one group is fully quenched (R₁ ≤ 0); a single exponential is not adequate (H96). |
| C adequacy | pinned vs unpinned at the same boundary; switcher fixed effects | 1 | Within-boundary and within-agent contrasts; dR borderline (one variant significant). |
| D unfitted predictions | offset end at the last commit (O3) is not fitted | 0 | The commit-locked offset, HH340's signature, is absent. |
| E interventional | NE24 (holdout); G40 continuing vs stopping | 0 | G40 continuing vs stopping is null; NE24 not run. |
| F identifiability | real-skeleton synthetic: size, power at ρ_λ = 2, kill power | 1 | Calibrated to real moments; size ≤ 0.03; detection power 0.85; HH-rule power 0.47–0.60 (A1). |
| G ground truth | owner rule and commits from public git histories | 1 | DQ4 commits (99.6% author agreement); owner rule on non-holdout commits. |
| H comparative | R0, R-act, R-cont, R-comp | 1 | R-act excluded (activity matched; S2); R0 not rejected; R-cont handled within boundary. |
| I transfer | regimes I and III, both models; holdout not run | 0 | Transitions disagree (2 supported, 2 failed); only 1 regime-I pinned agent; holdout not run. |

**Scorecard: A1 B1 C1 D0 E0 F1 G1 H1 I0.**

## Prediction
*Written 2026-10-04 21:29–21:30 UTC, before the synthetic validation and before any H110 statistic on real data.*

**What I had seen when writing this (not blind):** the H96 card (per-transition R₁: G31 0.26, G37 0.28, G38 0.11, G39 −0.34, G40 1.43, G41 −0.28, G42 0.48; q 0.16–0.66), H100 (GPT-5.4 carried its old room's position), H70/H87 (own artifact: 0.14 bits, κ_A ≈ 0), the pinning counts above. No H110 estimator has been computed. G40's large R₁ with 14/15 pinned is known, so O5 and the G40 transition are not blind.

My expectation: H96 shows that 70–80% of the old state is gone within the first active hour for everyone. H70/H87 show that the own artifact stores *where* an agent works, not a content state. I expect a small or no pinning effect, and too little power to separate a 2× ratio from 1×. Prior on HH340's ≥ 2× slower decay: about 0.2.

- **P0, synthetic (axis F; run first).** (a) Size of "ρ_λ CI lower > 1" ≤ 0.07 under S0, S2 and S3 [0.6]; (b) power of the HH rule (ρ_λ ≥ 2 and CI lower > 1) ≥ 0.8 under S1 [0.4]; (c) under S0 the kill rule (ρ_λ ∈ [0.8, 1.25]) fires with probability ≥ 0.5 [0.3]. If (b) or (c) fail, the kill cannot fire and a negative is "inconclusive".
- **P1, exchange bias (HH340's core; the test).** Pooled ρ_λ ≥ 2 with its CI lower bound > 1, in both models, and in the switcher variant ρ_λ > 1 [0.2]. **Kill:** pooled ρ_λ ∈ [0.8, 1.25] with P0(b) power ≥ 0.8 [0.3].
- **P2, offset end.** mean e(live) > 0 (CI) and mean e(after) ≤ ½ mean e(live) [0.25].
- **P3, own state.** O4's ρ_λ(o) > 1 with CI lower > 1 [0.3].
- **P4, transition level (descriptive, not blind).** ρ(pinned share, R₁) > 0 [0.5].
- **Effect that matters:** ρ_λ = 2 (HH340), equivalently R₁^P ≈ (R₁^U)^{1/2}: about 0.5 vs 0.25 on day 1.

**Verdict rules.**
- *Transition (period folder):* **supported** if both groups have ≥ 2 agents with identified pre levels and R₁^P > R₁^U with λ_U/λ_P ≥ 2; **failed** if λ_U/λ_P ∈ [0.8, 1.25] or R₁^P < R₁^U; **descriptive** if a group has < 2 agents or a pre level is not identified; **mixed** otherwise. Per-transition verdicts are descriptive evidence; the pooled rule decides.
- *Natives:* G40 supported if the continuing pinned agents' mean e over days 1–3 exceeds the stopping pinned agents' (bootstrap CI > 0); failed if reversed with CI; mixed otherwise; descriptive if a group has < 2 agents. G39 supported if agents who kept committing to a #38 repo keep a larger own-room memory than those who did not (sign, both models); descriptive with < 2 per group.
- *Hypothesis:* **supported** if P1 passes; **failed (killed)** if the kill fires with power ≥ 0.8; **inconclusive** if the kill's power is < 0.8 and P1 fails; **mixed** otherwise.

### Amendment 1 (2026-10-04 21:55 UTC, after the synthetic validation, before any H110 statistic on real data)
`analysis/synthetic.py` on the real skeleton (7 transitions, real windows, statement counts, pinning labels and last-commit days). Calibration (instrument; no pinning information used): the generator matches the real old-day moments (within-agent-day statement cosine 0.41/0.45, between-agent same-day 0.35/0.38, cross-period 0.09/0.13, agent self-similarity excess 0.11; bge/gte) with grid error ≤ 0.002. bge 60 replicates per world, gte 30.

| World | ratio ρ_λ median [IQR] | HH rule (ρ_λ ≥ 2 and CI lower > 1) | CI lower > 1 | kill fires (ρ_λ in [0.8, 1.25]) | offset O3: live CI > 0 |
| --- | --- | --- | --- | --- | --- |
| S0 no pinning | 0.95 [0.87, 1.11] / 0.94 | 0.00 / 0.00 | 0.03 / 0.00 | 0.75 / 0.90 | 0.12 / 0.13 |
| S1 HH340 (rate halved, boundary status) | 2.14 [1.77, 2.43] / 1.99 | 0.60 / 0.47 | 0.85 / 0.87 | 0.02 / 0.00 | 0.83 / 0.90 |
| S1L HH340 (halved only while committing) | 1.43 [1.25, 1.72] / 1.59 | 0.10 / 0.17 | 0.43 / 0.57 | 0.22 / 0.17 | 0.80 / 0.83 |
| S2 activity confound | 1.00 [0.83, 1.15] / 0.99 | 0.00 / 0.00 | 0.02 / 0.03 | 0.67 / 0.63 | 0.18 / 0.23 |

Changes forced by the synthetic:
1. **P0(b) fails as written:** the HH rule has power 0.60 (bge) / 0.47 (gte) at a true 2× effect, because the point estimate straddles 2. By the card's own clause the kill could then never fire. That clause measured the wrong thing. What a kill needs is discrimination: it fires in 75–90% of no-pinning worlds and in 0–2% of boundary-status 2× worlds. **New kill condition:** the kill counts if it fires in ≥ 50% of S0 worlds and ≤ 5% of S1 worlds (both met). Against the live-only world (S1L) a firing kill is weak evidence (fires 17–22%). The live-only version is tested by O3.
2. **A powered detection rule is added beside the HH rule:** "CI lower > 1" (size 0.00–0.03 under S0 and S2; power 0.85–0.87 under S1). If it holds while ρ_λ < 2, the verdict is *mixed* (a pinning effect smaller than HH340's).
3. **O3 is liberal** (live CI > 0 in 12–13% of S0 worlds; 18–23% under S2). P2 now also needs e(after) ≤ ½ e(live) and, for support, a live CI lower bound above the S0 95th percentile of e(live) (bge 0.060, gte 0.049; 40 extra S0 replicates computed at 21:57 UTC, still before real data).
4. The activity confound (S2) does not fake a pinning effect (CI lower > 1 in 2–3%).
5. The synthetic omits the field projection (random directions); the real run projects F_P.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | descriptive | 1 pinned / 10 unpinned; transition R₁ 0.28 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | supported | R₁ pinned 0.44 vs unpinned −0.22 (8/4; gte 0.14 vs −0.17); ratio 4.7 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | supported | R₁ 0.35 vs −0.21 (5/7; gte 1.12 vs 0.11); ratio 3.7 |
| [G39](goalperiod-subhypotheses/G39/README.md) | native | descriptive | 1 pinned; only 1 veteran kept committing to a #38 repo (native not testable) |
| [G40](goalperiod-subhypotheses/G40/README.md) | native | mixed | continuing − stopping pinned agents −0.01 [−0.21, 0.18] (4 vs 4; gte −0.08); 1 unpinned agent |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | R₁ −0.60 vs −0.23 (4/11): both quenched, pinned below |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | R₁ 0.24 vs 0.56 (9/6; gte 0.09 vs 0.36): reversed |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only, asserted in the scheme)
- **Scheme:** 7 transitions; 96 agent × transition pinning rows; 1.2 MB in `data/processed/H110-exchange-bias-own-artifact/`.
- **Code:** `scheme/build.py`; `analysis/{h110lib,synthetic,run,report,confirm}.py`.
- **Numbers:** `results/results.json`, `results/remanence_<model>.parquet`; `synthetic/synthetic_summary_{bge_small,gte_modernbert}.json`. Estimates: 53 rows in `per_period_estimates` (hypothesis H110).
- **Figure:** `figures/summary_obs.pdf` (per-transition and pooled persistence; offset vs commits).

**Headline.**
1. **A day-1 asymmetry in the right direction, not significant.** Pooled over the 4 transitions with both groups: R₁^P 0.17 [−0.10, 0.41], R₁^U −0.13 [−0.27, 0.05]; dR 0.30 [−0.01, 0.57] (bge), 0.22 [−0.03, 0.43] (gte). The decay ratio is 2.2 (gte 1.7), with a CI lower bound at the floor (1.0): the unpinned group's old state is fully quenched (R₁ below 0), so the ratio is not resolved. Switcher fixed effects (24 + 24 agent-transitions): dR 0.37 [0.05, 0.66] (bge), 0.23 [−0.07, 0.46] (gte). white32: 0.35 [0.11, 0.58].
2. **It is not exchange bias.** (a) No offset while agents still commit to the pinned repo: e(live) 0.00 [−0.10, 0.09] (bge), −0.04 [−0.13, 0.06] (gte); e(after) −0.04 / −0.07. (b) G40: pinned agents who kept committing vs those who stopped differ by −0.01 [−0.21, 0.18] (gte −0.08). (c) By day 2 the difference is 0.11 [−0.19, 0.43] (gte 0.09). (d) With "any repo" as the pinned layer, the sign reverses (dR −0.23 [−0.90, 0.29]; gte −0.23). (e) The own-state remanence o shows nothing (dR 0.05 [−0.30, 0.36]).
3. **Transitions disagree.** #36→#37 and #37→#38 favour pinned agents (ratio 4.7 and 3.7); #40→#41 quenches both groups; #41→#42 reverses (0.24 vs 0.56).
4. **Activity is matched.** Pinned and unpinned agents have the same median statements per window (32 pre, 36.5 day 1), so the activity confound (S2) is not at work.
5. **Transition level (not blind):** Spearman ρ(pinned share, R₁) 0.57 (bge), 0.25 (gte), n 7, driven by the #39→#40 continuation (R₁ 1.32, 14/15 pinned).

**Synthetic validation (axis F):** Amendment 1 (kill discriminates S0 vs S1: fires 75–90% vs 0–2%; detection rule size ≤ 0.03, power 0.85–0.87; HH rule power 0.47–0.60).

**Outcome vs prediction**

| | Prediction (locked) | Outcome | Verdict |
| --- | --- | --- | --- |
| P0 | (a) size ≤ 0.07; (b) HH-rule power ≥ 0.8; (c) kill fires ≥ 0.5 under S0 | (a) 0.00–0.03; (b) 0.47–0.60; (c) 0.75–0.90 | (a), (c) passed; (b) failed → kill condition amended (A1) |
| P1 | ρ_λ ≥ 2, CI lower > 1 (both models); kill if ρ_λ in [0.8, 1.25] | ρ_λ 2.2 / 1.7, CI lower 1.0 (floor); dR 0.30 [−0.01, 0.57] / 0.22 [−0.03, 0.43] | **neither** (no pass, no kill) |
| P2 | e(live) > 0 and e(after) ≤ ½ e(live) | e(live) 0.00 [−0.10, 0.09] / −0.04 | **failed** |
| P3 | own-state ρ_λ CI lower > 1 | 1.15 [0.39, 3.33] / 1.13 | failed |
| P4 | ρ(pinned share, R₁) > 0 (not blind) | 0.57 / 0.25 (n 7) | holds, weak and not blind |
| G40 native | continuing > stopping | −0.01 [−0.21, 0.18] / −0.08 | mixed (null) |
| G39 native | kept-committing veterans keep more room memory | 1 veteran kept committing | descriptive |
| HH340 | ≥ 2× slower decay; offset ends with the last commit | small day-1 asymmetry; no commit-locked offset | **mixed** |

**What this means.**
1. In magnet terms, there is no pinned layer: the bias does not track the state of the supposed pinning layer (continued commits). The own repo stores *where* the agent works (H70), not a content field that biases its switch.
2. The day-1 asymmetry may be real but small and short (≤ 1 day). It could come from a pre-switch difference: agents with live own repos at the boundary may be mid-task, and finish that task on day 1 whatever they commit later. Selection, not coupling to the artifact.
3. It agrees with H96: a goal switch is a quench for everyone; nothing self-made keeps the old state beyond day 1.

**Operator-facing conclusion.** Do not expect agents with their own live repo to resist a goal change: by day 2 they have switched like everyone else (difference 0.11 of the pre level, CI includes 0). If an agent must drop its old project, the kickoff alone does it; archiving its repo is not needed for the content switch.

**Caveats.**
- Small groups: 4 contrast transitions, 26 + 28 agent-transitions; the per-transition verdicts are descriptive.
- The decay ratio is unresolved when the unpinned group is fully quenched (R₁ ≤ 0); dR is the readable number.
- "Own repo" uses the owner rule on non-holdout commits only; repos first committed in held-out periods are owned by their first non-holdout committer.
- The commit-locked offset (O3) has a liberal size (0.12–0.13); its null result does not depend on that.

**Claim that stands:** at 4 non-holdout goal switches with both groups, agents still committing to their own repo keep at most a small, short old-state residual on day 1 (dR 0.30 [−0.01, 0.57] of the pre level, bge; gte 0.22 [−0.03, 0.43]) that is not tied to continued commits (pinned excess while committing 0.00 [−0.10, 0.09]) and is gone by day 2. Excluded: the switcher-variant significance (one model only), the transition-level correlation (not blind), the G39 native (not testable).

### Confirmatory design (written 2026-10-04 after exploration; not run)
`analysis/confirm.py`, frozen (sha256 of `h110lib.py`, `scheme/build.py` and itself in `analysis/confirm.sha256`); predictions in its header:
- **C1 (HH340 detection):** pooled dR CI lower > 0 and ρ_λ ≥ 2 over the held-out regime-III transitions #42→#43 … #48→#49 and #50→#51 [0.25].
- **C2 (kill):** pooled ρ_λ in [0.8, 1.25] [0.35].
- **C3 (NE24, #49→#50, GitHub → GitLab):** dR ≤ 0.10 (the pinned advantage vanishes when the pinning layer is replaced) [0.5].
- **C4 (signature):** e(live) CI lower > 0.06 and e(after) ≤ ½ e(live) [0.15].
- **Guards:** `--confirm` plus `H110_CONFIRM=1`; frozen hashes; `holdout_ledger.check()` per target (families `content_alignment`, `artifact_lineage`). `--dry-run` on #36→#37, #37→#38, #41→#42 with #40→#41 as the NE24 stand-in passed (`confirm_dryrun/dryrun.json`).
- **Reuse disclosure:** the same transitions are planned by H96 (the estimator H110 re-implements: a close cousin), H82 and H54; NE24 by H70 (C1), H01 and H58. Disclose; run after H96's confirm or declare second use.

## Round 2 redirects
- **H110-R1. Pre-switch task state.** Is the day-1 asymmetry a mid-task effect? Split pinned agents by whether their last pre-kickoff commit closed a task (merge, deploy, release) vs left it open.
- **H110-R2. Pool with H96's transitions** (same estimator, regime I has sparse commits) and add the held-out transitions in the confirm run for power.
- **H110-R3. A commit-level offset.** Replace the day clock with the agent's own commits: does old-state alignment of a statement depend on whether it was made between two commits to the old repo?
- **H110-R4. NE24 confirm** after Vivian's sign-off.

## Notes
- 2026-10-04 21:29 UTC: round-1 agent (same session as H109) started the card after reading H96, H97, H70, H87, H100 and H58.
- 21:29–21:30 UTC: card filled before any H110 statistic. Sampling facts seen: eligible and pinned counts per transition.
- 21:31 UTC: period folders with dated predictions; 21:40 UTC the G40 groups (continuing ≥ 2 of days 1–3; stopping none) fixed in its README, before running.
- 21:47–21:57 UTC: scheme build and synthetic (bge 60, gte 30 replicates); Amendment 1 at 21:55 UTC; extra S0 replicates for the O3 threshold at 21:57 UTC.
- 21:58–22:00 UTC: real-data run (both models, white32), report, estimates, confirm freeze and dry run.
- Reporting additions after seeing results (labelled; no verdict rule changed): dR = R₁^P − R₁^U with its CI as the readable contrast when the ratio hits the floor; the activity audit table.
- Suggested shared changes (not made): DEFINITIONS entries for *pinned agent (own-repo, boundary)*, *group persistence R₁^g and decay ratio ρ_λ*, *pinned offset e_i*; an infra Known issue: "decay-rate ratios from day-1 persistence are unresolved when one group is fully quenched (R₁ ≤ 0); report the persistence difference"; H96's estimator as a shared `old_state.py` (H96, H110, H82 all build ê_old, placebo old states and the field span).
