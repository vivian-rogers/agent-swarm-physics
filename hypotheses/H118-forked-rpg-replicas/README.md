# H118: The forked RPG is two replicas of one dynamics: damage spreading between rooms (NE15, #35)

**Status:** exploratory round 1 done (2026-10-04, non-holdout only): **mixed.** The two forked rooms are not replicas that slowly separate. Their content overlap is already far below the identical-replica level in the first active hour after the fork (q 0.51 vs relabel 0.80; day 1 0.37), and the rooms share no same-day state beyond day 1 (equal-time memory M_late 0.07 [−0.03, 0.17]; gte 0.12 [−0.01, 0.22]). The late overlap q_∞ 0.25 [0.11, 0.35] sits in the lower half of the identical-kickoff band (0.01–0.83), below the same-basis day after the goal change (36a: 0.62): no plateau from the game's rules is visible, but the plateau test has power 0.16–0.29 (Amendment 1). The game state behaves the other way: code damage spreads on the edit clock over five days and then freezes, half of the inherited src files stay untouched in both forks (frozen core 0.50), and identity exceeds independent replicas (X 0.12, hypergeometric p 6e-12): correlated damage at shared hot spots. Replication: no same-day memory after the kickoff in 6/7 two-room periods; different-kickoff periods have the lowest late overlap (G38 0.06, G44 −0.15). Card and predictions written 2026-10-04 21:58–22:03 UTC; Amendment 1 at 22:36 UTC after the synthetic, before real data. `analysis/confirm.py` frozen (SHA-256 23:08 UTC) and dry-run, not run. Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH358.
**Question (GOALS.md):** **Q2** (what is field and what is coupling: after the fork, is the two rooms' common state held by a shared field, the game's rules, or do the players' independent noise and coupling take it apart?), with **Q3** second (a frozen or ordered phase in which a shared initial state survives would be collective order the fields do not explain).
**Fields:** stat mech (damage spreading between replicas of a kinetic spin model; frozen, chaotic and field-ordered phases), dynamics (relaxation of a two-time overlap), info theory (copy identity of keyed game state)
**Literature:** `physics-models/02-nonequilibrium-ising/README.md` (kinetic Ising; replicas under one dynamics), `physics-models/11-vector-spins/README.md` (content spins; field-induced overlap q_∞ = |m|²). Damage spreading: Kauffman, *J. Theor. Biol.* 22, 437 (1969)†; Derrida & Weisbuch, *Europhys. Lett.* 4, 657 (1987)†; Stanley et al., *J. Phys. A* 20, L1013 (1987)† (Ising damage spreading); Grassberger, *J. Phys. A* 28, L67 (1995)† (damage depends on the shared-noise convention). († = cited from memory; not in `literature/`.) Project cards: H07 (fork lineages; independent-lineage identity; hot spots), H100 (#best/#rest split is mostly endogenous), H107 (#35 split is full size on day 1, direction half kept), H108 (#35 room direction not pinned, P(1) 0.32), H48 (content settles in hours), H96/H103 (goal switch is a quench; content decays with work).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent (Claude Code excluded); Regime; Driving / external field; Interaction (broadcast: co-located = same room); Agent state, *vector* variant (DQ5 `style_resid` 32-d regime-whitened statement vectors, both embedding models); Lineage and Copy information (fork variant) (H07). H100/H107 named variants used as defined there: **room of a statement**, **joint relabel**. New named variants proposed here (defined under Observables; DEFINITIONS.md not edited): **replica overlap q (content)**, **equal-time memory M**, **damage time τ_D**, **plateau excess P**, **code overlap q_code**, **independent-replica identity q_ind**, **identity excess X**.
**From:** HH358 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (primary: replicas and damage spreading), `physics-models/11-vector-spins/` (content spins)
**Data inputs (shared tables first):** `embeddings/statements.parquet` + `statements_style_resid32_{bge_small,gte_modernbert}.npy`; `rooms_timeline` via `infra/shared/rooms_asof.py` (null `t_end` → +inf); `calendar` (active windows); `period_units`; `roster`; `embeddings/goals.parquet` (kickoff rows, descriptive only); `hypotheses/holdout.json` via `holdout_mask`. Game state: H07's processed lineage tables `data/processed/H07-rpg-forks/{fp_trees,commits,blob_functions}.parquet` (read as data files; no H07 code is imported, STANDARDS §8). No text is read.

## Source HH (verbatim from the HH list, including refinements)
- **HH358 · The forked RPG is two replicas of one dynamics: damage spreading between rooms (NE15, #35).** At NE15 the RPG forked per room: the same game and rules, two copies, different players. In kinetic Ising, two replicas started from the same state either stay together (ordered or frozen phase) or separate at a rate set by the noise (damage spreading).
  - *Prediction:* the two rooms' game-state and content overlap q(t) decays to the cross-room baseline within about a day (fast damage spreading), with no plateau. A plateau would be a shared field from the game rules.
  - *Check:* game-state features and content centroids per room per hour from the fork time; compare with H100's room split onset.
  - *Kill:* q(t) stays above baseline for the whole period (the rules, not the players, set the state).
  - *Impostors:* the rules are a common field, and the plateau measures it.
  - *Models:* 02, 11 · *Builds on:* H100, H07 (forks), HH337

## Question
At 16:20 UTC on 2026-03-16 the village split into #best (3 agents) and #rest (9–10 agents), and each room took its own copy of the RPG built in #34. Treat the two rooms as two replicas of one dynamics that start from the same state. Does their overlap decay to the level two independent rooms would show within about a day (fast damage spreading), or does a shared component survive (a plateau set by the game's rules, or a frozen core of untouched state)?

## Design: two layers (STANDARDS §4)
- **Natives** (role `native`), each with its own dated prediction:
  - **G35 content (NE15):** the hourly replica overlap q(t) of the rooms' content from the fork, the equal-time memory M(d), the damage time τ_D, and the plateau against the identical-kickoff band.
  - **G35 game state (NE15):** the hourly code overlap of the two forks on ancestor keys (files, src files, functions) against the independent-replica identity, and the frozen core.
  - **G38 + G44 (positive control for the overlap instrument):** the rooms got different kickoffs, so they are not replicas of one dynamics; their late overlap should sit below the identical-kickoff band.
- **Replication** (role `replication`): every non-holdout two-room goal period restarts both rooms from one shared state (the previous period plus one kickoff). The same content estimator (M(d), τ_D, late overlap q_∞) runs on G36, G37, G39, G41, G42 (identical kickoffs; these also form the baseline band) and on G38, G44. G36 is split by regime (36a regime II, 36b–c regime III); its estimator uses the regime-III days, and 36a is reported as the one same-basis (regime II) band point for G35.
- **Not used:** #34 (held out) is the pre-fork state, so q(0) is not measured; the decay starts at the first active hour after the fork. #43 and #45–#50 are held out; 51g's #focus room has 2 agents (not eligible).
- **Exception (CLAUDE.md (c)):** the NE15 fork is a boundary design: the object is the relaxation after the fork. The baseline band compares fitted quantities across periods (a phase-diagram comparison), not pooled data.

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (replicas of a kinetic spin model) with `physics-models/11-vector-spins/` for content.

Two replicas A (#best) and B (#rest) of one kinetic dynamics start from one configuration at T0. Each replica updates with its own noise (its players). The overlap q(t) between them follows three regimes:
- **Chaotic phase (damage spreads):** q(t) = q_∞ + (q_0 − q_∞) e^{−t/τ_D}, with τ_D set by the update rate. With no shared field q_∞ = 0 (in a basis centred away from the shared state).
- **Field-ordered phase:** a field h common to both replicas gives q_∞ = |m(h)|² > 0. Two independent replicas in the same field keep this overlap forever. This is the HH's plateau: the rules (and the goal) as a common field.
- **Frozen phase:** spins that never update keep their initial value in both replicas, so q stays near q_0 for those degrees of freedom. In the game state this is the inherited code nobody touches.

**Content mapping.** Agent i's statement vector x_s ∈ ℝ³² (DQ5 style_resid, regime basis), re-centred on a **leave-own-period-out reference** μ_ref (the mean of the same regime's non-holdout statements outside the period; regime III also excludes #51, infra Known issue on the #51-dominated centre). The room state in active-hour bin b is the agent-weighted centroid c_r(b). Centring away from the period keeps the shared static component (goal, game) in both centroids, so q_∞ measures it.

**Game-state mapping.** Each ancestor key k (a file path, a src file, a function's qualified name) is a spin σ_k ∈ {inherited value, new value}. In each replica a key mutates with hazard μ_k on the edit clock. Independent replicas with no shared rules field are identical at k only if both kept the inherited value, or both reached the same new value by chance. So q_code(t) ≥ q_ind(t) = (1/K)Σ_k 1[unchanged in A](t) · (1/K)Σ_k 1[unchanged in B](t) (the product of the copy fractions, for keys mutating independently of each other across replicas). **Correlated damage** (both forks edit the same keys: shared hot spots, the same inherited defects, the same rules) gives q_code(both unchanged) > q_ind. Identical new values beyond chance are a second rules-field signature (H07: 3 shared innovations, all convergent repairs).

**Rivals.**
- **R-fast (HH): fast damage spreading, no plateau.** τ_D ≤ 1 active day; M(d ≥ 2) ≈ 0; q_∞ inside the identical-kickoff band.
- **R-rules (plateau): the rules are a shared field.** q_∞ above the band in every #35 day (HH kill); in game state, identity excess X > 0.
- **R-frozen: a frozen core.** Content: q_eq stays near its first-hour value for days (τ_D ≥ 2 days). Game state: a large set of keys never changes in either fork.
- **R-drive: a shared time-varying drive** (operator messages to both rooms, the day schedule, outside events). M(d) stays positive on later days without decaying from day 1.
- **R-comp (composition):** the rooms differ from the first hour because their members differ (3 vs 9–10 different models), not because noise spreads. In regime II no agent constants exist outside #33 and #36a (4 days), so composition stays in; it moves q_eq down from hour 1, which reads as R-fast.

## Data scheme (`scheme/`)
`scheme/build.py` → `data/processed/H118-forked-rpg-replicas/` (≤ 10 MB, `_provenance.json`). Non-holdout rows only, asserted with `holdout_mask`. No vectors are copied: the scheme stores row indices into the shared statement arrays and a small per-(period, room, bin, half) centroid table.
- **Statements** (`statements.parquet`): every non-holdout agent statement (chat and intentions) of goals #33–#44 (Claude Code agent excluded), with `srow`, agent, t, PT day, goal, regime, the room at the statement (shared `rooms_asof.statement_rooms`: chat = message room, intentions = as-of room), the active-hour bin (hour index since the day's calendar `win_start`, capped at the window), the day index within the period, and the agent's period room (majority room over the period; agents with < 80% of their in-room statements in one of the two rooms are dropped from that period, H100/H107 rule).
- **Reference centres** (`ref_centres.npz`): μ_ref per (period, model): the mean style_resid vector of the same regime's non-holdout statements outside the period (regime III: also outside #51).
- **Centroids** (`centroids_<model>.npz`): per (period, room, bin, half): agent-weighted centroid (mean over agents of each agent's mean statement vector in that half), statement and agent counts. Halves: statement parity within (agent, bin); an agent with one statement in a bin goes to half 1 or 2 by agent-code parity.
- **Game state** (`code_hourly.parquet`): from H07's `fp_trees` (first-parent trees of `rpg-game-best` and `rpg-game-rest`, the 7 day-1 #best commits on `rpg-game` included as H07 did), the tree of each fork at the end of every active hour from T0 to the end of #35 (and at the end of each later non-holdout day to 05-28): for ancestor keys (files, `src/**/*.js` files, functions keyed by qualified name with a body hash from `blob_functions`): unchanged-in-best, unchanged-in-rest, identical, both-changed-to-the-same-value; plus cumulative fork commits and file touches.
- **Regimes covered:** II (#35, #36a) and III (#36b–#44, non-holdout).

## Observables
*Written 2026-10-04 ~22:00 UTC, before any H118 statistic on real data.* Primary: bge style_resid; gte reported alongside.
- **O1 Replica overlap q.** For a set Π of bin pairs (b, b′) with b from #best and b′ from #rest: N(Π) = mean over Π of ½[c_A¹(b)·c_B²(b′) + c_A²(b)·c_B¹(b′)]; S_A(b) = c_A¹(b)·c_A²(b) (unbiased squared norm of A's centroid; likewise S_B). **q(Π) = N(Π) / √(⟨S_A⟩_Π ⟨S_B⟩_Π)** (ratio of means: a disattenuated cosine; split halves remove the statement-noise bias that unit-vector cosines carry, infra Known issue on amplitude bias). Bins with fewer than 4 statements in either room are dropped.
  - **q_eq(h)** hourly (Π = {(b, b)}); **q_eq(d)** daily (all same-hour pairs of day d).
  - **q_lag(d)**: Π = {(b, b′): b in day d, b′ in a different day} ∪ {(b′, b): …} (#best on day d against #rest on other days, and the reverse). It keeps every static shared component and removes same-day shared state.
  - **q_rel(d)**: the mean of q_eq(d) over 500 joint relabels of the period's agents (room sizes kept, the same relabel in every bin; H107 rule). It is the overlap two rooms of these agents would show with no room effect: the "identical replicas" reference.
- **O2 Equal-time memory M(d) = q_eq(d) − q_lag(d).** M > 0 means the rooms share same-day state beyond their static common component: memory of the common initial state (it decays from day 1) or a shared time-varying drive (it does not decay).
- **O3 Damage time τ_D.** Fit q_eq(t_b) = q_∞ + (q_0 − q_∞) e^{−t_b/τ_D} to the hourly overlaps, t_b = active hours since the kickoff (bin mid-point), weights = harmonic mean of the two rooms' statement counts; τ_D profiled on a log grid 0.25–80 active h. Reported with the fitted q_0, q_∞. "Fast" = τ_D ≤ 4 active h (one 4-h day).
- **O4 Late overlap q_∞^late** = q_eq over the last ⌈n/2⌉ days of the period (model-free companion of the fitted q_∞).
- **O5 Plateau excess P = q_∞^late(G35) − max over the band** of q_∞^late, the band = identical-kickoff periods G36 (regime-III days), G37, G39, G41, G42. Also G35's rank in the band and the same-basis point 36a (regime II, one day: its whole-day q_eq).
- **O6 Code overlap (game state).** For each ancestor-key family at the end of active hour h: c_A(h), c_B(h) = share of ancestor keys unchanged in each fork; **q_code(h)** = share identical in both forks; **q_ind(h) = c_A(h)·c_B(h)**; **identity excess X(h) = q_code(h) − q_ind(h)**, split into the both-unchanged part (correlated hot spots) and the both-changed-identically part (convergent innovation); **frozen core F(h)** = share unchanged in both. Damage D_code(h) = 1 − q_code(h); its half-rise time on active hours and on cumulative file touches.
- **Robustness:** both embedding models; white32 instead of style_resid; 2-h bins instead of 1-h; q with each room's own leave-period-out centre instead of the regime reference (does not change q_eq but changes q_∞ level).

## Null / baseline
- **N1 Joint relabel** (q_rel): 500 joint relabels of agents, room sizes kept.
- **N2 Statement bootstrap and agent bootstrap** (CIs): (a) statements resampled within (agent, bin), 300 replicates; (b) agents resampled within rooms, 300 replicates (wide with 3 #best agents; reported as the conservative interval). Verdicts use the agent bootstrap.
- **N3 Cross-room baseline (the HH's "baseline")**: the identical-kickoff band (O5) for the plateau, and q_lag for the equal-time memory (O2).
- **N4 Independent-replica identity** q_ind for game state; a key-permutation null for X (keys' unchanged flags permuted within each fork among keys of the same family and inherited size decile, 1,000 draws), which keeps each fork's mutation count and removes cross-fork key correlation.
- **N5 Synthetic worlds (axis F; run first):** on the real statement skeletons (agent × room × bin × count) of G35 and the band periods: (W0) fast damage spreading, τ_D = 2 h, shared goal component g of equal size in every period; (W1) slow, τ_D = 2 days; (W2) W0 plus an extra shared rules component in G35 only (|h_rules| = |g|); (W3) a shared day-level drive in both rooms, no memory; (W4) a frozen world (τ_D = 80 h). Statement noise and agent-constant variances from H107's regime-III calibration (s_ε² = 0.0195, s_η² = 0.0026, τ² = 0.0014 per coordinate), shared and room components on a grid relative to them.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | no | Content directions and code identity, not timing. Bins are active hours, so night gaps carry no weight; a shared day schedule would appear as R-drive (M persistent), which O2 separates from memory. | n/a |
| Exogenous field (kickoff/goal/operator) | yes: the plateau measures it | The HH's own point: the rules are a common field and the plateau measures it. The goal field is matched by the identical-kickoff band (rooms share a goal, not an artifact); kickoff-day transients enter M(1) and are read as the shared initial state. Operator messages to both rooms would look like R-drive; not regressed out (descriptive count only). | partly |
| Shared model priors (family, style) | yes | DQ5 style_resid vectors; both embedding models. All agents share LLM content priors, which raise q_∞ in every period alike; the band comparison cancels this only if prior strength is the same across periods. No agent constants in regime II. | partly |
| Contemporaneous convergence | yes | Two rooms that never read each other can still converge on the same content because they face the same game. H07 (round 1b): cross-team reads are 2% of #35 items, and 0/3 shared innovations had a readable channel. q measures overlap whatever its cause; convergence is part of the rules field here, not a coupling claim. | n/a (no coupling claim) |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-fast, R-rules, R-frozen, R-drive, R-comp (above).
**Locked holdout used for confirmation:** none run. `analysis/confirm.py` (frozen 2026-10-04 23:08 UTC; guarded by `--confirm`, `H118_CONFIRM=1`, a SHA-256 freeze of `confirm.py`, `h118lib.py` and `confirm_band.json`, and the holdout ledger) targets the held-out two-room periods #45, #46, #47 and #50: C1 M_late covers 0 in ≥ 3/4 scorable targets [0.7]; C2 q_∞^late inside the frozen round-1 band (bge 0.01–0.83) ± 0.05 in ≥ 3/4 [0.5]; C3 q_∞^late below the joint-relabel reference in ≥ 3/4 [0.8]. Dry run on #39, #41, #42, #44: pass/pass/pass. The #34 → #35 fork boundary itself is not a target (its pre-state #34 is held out, but no H118 statistic uses #34).

| Axis | Test (plan) | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | rooms, bins, reference centre and keyed game state from dataset fields; both models | 1 | see Round 1 scorecard |
| B assumptions | single-exponential relaxation; stationarity of the late block; bin size | 1 | τ_D unidentifiable at G35 counts |
| C adequacy | q_eq vs q_rel and q_lag; X vs the key-permutation null | 1 | day-1 overlap far below relabel; X p 6e-12 |
| D unfitted predictions | τ_D, M(d), plateau rank are not fitted to the HH thresholds | 1 | P3 3/4, P5 met; τ_D, plateau unpowered |
| E interventional | the NE15 fork itself; kickoff restarts in 7 periods | 1 | content apart in hour 1; code on the edit clock |
| F identifiability | real-skeleton synthetic: fast vs slow vs plateau vs drive worlds | 1 | memory test calibrated; τ_D and plateau underpowered |
| G ground truth | different-kickoff periods (G38, G44) must sit below the band; H07's fork lineages | 1 | control met |
| H comparative | R-fast vs R-rules vs R-frozen vs R-drive | 1 | R-drive rejected; R-frozen/R-rules in code only |
| I transfer | replication periods; holdout | 1 | 6/7 replications; holdout not run |

## Prediction
*Written 2026-10-04 ~22:02 UTC, before the synthetic validation and before any H118 statistic on real data.*

**What I had seen when writing this (so these are not blind):** H07's card and results (end-of-#35 file copy fractions 0.69 #best / 0.81 #rest; horizontal identity on ancestor keys equals P(both unchanged) at day level; co-change 2.4× independence; 3 convergent shared innovations; 2% cross-team reads), H107's G35 numbers (day-1 split full size, r₁ 1.39, π₁ 0.43; gte 1.95 / 0.62), H108's #35 P(1) 0.32 (direction not pinned), H100's status line, H48's settling times (τ ≈ 2–4.5 h), H96's quench result. Skeleton counts only for G35 (chat 554 in #best, 1,544 in #rest, 137 in #general; 1,357 intentions; 5 days × 4 active hours). No overlap, memory or code-identity statistic had been computed.

- **P0, synthetic (axis F; run first).** On the real skeletons: (a) M(d ≥ 2) has a 95% statement-bootstrap interval covering 0 in ≥ 90% of W0 runs [0.7]; (b) the τ_D fit classifies W0 (2 h) as fast (≤ 4 h) in ≥ 70% and W1 (2 days) as slow (≥ 8 h) in ≥ 70% at G35's counts [0.6]; (c) the plateau rule (O5: q_∞^late(G35) > band max) fires in ≤ 10% of W0 runs and in ≥ 70% of W2 runs [0.5]; (d) W3 gives M(d ≥ 2) > 0 in ≥ 70% of runs (the drive is visible) [0.6]. Where (b) or (c) fails at G35's counts, that clause's verdict is "inconclusive".
- **P1, G35 content: fast damage spreading.** τ_D ≤ 4 active hours (point), with the agent-bootstrap upper bound ≤ 8 h; M(d) agent-bootstrap interval covers 0 for every d ≥ 2 [0.55].
- **P2, G35 content: no plateau (HH).** q_∞^late(G35) ≤ the band max [0.4]. *HH kill:* the lower agent-bootstrap bound of q_eq(d) is above the band max on every day of #35 [0.35].
- **P3, G35 game state (informed by H07; not blind).** Code damage is slow and partly frozen: src-file q_code at the end of active hour 4 (end of day 1) ≥ 0.85, and at the end of #35 in [0.45, 0.75]; frozen core F ≥ 0.40 at the end of #35; identity excess X > 0 at the end of #35 with key-permutation p < 0.05 (correlated damage: shared hot spots) [0.75]. The HH's "game state decays within a day" clause therefore fails [0.8].
- **P4, replication (G36–G39, G41, G42, G44).** M(d ≥ 2) interval covers 0 in ≥ 5/7 periods, and τ_D ≤ 4 active h in ≥ 5/7 [0.45].
- **P5, positive control (G38, G44: different room kickoffs).** q_∞^late below the identical-kickoff band median in both [0.6].

**Verdict rules.**
- *G35 (native):* content **supported** (R-fast) if P1 and P2 hold; **failed** if the HH kill fires or τ_D ≥ 2 active days (R-frozen); **mixed** otherwise. Game state **supported** if src q_code reaches within 0.05 of its end-of-#35 value by the end of day 1 and X ≤ 0.02; **failed** if q_code at the end of day 1 exceeds its end-of-#35 value by ≥ 0.10 or X > 0.05 with p < 0.05; **mixed** otherwise. The period verdict is supported only if both are supported, failed if both fail, mixed otherwise.
- *Replication periods:* **supported** if M(d ≥ 2) covers 0 and τ_D ≤ 4 h; **failed** if τ_D ≥ 2 days or M(d ≥ 2) > 0 on every later day; **mixed** otherwise; **descriptive** if q_eq is undefined (fewer than 3 usable bins per day).
- *G38/G44 (control):* supported if q_∞^late < band median.
- *Hypothesis level (HH358):* **supported** if G35 is supported; **failed** if G35 fails; **mixed** otherwise. The replication count and the control are reported alongside and set credence, not the verdict.
- *Two models:* verdicts use bge; a clause that gte reverses is downgraded to mixed.

### Amendment 1 (after the synthetic validation, before any H118 statistic on real data)
*2026-10-04 22:36 UTC.* `analysis/synthetic.py` (40 worlds per setting, 100 bootstraps) and `analysis/synthetic_a1.py` (100 worlds; written after the first run to test replacement rules), on the real statement skeletons of G35 and the five band periods. Outputs: `data/processed/H118-forked-rpg-replicas/synthetic/summary{,_a1}.json`.

| World (planted) | τ_D ≤ 4 h | τ_D ≥ 8 h | all-days M(d ≥ 2) covers 0 (agent × bin) | M_late rejects 0 (agent × bin) | plateau: point > band max | plateau: PI rule | day-2 excess rule |
| --- | --- | --- | --- | --- | --- | --- | --- |
| W0 fast (2 h) | 0.78 | 0.20 | 0.70 | 0.13 (eq) / 0.10 (var) | 0.23 / 0.23 | 0.02 / 0.08 | 0.06 |
| W1 slow (2 d) | 0.33 | 0.58 | 0.60 | 0.01 | 0.15 | 0.00 | 0.21 |
| W2 rules field | 0.70 | 0.20 | 0.63 | 0.07 / 0.09 | 0.68 / 0.48 | 0.29 / 0.16 | 0.10 |
| W3 shared drive | 0.58 | 0.28 | 0.00 | 1.00 | 0.08 | 0.03 | 0.16 |
| W4 frozen (200 h) | 0.40 | 0.45 | 0.93 | 0.01 | 0.13 | 0.00 | 0.05 |

- **P0(a) fails as written.** Statement-only bootstraps condition on the realized room trajectories, so they are far too narrow (all-days coverage 0.05–0.13). With bins resampled within days and agents within rooms (agent × bin), all-days coverage is 0.70. **Change:** the memory test is **M_late** = the mean of M(d) over d ≥ 2, with the agent × bin bootstrap interval (false rejection 0.07–0.13 in no-memory worlds; a shared drive is caught in 100%). Per-day M(d) intervals are reported but not scored.
- **P0(b) fails for slow worlds.** τ_D classifies fast worlds as fast in 70–78%, but 2-day memory as slow in only 58% and a frozen world in 45%. M cannot see slow memory either (memory shared across days enters q_lag too), and a day-2 excess rule has power 0.05–0.21. **Consequence:** at G35's counts a fast τ_D cannot be told from slow or frozen memory of this planted size. By P0's rule, the τ_D clause is **inconclusive** whatever the real τ_D.
- **P0(c) fails.** Under exchangeable periods the point rule (G35 above the band max) fires 1/6 of the time by symmetry (observed 0.15–0.23). The lower-bound rule has power 0.2. A prediction-interval rule (q_∞^late(G35) > band mean + t₄,0.95 · sd · √(1 + 1/5)) has size 0.02–0.08 but power 0.16–0.29. **Change:** the plateau test is the PI rule. A non-firing is **inconclusive** (power < 0.7); a firing is evidence for a plateau (size ≤ 0.08). The HH kill (every day above the band max) is reported, not scored, for the same reason.
- **P0(d) passes:** a shared day-level drive gives M_late > 0 in 100% of runs.
- **Verdict rules, amended.** G35 content: **supported** if M_late covers 0 and τ_D ≤ 4 h and the PI rule does not fire (written as "mixed: fast-looking but inconclusive" because τ_D and the plateau are unpowered); **failed** if the PI rule fires (a plateau above the band) or M_late > 0 (R-drive); **mixed** otherwise. Replication periods: **supported** if M_late covers 0, **failed** if M_late > 0; τ_D descriptive. Game-state rules are unchanged (they do not use these estimators).
- **Not changed:** predictions P1–P5 and their credences, the observables and the nulls.

## Results by goal period
Primary: bge style_resid, 1-h active bins, agent × bin bootstrap 95% intervals; gte in brackets. q_∞^late = late-block overlap; M_late = equal-time memory over days ≥ 2; q_rel = joint-relabel (identical replicas) reference.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G35](goalperiod-subhypotheses/G35/README.md) | native (NE15 fork) | mixed | content: q_eq(h 1) 0.51 vs q_rel 0.80; M_late 0.07 [−0.03, 0.17] (0.12); q_∞ 0.25 [0.11, 0.35] (0.29), band rank 2/5; τ_D 0.6 h [0.25, 80] (gte 5.2 h, no decay). Code: src q_code 0.84 at the end of day 1, 0.50 at the end of #35; X 0.12 (p 6e-12); frozen core 0.50 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | supported | M_late 0.02 [−0.05, 0.12] (−0.00); q_∞ 0.65 (0.65) vs q_rel 0.74 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | supported | M_late 0.07 [−0.03, 0.23] (0.06); q_∞ 0.20 (0.11) |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication + native (control) | supported | M_late 0.01 [−0.01, 0.03] (0.01); q_∞ 0.06 [−0.03, 0.13] (0.17) < band median 0.37 (0.60) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | supported | M_late 0.02 [−0.04, 0.08] (0.00); q_∞ 0.37 (0.60) |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | M_late −0.04 [−0.11, 0.03]; gte −0.14 [−0.19, −0.05] (same-day anti-alignment); q_∞ 0.01 (−0.22) |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | supported | M_late 0.04 [−0.01, 0.07] (0.01); q_∞ 0.83 (0.79) vs q_rel 0.85 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication + native (control) | mixed | M_late −0.07 [−0.12, −0.00] (−0.02); q_∞ −0.15 [−0.24, −0.02] (−0.21) < band median (control met) |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only)
- **Scheme:** 24,620 non-holdout statements in #best/#rest (goals #35–#44; 12 one-room agents in #35: 3 + 9); 873 room × bin × half centroids per model; hourly code states of the two main forks from H07's first-parent trees (68 time points). 0.9 MB in `data/processed/H118-forked-rpg-replicas/`. Code: `scheme/build.py`, `analysis/{h118lib,synthetic,synthetic_a1,run,write_estimates,figures,confirm}.py`. Runtime ≈ 1 min for the real-data run.
- **Data fix during the run (instrument, labelled):** the first scheme build keyed functions by the tree's commit index instead of H07's occurrence index (a column-name clash in a join), so every function looked changed. Fixed before any function-level number was read; the content part is unaffected (`run.py --code-only` recomputed the game state).

**G35 content (NE15).**
- The rooms start apart. In the first active hour after the fork q_eq = 0.51 (gte 0.37), against 0.80 for random rooms of the same agents. Day by day q_eq is 0.37, 0.49, 0.13, 0.39, 0.27 (gte 0.27, 0.38, 0.20, 0.49, 0.24), with no trend.
- No same-day memory after day 1: M_late 0.065 [−0.032, 0.165] (gte 0.123 [−0.012, 0.217]).
- τ_D is not identified: 0.6 h in bge with an interval spanning the whole grid; gte fits no decay (5.2 h, overlap rising). The synthetic had already shown that τ_D cannot separate fast from slow memory at these counts (Amendment 1).
- No plateau above the identical-kickoff band. q_∞^late 0.25 [0.11, 0.35] (gte 0.29 [0.14, 0.39]) ranks 2/5 in the band (bge 0.01–0.83; gte −0.22–0.79), far below the PI threshold (1.16). The same rooms one day after the goal change (36a, regime II, the same basis) overlap more: 0.62 (gte 0.66). The game held the rooms no closer than a shared kickoff does. The HH kill (every day above the band max) does not fire. Power for the plateau is 0.16–0.29, so "no plateau" is inconclusive, not a negative.
- Robustness: white32 q_∞ 0.43, M_late 0.05 [−0.02, 0.12]; 2-h bins 0.30, M_late 0.05 [−0.09, 0.20]; period-centred (static shared part removed) q_∞ −0.09, M_late 0.10 [−0.07, 0.21].

**G35 game state (NE15).** Ancestor keys: 190 src files, 1,836 functions, 474 files.
| Time | src q_code | src q_ind | X (src) | frozen core (src) | functions q_code / q_ind | X (functions) |
| --- | --- | --- | --- | --- | --- | --- |
| end of hour 1 | 0.974 | 0.963 | 0.010 | 0.974 | 0.996 / 0.995 | 0.001 |
| end of day 1 (4 h) | 0.837 | 0.804 | 0.032 | 0.832 | 0.973 / 0.968 | 0.005 |
| end of day 3 | 0.700 | 0.627 | 0.073 | 0.700 | 0.940 / 0.925 | 0.014 |
| end of #35 (20 h) | 0.500 | 0.384 | **0.116** (p 6e-12) | 0.500 | 0.893 / 0.865 | **0.029** (p 1e-41) |
| 05-28 (last fork commit) | 0.474 | 0.354 | 0.120 | 0.474 | 0.873 / 0.843 | 0.029 |
- Code damage grows steadily through the five days (half of its end-of-#35 value after ≈ 6.5 active hours) and freezes once the goal changes (+0.03 damage in the next two months).
- Almost all of the excess identity is both-unchanged (functions: both changed to the same body 0.0011, two functions): the forks edit the same inherited files and leave the same files alone. That is a shared field in where damage lands (hot spots, H07's 2.4× co-change), not in what the edits are.

**Replication (kickoff restarts).** M_late covers 0 in 6/7 two-room periods in bge (G36, G37, G38, G39, G41, G42). G44 is negative (−0.07 [−0.12, −0.00]); gte adds G41 (−0.14 [−0.19, −0.05]). Negative memory means that on a given day the rooms move apart more than across days: room-specific daily drives (G44 had room kickoffs and heavy operator traffic in #best, H100). τ_D ≤ 4 h in 3/7 (descriptive; unpowered). Late overlaps range from −0.15 to 0.83, so periods differ more than any G35 effect.

**Control (G38, G44: different room kickoffs).** Both have the lowest late overlaps of all eight periods (0.06 and −0.15; gte 0.17 and −0.21), below the band median in both models. Supported.

**Prediction verdicts.**
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P0 synthetic (a)–(d) | (a) failed, fixed by M_late (size 0.07–0.13); (b) failed for slow worlds; (c) failed (PI power 0.16–0.29); (d) passed | 1/4 as written (Amendment 1) |
| P1 τ_D ≤ 4 h, M(d ≥ 2) covers 0 | τ_D 0.6 h but unidentified (gte 5.2 h, no decay); M_late covers 0 | mixed (τ_D inconclusive) |
| P2 no plateau (≤ band max); HH kill | q_∞ 0.25 rank 2/5; kill does not fire | consistent; inconclusive (power 0.16–0.29) |
| P3 game state slow, frozen core, X > 0 | day 1 0.837 (predicted ≥ 0.85: narrowly missed); end 0.50 ∈ [0.45, 0.75]; F 0.50 ≥ 0.40; X 0.116, p 6e-12 | 3/4 supported (informed by H07) |
| P4 replication M covers 0 ≥ 5/7; τ_D ≤ 4 h ≥ 5/7 | 6/7 in each model (bge: G44 negative; gte: G41 negative); τ_D 3/7 | half (τ_D descriptive) |
| P5 control below band median | G38 0.06, G44 −0.15 (gte 0.17, −0.21) | supported |
| HH358 | content: no same-day memory, no visible plateau, τ_D unidentified; game state: slow, frozen and correlated damage | mixed |

**Scorecard (round 1).**
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | Rooms, active-hour bins, leave-own-period-out reference and keyed game state from dataset fields, both embedding models. Composition is not removed in regime II (no agent constants). |
| B assumptions | 1 | Single-exponential relaxation not identifiable at G35's counts; bin size (1 h vs 2 h) and whitening variant do not change the conclusions; the late block is assumed stationary. |
| C adequacy | 1 | Day-1 overlap far below the relabel reference in every model and variant; M_late calibrated on the real skeleton (size 0.07–0.13); code excess against an exact hypergeometric null (p 6e-12). |
| D unfitted predictions | 1 | P3 3/4, P5 supported, P4 memory clause supported; τ_D and plateau clauses unpowered. |
| E interventional | 1 | The NE15 fork and seven kickoff restarts: content separates within the first active hour; code separates on the edit clock and freezes when the goal changes. |
| F identifiability | 1 | Real-skeleton synthetic run first: the memory test is calibrated and catches a shared drive in 100% of runs, but τ_D and the plateau rule have power ≤ 0.6 and ≤ 0.29. |
| G ground truth | 1 | The two different-kickoff periods have the lowest overlaps (control met). The fork lineages come from H07's git trees. |
| H comparative | 1 | R-drive rejected in G35 and 6/7 replications; R-frozen holds for the game state and not for content; R-rules holds for code (correlated damage) and is not detectable in content. |
| I transfer | 1 | The memory result replicates in 6/7 two-room periods in each model (bge misses G44, gte misses G41, both by negative memory); holdout not run. |

**Claim that stands:** After the NE15 fork the two rooms' content shared no same-day state beyond day 1 (M_late 0.07 [−0.03, 0.17]) and was far from identical replicas from the first active hour (q 0.51 vs 0.80), while their code diverged slowly with a frozen core (0.50 of src files) and correlated damage (identity excess 0.12, p 6e-12). *Exclusions:* τ_D (unidentified at these counts); the absence of a rules plateau in content (power 0.16–0.29); the day-1 game-state threshold (P3, narrowly missed and informed by H07); the gte sign of G41's memory.

### Round 2 redirects (suggested, 2026-10-04)
- **What the direction is really after:** whether a shared artifact acts as a field on where forked teams work (code hot spots) while their conversations decorrelate at once.
- **H118-R1.** Hierarchical damage time: pool the hourly relaxation across the eight kickoffs with period-specific τ_D and shrinkage (CLAUDE.md exception (d)); one period cannot identify it.
- **H118-R2.** Composition-free overlap: agent constants for regime-II agents from #33 and #36a remove R-comp from G35's day-1 separation.
- **H118-R3.** Where damage lands: test whether H07's #34 touch counts predict the shared hot spots behind the identity excess X (H07's C1).
- **H118-R4.** Same-day anti-alignment (G41, G44): link negative memory to room-specific operator messages per day.

## Notes
- 2026-10-04 21:58 UTC: card opened; HH358's "cross-room baseline" is operationalized twice before data: q_lag (same period, other days) for the equal-time memory, and the identical-kickoff band for the plateau. The HH's two clauses (decay within a day; no plateau) are scored separately.
- 2026-10-04 22:36 UTC: Amendment 1 (synthetic): memory test changed to M_late with the agent × bin bootstrap; τ_D and the plateau declared unpowered; plateau test changed to a prediction-interval rule.
- 2026-10-04 ~23:00 UTC: real-data run; the function-level game state was rebuilt after a join bug (commit index shadowing the occurrence index) found before any function number was read.
- 2026-10-04 23:08 UTC: `analysis/confirm.py` frozen with `confirm_band.json`; dry run on #39, #41, #42, #44 only. Never run with `--confirm`.
