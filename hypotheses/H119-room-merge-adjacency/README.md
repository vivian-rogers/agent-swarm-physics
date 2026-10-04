# H119: The room merge switches a known adjacency on and off: recover it from the dynamics (NE42)

**Status:** exploratory round 1 **done (2026-10-04): failed by HH359's kill rule.** Card and predictions 22:05 UTC; Amendments 0–1 (structural, synthetic) 22:43 UTC; real-data run 22:45–22:46 UTC. `analysis/confirm.py` frozen and dry-run, **not run**.
- **The cross-block coupling does not rise in the merged week.** NE42 merge contrast M = −0.02 [−0.13, 0.09] per pair (synthetic power 0.95 at J = 0.3); full-J cross means −0.02 in all three weeks; daily J_x shows no step (Mann–Whitney p 0.95).
- **Nothing couples in the merged room.** Within-block pairs (co-located all along) are also at 0 in #40 (E1 0.01; E2 read minus in-flight 0.08 [−0.16, 0.31]). They couple in #41 after the split (full-J 0.23 ± 0.04; E2 0.47 [0.27, 0.66]). The merge diluted per-pair coupling below detection (H05's attention reallocation, H51's g_lag collapse), so the adjacency switch is invisible in the dynamics.
- **Replication (other switches):** E1 follows co-location in sign at all 4 testable switches, significant at the two #focus switches (S 0.06, 0.05), but E1 is not specific (room-drive false positives 0.58–0.95). The read-gated attribution holds at one switch (05-25 move: E2 0.73 [0.15, 1.31]). Verdicts: 4 mixed, 1 n/a.
- Remanence and partition memory are untestable: there is no merged-week coupling to remain.
**Question (GOALS.md):** **Q1** (what couples agents: does a kinetic-Ising coupling fitted from talk dynamics follow the known read path, switching on and off with the rooms?) and **Q2** second (coupling vs a room-shared field).
**Fields:** stat mech (inverse kinetic Ising, network recovery against ground truth), dynamics (A-B-A event study), sociophysics (group merge and split)
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md); per-spin logistic inference (Roudi & Hertz 2011)† via `physics-models/02-nonequilibrium-ising/`. Project cards: H05 (rooms couple talk only through reads; NE42 stay pairs decouple when merged, recouple at the split), H100 (no room remanence beyond composition; joint relabel), H102 (sharp, empty room walls; posted-unread placebo), H94 and H51 (NE42 natives: ownership price falls, hub forms; observables follow room size), H08 (read-out gating), H50 (talk coupling at hop 1), H40 (call clock), H47 (NE42 shows no partition memory in content), H41 (hoppers leak half the time), H90 (partition contrasts needed).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent (Claude Code agent excluded); Regime (all units regime III); Driving / external field (goal kickoffs); Interaction (broadcast: co-located = same current room, from `rooms_timeline` via `rooms_asof`); **Interaction (ledger-visible exposure)**, **Unread (in-flight) exposure placebo**, **Exposure (ledger receiving call)**; H100's **room of a statement**. New named variants proposed (DEFINITIONS.md not edited; shared with H117): **talk spin (trimmed minute)**, **KI-5 block coupling**, **read-gated call coupling J^R / in-flight coupling J^U**, plus **block couplings J_x / J_w** (cross-block / within-block, per pair), **merge contrast M**, **remanence Rm**, **switch contrast S**.
**From:** HH359 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/`
**Data inputs (shared tables first):** `activity_bins_fixed`, `calendar`, `period_units`, `roster`, `rooms_timeline` via `infra/shared/rooms_asof.py`, DQ1 `context_ledger_turns` + `call_windows`, `chat_core` (message times and rooms; no text), `holdout.json` via `common.holdout_mask`; `day_matrices.trim_rows`; `estimates.write_estimates`. No text is read.

## Source HH (verbatim from the HH list, including refinements)
- **HH359 · The room merge switches a known adjacency on and off: recover it from the dynamics (NE42).** For one week #best and #rest were one room, then split back. Who can read whom is known at every moment.
  - *Prediction:* the fitted cross-block J is ≈ 0 before, positive during, and ≈ 0 after the merge (no remanence, as H100), and it is carried by read-outs of the other block's messages only.
  - *Check:* sliding-window kinetic Ising on talk spins, block-averaged J_cross(t); read vs in-flight contrast inside the merge week.
  - *Kill:* J_cross does not rise during the merge, or stays raised after the split.
  - *Impostors:* the goal changed in the merged week (H51 NE42), so use only read-gated coupling.
  - *Models:* 02 · *Builds on:* H05, H100, H94 (NE42 hub)

## Question
When the room structure switches who can read whom (a merge, a split, a move), does a kinetic-Ising coupling fitted from talk timing switch with it: zero across a wall, positive inside a room, back to zero after the wall returns? And is the coupling carried by what the recipient actually read, not by a shared room drive?

## Design: two layers (STANDARDS §4)
**NE42 is not held out** (#39–#41 are exploratory). The room structure (metadata, not outcomes) was looked up before writing this card:
- **#39** (04-27 → 05-01): #best = Claude Opus 4.7, GPT-5.5, Gemini 3.1 Pro, Kimi K2.6 (4); #rest = Claude Haiku 4.5, Opus 4.5, Opus 4.6, Sonnet 4.5, Sonnet 4.6, DeepSeek-V3.2, GPT-5, GPT-5.1, GPT-5.2, GPT-5.4, Gemini 2.5 Pro (11).
- **#40** (05-04 → 05-08): all of them in #universe-coordination (room 4) from ~17:02 UTC on 05-04, **except GPT-5, left alone in #rest**.
- **#41** (05-11 → 05-15): split back to the #39 partition at ~17:02 UTC on 05-11.
- Pair classes: **cross** (#best × #rest without GPT-5; 40 pairs): off → on → off. **Within** (6 + 45 pairs): on → on → on. **GPT-5 × #rest** (10 pairs): on → off → on, the mirror arm. **GPT-5 × #best**: off throughout.
- **Replication** (role `replication`): the common estimator (switched vs fixed pairs across the boundary, k = 2 days each side) at every other non-holdout adjacency switch:
  | Unit | Folder | Before | After | Switch |
  | --- | --- | --- | --- | --- |
  | 04-02 move | `G38/` | 03-31, 04-01 | 04-02, 04-03 | Claude Sonnet 4.6 #rest → #best (on: × #best; off: × #rest) |
  | 04-27 moves | `G39/` | 04-23, 04-24 | 04-27, 04-28 | Claude Opus 4.6, Sonnet 4.6, GPT-5.4 #best → #rest |
  | 05-25 move | `G44/` | 05-21, 05-22 (#42) | 05-26, 05-27 (#44) | Gemini 3.1 Pro #best → #rest; the held-out #43 day (05-25) is skipped |
  | #focus opens / closes | `G51/` | 08-03, 08-04 · 08-20, 08-21 | 08-05, 08-06 · 08-24, 08-25 | Gemini 2.5 Pro and Claude Opus 4.8 leave #general (off), then return (on) |
  The 04-02, 04-27 and 05-25 moves coincide with goal switches; the pair contrast (switched vs fixed pairs on the same days) removes the common field.
- **Natives** (role `native`), in `NE42/`: (N1) the A-B-A on block couplings by week; (N2) day-resolved J_x(t); (N3) read vs in-flight inside the merged week (E2); (N4) the GPT-5 mirror arm; (N5) partition memory during the merge (J_x vs J_w in #40).

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (kinetic Ising, parallel update), with the coupling matrix structured by blocks (a stochastic-block J).
- **E1, KI-5 block (primary).** Talk spins s_i(t) on each day's DQ8 all-present minute grid (`activity_bins_fixed.state == 4`). For recipient i:
  logit P(s_i(t+1) = +1) = 2[ h_i + δ_i(b) + K_i s_i(t) + K′_i m_i(t) + Σ_c J_c Σ_{j ∈ c(i)} m_j(t) ],
  m_j = 5-min boxcar of s_j; δ_i(b) per (day, 30-min block); c runs over pair classes (within, cross, GPT-5 arm), so J_c is a **per-pair** coupling shared within the class. Fitted pooled over recipients with recipient-specific fields; L2 λ = 1 on everything except h_i. Also the **full-J** version (one J_ij per directed pair, H117's per-agent fit), block-averaged afterwards, as the HH states it.
- **E2, read-gated call coupling (the HH's "read-gated" requirement).** One row per ledger call of agent i: y = the call posts chat. L = latency_s; R_cj = j's messages visible to i and posted in [t_call − L, t_call); U_cj = j's messages posted in [t_call, t_call + L) (unread at output; same-room in-flight or other-room never visible). logit P(y_c) = δ_i(b) + a_i y_{c−1} + Σ_c [J^R_c log(1 + R_c) + J^U_c log(1 + U_c)], with R_c, U_c summed over the pair class c. Read-gated coupling predicts J^R_c > 0 and J^U_c ≈ 0; a room-shared drive predicts J^R_c ≈ J^U_c (both directions of a pair averaged, so agent-specific lags cancel).
- **What the model predicts here.** J_x ≈ 0 in #39 and #41 (no read path), J_x > 0 in #40, with J_x(#41) back at J_x(#39); J_w > 0 throughout (it may fall in #40 by attention dilution, H05). In E2, the #40 cross coupling is J^R_x > 0 with J^U_x ≈ 0.

**Rivals.**
- **R-field (room-shared drive):** co-located agents share a room-level drive (topic bursts, the goal), so J_x rises in #40 without any read-gated coupling. E1 cannot reject it alone; E2's read vs in-flight contrast can.
- **R-memory (remanence):** relationships formed in #40 persist, so J_x stays raised in #41 (the HH kill's second clause; H100 found no room remanence in content).
- **R-partition (partition memory):** inside the merged room agents keep answering their old room-mates, so J_x(#40) < J_w(#40).
- **R-dilution (H05/H18):** pair coupling scales with 1/room size; predicts J_w falls in #40 and J_x(#40) ≈ J_w(#40) (compatible with the main prediction).
- **R-goal (goal confound):** #40's shared objective raises all coupling; predicts J_w rises in #40 as much as J_x (the within-class change absorbs it in the DiD).

## Data scheme (`scheme/`)
- **Transform:** `scheme/ki_talk.py` (library shared verbatim with H117: spins, co-location, designs, penalized logistic fitter with diagonal-block fields, cluster-robust SEs) and `scheme/build.py` (per-unit tables).
  - Minute grid per day: calendar window, DQ8 all-present trim; talk spins from `activity_bins_fixed`.
  - Eligible agents per unit: present on every unit day, ≥ 10 talk minutes in each week or side, Claude Code excluded.
  - Pair classes from minute-level co-location (`rooms_asof`): fixed (≥ 95% co-located both sides), on (≤ 5% before, ≥ 95% after), off (reverse); the NE42 classes are the named ones above, checked against the minute-level co-location (≥ 95% in the designated weeks).
  - E2 rows from `context_ledger_turns` ⨝ `call_windows` (latency_s in (0, 600] s); R and U from `chat_core` agent messages with H100's message room.
- **Output:** `data/processed/H119-room-merge-adjacency/` (`ne42_weeks.parquet`, `ne42_days.parquet`, `e2_ne42.parquet`, `switch_units.parquet`, `synthetic/*.parquet`, `_provenance.json`).
- **Regimes covered:** III only.

## Observables
1. **Block couplings** J_x(w), J_w(w), J_g5(w) (per pair, logistic units) for w ∈ {#39, #40, #41}, with cluster-robust (day × 30-min block) CIs.
2. **Merge contrast** M = J_x(#40) − ½[J_x(#39) + J_x(#41)]; **DiD** M_D = M − {J_w(#40) − ½[J_w(#39) + J_w(#41)]}.
3. **Remanence** Rm = J_x(#41) − J_x(#39).
4. **Partition memory** P_m = J_x(#40) − J_w(#40).
5. **Daily J_x(d), J_w(d)** (one fit per day) for the 15 NE42 days.
6. **E2:** J^R_x, J^U_x, J^R_w, J^U_w per week; contrast C_RU = J^R_x − J^U_x in #40.
7. **Switch contrast** at the replication units: S = (Δ_on − Δ_fixed) − (Δ_off − Δ_fixed) = Δ_on − Δ_off, with Δ = after − before of the class coupling (one arm where only one exists).

## Null / baseline
- **Sampling:** cluster-robust (day × 30-min block) Wald intervals on contrasts; a 30-min-block bootstrap (200 draws, within side) as a check.
- **Relabel null for M_D:** 999 random 4-vs-10 partitions of the same agents (sizes kept, GPT-5 out), refitting the class model: tests whether the real partition's merge contrast exceeds an arbitrary partition's (all pairs co-located in #40, so a random partition mixes classes). Note DQ8: room relabeling is anti-conservative under room-specific drives, which exist in #39/#41; the relabel null is a secondary.
- **Read vs in-flight (E2):** J^U is the convergence placebo at matched window length (STANDARDS §3 partition contrast).
- **Synthetic** (axis F): Prediction P0.

## Impostor table (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | DQ8 all-present trim; per-(day, 30-min block) recipient fields; cross and within pairs share the schedule, so the DiD removes it. | removed |
| Exogenous field (goal, operator) | yes | #40's shared objective coincides with the merge (H51). The within-class change absorbs a goal-wide coupling change (DiD); E2's read vs in-flight contrast removes a room-shared drive; the replication moves coincide with goal switches and use switched vs fixed pairs. | partly |
| Shared model priors (family, style) | weakly | Talk timing, recipient fields absorb agent constants; same agents in all three weeks. | removed |
| Contemporaneous convergence | yes | E2: read vs posted-but-unread at matched window length, both directions averaged (H90). E1 alone does not remove it. | partly (E1) / removed (E2) |

## Prediction
*Written 2026-10-04 22:05 UTC, before the synthetic validation and before any H119 statistic on real data.*

**What I had seen when writing this (so these are not blind):** H05 round 1b (NE42 split: stay-pair talk κ_x +0.022 at the split vs −0.010 at the merge; merge-week add-arm talk c0_x DiD +0.035 to +0.055; MF2 J_out − J_in rises in #40 by +0.28 vs #39 but #39 → #41 also +0.20), H51 (g_lag 0.144 → 0.003 → 0.189 across NE42), H47 (NE42 r_X 0.57 → 1.37 → 0.17; no partition memory in content), H94 (λ_own collapse, hub 73% in #40), H100/H102 (no remanence; walls sharp), the room timeline above and the calendar. These point toward a merge effect in talk; no kinetic-Ising J, E2 coefficient or daily J had been computed.

- **P0, synthetic (axis F; real #39–#41 skeleton; run first).** (a) With adjacency-gated coupling at J_room = 0.3 (per pair, logistic units), M > 0 is detected (one-sided p < 0.05) in ≥ 80% of worlds [0.55]; (b) in a no-coupling world with a room-shared OU drive (τ 10 min) that follows the rooms, E1's M false-positive rate is reported (expected high: E1 cannot separate R-field) [0.6 that it exceeds 0.2], while E2's C_RU false-positive rate is ≤ 0.10 [0.55]; (c) with remanence (cross coupling kept at half strength in #41), Rm > 0 is detected in ≥ 60% of worlds [0.45]. If (a) fails, the NE42 non-detection is inconclusive; if (b)'s E2 size fails, P6 is not interpretable.
- **P1, merge (HH).** M > 0 with the 95% CI excluding 0 [0.65]; M_D > 0 with CI excluding 0 [0.55]. J_x(#39) and J_x(#41) CIs include 0 [0.55].
- **P2, no remanence (HH).** Rm CI includes 0 and Rm < M/2 [0.6].
- **P3, partition memory (N5).** P_m CI includes 0 (no memory of the old partition inside the merged room) [0.45].
- **P4, GPT-5 mirror arm (N4).** J_g5(#40) < ½[J_g5(#39) + J_g5(#41)] [0.4; low power, one agent].
- **P5, timing (N2).** Mean daily J_x over the 5 merged days exceeds the mean over the 10 unmerged days, Mann–Whitney p < 0.05 [0.55]; the step happens on the first merged day (J_x(05-04) above the #39 daily range) [0.4].
- **P6, read-gated (N3; the HH's "carried by read-outs only").** In #40, J^R_x > 0 (CI excludes 0) [0.6] and C_RU = J^R_x − J^U_x > 0 (CI excludes 0) [0.55]; J^U_x CI includes 0 in all three weeks [0.55].
- **P7, replication (switch contrast).** S > 0 (one-sided p < 0.05) in ≥ 3 of the 5 switch events (04-02, 04-27, 05-25, #focus off, #focus on) [0.4]; S > 0 as a point estimate in ≥ 4/5 [0.55]. Talk volume per mover is small, so power is checked in P0's analog on the 04-27 skeleton.

**Verdict rules.**
- *NE42 native:* **supported** if P1 (M CI excludes 0) and P2 hold and P6's first two clauses hold; **failed** by the HH kill: M's CI includes 0 or M ≤ 0, or Rm > 0 with CI excluding 0 and Rm ≥ M/2; **mixed** otherwise (e.g. M > 0 and no remanence, but E2 cannot separate read from in-flight).
- *Replication unit:* **supported** if S > 0 with one-sided p < 0.05; **failed** if S ≤ 0; **mixed** otherwise.
- *Hypothesis level:* **failed** if the NE42 kill fires. **Supported** if NE42 is supported and ≥ 2 replication units are supported. **Mixed** otherwise.
- *Multiplicity:* E1 class model is primary; full-J block averages, relabel null and daily fits are secondary.

### Amendment 0 (structural; 2026-10-04 22:43 UTC, before any H119 statistic on real data)
Found while building the skeletons. What I saw: kept-minute and per-agent talk-minute counts on several window days, the eligible-agent lists and pair-class counts of each skeleton. No coupling had been fitted on real data.
1. **Trim and thresholds** as in H117 Amendment 0: the all-present trim is computed over agents with ≥ 60 active minutes that day; fixed pair ≥ 90% co-located on both sides; switched ≥ 90% / ≤ 20%.
2. **NE42 eligibility.** 11 agents pass the rule (≥ 10 talk minutes in each week, present on all 15 days). GPT-5 is not eligible, so the mirror arm (P4/N4) is **n/a**. Pair classes: 62 within, 48 cross (directed).
3. **Switch units.** At 04-02 the mover (Claude Sonnet 4.6) is not eligible, so G38 is **n/a**. At 04-27 only GPT-5.4 of the three movers is eligible (6 switched-on directed pairs). The #focus return happens at 18:10 UTC on 08-24, so the on-switch after side moves to 08-25, 08-26.

### Amendment 1 (after the synthetic validation; 2026-10-04 22:43 UTC, before any H119 statistic on real data; not post hoc on outcomes)
P0 (`analysis/synthetic.py`, `synthetic/p0_summary.json`; 40 worlds per arm; real NE42 skeleton, core60 trim).
- **E1 on NE42:** M detected (CI > 0) in 0.95 of worlds at J = 0.3 and 1.00 at J = 0.6. Rm never false-positive (0/80); with planted remanence Rm is detected in 0.975. **P0(a) and P0(c) pass.**
- **Room-drive world (no coupling):** E1 detects M in 0.63 and M_D in 0.80 of worlds. **E1 cannot separate R-field**, as P0(b) expected.
- **E2:** C_RU,x (read minus in-flight, cross class) is detected in 0.73 of worlds at J = 0.3 and 1.00 at J = 0.6. Under the room drive it is never detected (0.00; within class 0.05), although J^U,x alone is positive in 0.35. **P0(b)'s E2 clause passes:** E2 is the coupling test.
- **P_m bias:** in coupling worlds with no partition memory, P_m's CI lies below 0 in 0.05 (J = 0.6) to 0.38 (J = 0.3) of worlds. P3 is read with that bias in mind.
- **Switch units (E1 S):**

  | Unit | Power at J = 0.3 | Power at J = 0.6 | False positives, room drive only |
  | --- | --- | --- | --- |
  | 04-27 | 0.08 | 0.25 | 0.18 |
  | 05-25 | 0.98 | 0.83 | 0.95 (S inflated) |
  | #focus off | 0.48 | 0.33 | 0.93 |
  | #focus on | 0.83 | 0.85 | 0.58 |

  E1's S is not specific to coupling.

**Consequences (binding).**
1. The NE42 verdict rule is unchanged; it already requires E2.
2. **Replication-unit rule amended:** **supported** only if E1 S > 0 (one-sided p < 0.05) **and** E2's read-minus-in-flight contrast for the switched arm, on the side where the arm shares a room, is > 0 with its CI excluding 0. **Mixed** if only one holds. **Failed** if S ≤ 0 and the E2 contrast is ≤ 0.
3. E1 results alone are reported as "the fitted J follows co-location", not as coupling.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-field, R-memory, R-partition, R-dilution, R-goal (above).
**Locked holdout used for confirmation:** none run. `analysis/confirm.py` targets the **#47 → #48–#49 → #50 merge and split** (two rooms → one room #general from 06-22 → two rooms from 06-29: an A-B-A entirely in the holdout) and **NE15** (one room in #34 → #best/#rest from 03-16: the cross arm switches off). Written and dry-run on non-holdout stand-ins; not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | see round 1 |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | see round 1 |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | see round 1 |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | see round 1 |
| E interventional | predicts the change across a natural experiment | 1 | see round 1 |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | see round 1 |
| G ground truth | agrees with known structure | 0 | see round 1 |
| H comparative | beats the named rivals | 1 | see round 1 |
| I transfer | holds in other same-mode periods, including the holdout | 0 | holdout not run |

*Scorecard plan:* G is the centre (the adjacency is known at every minute); E from the A-B-A and the switch events; D from E2's read vs in-flight signature and the GPT-5 mirror arm (unfitted); H from R-field (E2), R-memory (Rm), R-partition (P_m), R-goal (DiD); F from P0; C from CIs and the relabel null; I from the replication units and the confirm targets.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | failed | M −0.02 [−0.13, 0.09]; E2 #40 cross R−U 0.15 [−0.19, 0.48]; #41 within 0.47 [0.27, 0.66] |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | n/a | mover not eligible |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | S 0.22 (p₁ 0.27); E2 −0.35 (n.s.); power 0.08–0.25 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | mixed | S 0.52 (p₁ 0.062); E2 on-arm 0.73 [0.15, 1.31] |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | mixed | #focus S 0.063 [0.029, 0.097] / 0.050 [0.004, 0.097]; E2 n.s. |

## Results
### Exploratory round 1 (2026-10-04, non-holdout; run 22:45–22:46 UTC, after Amendments 0–1)
**Headline.** When #best and #rest shared one room for a week, the kinetic-Ising coupling fitted from talk timing did not switch on between them, and it vanished inside the old rooms too. Coupling per pair came back, within the old rooms, only after the split. A read path is necessary for coupling, but it is not sufficient: in a 14-agent room the per-pair coupling falls below what four hours a day for five days can resolve.

**Synthetic validation (axis F):** Amendment 1 (M power 0.95 at J 0.3; E2 read-minus-in-flight power 0.73 at J 0.3, size 0.00 under a room drive; E1 not specific under a room drive).

**Outcome vs prediction**
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P0 synthetic | (a), (b), (c) pass | supported |
| P1 M > 0; M_D > 0 | −0.019 [−0.127, 0.088]; 0.024 [−0.076, 0.125]; relabel p 0.43 / 0.39 | **failed** |
| P1 J_x(#39), J_x(#41) ≈ 0 | 0.078, 0.092 (CIs include 0) | pass (trivial) |
| P2 no remanence | Rm 0.014 [−0.143, 0.172] | pass (nothing to remain) |
| P3 no partition memory | P_m 0.056 [−0.010, 0.122] | pass (trivial) |
| P4 GPT-5 mirror arm | GPT-5 not eligible | n/a |
| P5 daily step | merged 0.002 vs unmerged 0.126; p 0.95 | failed |
| P6 J^R_x > 0, R − U > 0 in #40 | J^R_x −0.23 [−0.44, −0.02]; R − U 0.15 [−0.19, 0.48] | failed |
| P6 J^U_x ≈ 0 | negative in every week (window-length confound) | failed |
| P7 S > 0 (p < 0.05) at ≥ 3/5; point estimate ≥ 4/5 | 2/4 testable; 4/4 | partly |
| HH kill | M's CI includes 0 | **fires** |

**What this means.** The fitted J follows room structure only where per-pair coupling is large enough to see: inside the 4- and 7-agent rooms after the split, at the #focus switches (two agents, small S) and for one mover's new room-mates (E2). In the merged room, coupling is spread over 13 partners and drops to zero for old and new pairs alike. That is R-dilution, not adjacency gating. Room moves and merges therefore act on coupling through attention per partner, not only through who can read whom. The goal confound (#40's shared objective) would have raised coupling, yet coupling fell.

**Operator-facing conclusion.** Merging two groups into one room does not make them couple; for a week it removed measurable talk coupling for everyone (within-pair E2 0.29 → 0.08 → 0.47 across #39 / #40 / #41). To link two groups, keep rooms small and move or post across, rather than merge.

**Caveats.** 11 eligible agents; GPT-5 and several movers drop out by the 10-talk-minute rule. E1's minute grid sees per-pair couplings ≳ 0.2 only. The absolute J^R and J^U are confounded by call latency (talk and work calls differ in length, and the window equals the latency); only their difference is interpreted. The class model and full-J disagree on cross-pair sign in #39–#41 (0.08 vs −0.02), both null. #39 has a few short trimmed days (04-27: 76 kept minutes).

**Scorecard (round 1).**
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | Classes from the minute room timeline (cross 0.00 / 1.00 / 0.00 co-located); talk spins and ledger calls; eligibility removes low-talk agents. |
| B assumptions | 1 | Within-week stationarity assumed; daily fits noisy (se 0.04–0.21). |
| C adequacy | 1 | Wald CIs, relabel null, E2 placebo; no held-out likelihood. |
| D unfitted predictions | 1 | E2 read > in-flight inside the rooms after the split (0.47) and for the 05-25 mover (0.73). |
| E interventional | 1 | The A-B-A shows coupling falling in the merged week and returning after the split (within class): an intervention response, but not the predicted one. |
| F identifiability | 2 | Real-skeleton synthetic for E1 and E2: power 0.95 (M), 0.73 (E2), size 0.00 (E2 under a room drive), remanence 0.975. |
| G ground truth | 0 | The known merged-week adjacency is not recovered. |
| H comparative | 1 | R-dilution beats adjacency gating in #40; R-goal rejected (coupling fell under a shared objective); R-memory and R-partition untestable. |
| I transfer | 0 | Holdout not run. |

**Claim that stands:** in NE42's merged week (#40, 11 eligible agents), the talk-spin kinetic-Ising coupling between the former #best and #rest did not rise (merge contrast −0.02 [−0.13, 0.09] per pair; synthetic power 0.95 at 0.3), and within-room pairs lost their read-gated coupling too (E2 read minus in-flight 0.08 [−0.16, 0.31] in #40 vs 0.47 [0.27, 0.66] in #41). Excluded: remanence and partition memory (nothing to remain), the GPT-5 mirror arm (not eligible), the replication switches (E1 not specific; read-gated at one of five), per-pair couplings below 0.2.

### Confirmatory design (written 2026-10-04 after exploration; not run)
`analysis/confirm.py`: C1 the #47 → #48/#49 → #50 merge and split (two rooms 06-15..06-19 | #general 06-22..06-26 | two rooms 06-30..07-03; 06-29 skipped), with the same M/Rm/E2 rules and HH kill; C2 NE15 (#34 03-11..03-13 one room → #35 two rooms), cut-arm DiD < 0. Dry run on NE42 stand-ins passes (C1 stand-in reproduces round 1: failed; C2 stand-in #40 → #41: DiD −0.094 [−0.184, −0.005], post hoc, labelled). Ledger: allowed; disclosure needed (H04 on #47–#50, H05 on #34).

## Round 2 redirects
- **What the direction is really after:** does a read path make coupling, or does attention per partner? Fit J against room size across all two-room and one-room weeks (dilution exponent, H18) instead of an on/off switch.
- Read-gated E2 with log(latency) and per-sender read counts (H40's call clock) in every multi-room period.
- The confirm target #48–#49 (one room for 17 agents) is predicted by the dilution reading to show the same null; consider pre-registering that instead of the merge rise.

## Notes
- 2026-10-04 22:05 UTC: card written. NE12 (rooms v1, 02-25) is not an adjacency switch in practice: `period_units` lists one room for #32b and #33, so it is not used. NE15's before side (#34) and the 06-22 merge (#48) are held out and become the confirm targets. Code shared with H117 lives as an identical copy in each `scheme/` (no cross-hypothesis imports); suggested move to `infra/shared/kinetic_talk.py` in the report.
