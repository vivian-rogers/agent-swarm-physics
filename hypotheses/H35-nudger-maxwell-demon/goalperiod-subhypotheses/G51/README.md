# H35 × G51: Each agent: maximize your assigned goal (2026-07-06 → 2026-08-19 (nudger on); off-step 08-21 → 09-02)

**Verdict:** mixed
**Role:** native (round 1b native test below) · round 1: exploratory (round 1, non-holdout); primary
**Verdict (1b):** mixed (glance +0.08; sustained/work n.s. after placebo differencing; 2026-10-04)
**Period:** regime III · mode P (I/K) · 21–32 agents · nudges 728. Data: `data/processed/H35-nudger-maxwell-demon/G51/`.

## Why this period
primary: 728 nudges, 8-h days, plus the undocumented nudger stop on 08-20.

## Prediction
*Written 2026-10-03, before running on this period.*
- **P1:** b = I(M; D, G, K)/r ∈ [3, 8] bits per nudge, above the circular-shift null p95. D and K together carry ≥ 60% of I(M;X); I(M;G|D) ≤ 25%; I(M;A|X) ≤ 15%; controller memory N adds ≥ 0.3 bits per nudge.
- **P2:** first-nudge ATT on A30 ∈ [0.5, 3] extra active minutes, CI excluding 0; placebo-window CI including 0; repeat-nudge ATT ≤ 50% of first; H04's future-isolated design smaller than the past-only design.
- **P3:** the shared gate model's kick × ln k slope < 0, or the cross-fitted response at K = 1 exceeds K ≥ 10; flatness rejected (bootstrap CI of the K=1 minus K≥10 response excludes 0).
- **P4:** ΔV_log > 0 (escapes per nudge vs random-gate); η_SU ≤ 0.5 and η_KW ≤ 0.3, with bootstrap upper ends < 0.7; κ ∈ [0.05, 0.5] extra active minutes per bit per nudge.
- **P5:** gate-once with k* ∈ {1, 2} has a cross-fitted value per nudge ≥ 1.25 × the logged nudger's.
- **P6 (off-step, 08-21 → 09-02):** (a) nudges buy ≤ 1% of active agent-minutes, so the active-fraction change after 08-20 is within 2 day-SDs; (b) gate DiD (trigger region vs below, after − before) < 0, with size near the accounting prediction (sign only; low power).
- **Verdict rule:** supported if P1–P5 all hold; failed if none holds; otherwise mixed. P6 is reported separately (natural experiment).
- **What would count against:** η_SU > 0.7 (efficient demon), a flat response (worthless information), an ATT CI including 0, or a placebo response.

## Result
**Outcome vs prediction** (run 2026-10-03; numbers from `results.json` and `G51off/offstep_results.json`).

| Prediction | Predicted | Observed | Verdict |
| --- | --- | --- | --- |
| P1 information | b ∈ [3, 8]; D+K ≥ 60%; I(M;G given D) ≤ 25% (card: G given (D,K)); agent ≤ 15%; memory ≥ 0.3 | b = 1.42 bits per nudge (13% of the 10.7-bit decision entropy), above null; D+K 89%; I(M;G given D) 0.93 bits (65%, fails this wording), G given (D,K) 0.15 bits (11%, meets the card wording); agent given X 0.43 bits (31%); memory 0.32 | **partly**: magnitude ~2.5× lower than predicted; not agent-blind; the gate-timing clause depends on wording |
| P2 work | ATT ∈ [0.5, 3], CI excl. 0; placebo ∋ 0; repeat ≤ 50% of first; H04 design smaller | 1.45 [0.72, 2.20] (n 235; tool turns +6.2 [2.7, 11.0]); placebo 0.38 [−0.08, 0.86]; repeat 1.04 [0.37, 1.76] (71%); H04 design 1.40 | **mostly**: repeat clause fails (repeat placebo 0.5, selection) |
| P3 state dependence | shared slope < 0 or response(k = 1) > response(k ≥ 10); flatness rejected | shared-model slope −0.01 ± 0.05 (flat; set by mentions); cross-fitted gate response 0.23 (k = 1) vs 0.08 (k ≥ 10) escapes, k=1 minus k≥10 CI [0.07, 0.19]; card gate model nudge × ln k = −0.32 ± 0.13; minute response by trap age 0.02 / 2.22 / 2.61 / 2.32 / 0.52 min (k = 0 / 1 / 2–3 / 4–9 / ≥ 10); k 1–9 minus k ≥ 10 = 1.86 [0.47, 3.53] | **supported** |
| P4 inefficient demon (gate level) | ΔV_log > 0; η_SU ≤ 0.5, η_KW ≤ 0.3 (upper < 0.7); κ ∈ [0.05, 0.5] | among pause gates the logged choice is **worse than random**: ΔV = −0.076 (card model), −0.042 [−0.062, −0.024] (shared) escapes per nudge; η_SU < 0, η_KW = 0 | **failed as worded** (negative value of information, a stronger inefficiency than predicted) |
| P4 in the minute trap-age space (same estimators, work in minutes; added in round 1) | as above | ΔV = +0.50 [−0.09, 1.16] min per nudge; η_SU = 0.38 [−0.08, 0.68]; η_KW = 0.15 [0, 0.48]; κ = 0.49 [−0.10, 1.11] min per bit per nudge | bands met (secondary) |
| P5 better policy | once at k* ∈ {1, 2} ≥ 1.25 × logged | escapes: ×2.18 / ×2.01 (card model), ×1.55 [1.26, 1.84] / ×1.58 [1.34, 1.81] (shared); minutes: nudging only at k = 2–3 ×2.31 [1.66, 5.20] | **supported** |
| P6a off-step accounting | nudges ≤ 1% of active minutes; abs(Δ) < 2 day-SD | nudges buy 0.50% of active agent-minutes; predicted Δ active fraction −0.24 pp; observed −1.4 pp [−4.8, +2.0] (placebo split −2.9 pp; day SD 8.2 pp) | **supported** (undetectable, as predicted) |
| P6b off-step gate DiD | < 0, near the accounting (−0.005) | −0.050 [−0.099, −0.005]; placebo split −0.032 [−0.066, +0.009]; P(chain reaches k ≥ 10 given k ≥ 4) 0.245 → 0.296 | **inconclusive**: right sign but 10× the accounting and similar to the in-period drift |

**Where the nudges go.** Nudge rate per 1,000 agent-minutes rises from 0.55 (not in a pause chain) to 10.7 (k ≥ 10); 38% of nudges hit chains ≥ 10 re-pauses deep, where a nudge buys 0.5 min, and 23% hit agents not in a chain, where it buys ~0. Median 133 s after the agent's latest PAUSE; 72% land during a pause.

**Three nested views of efficiency.** (i) Coarse (pause status × idle duration): the nudger knows who is idle, and that information is used fairly well (η_SU 0.67–0.71, η_KW 0.50–0.55, κ ≈ 1.2 min per bit). (ii) Trap age at minute level: η_SU 0.38, η_KW 0.15. (iii) Among pausing agents (gate level): worse than random. The inefficiency is in the fine choice, not in detecting idleness.

| Quantity | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| information used, b = I(M;D,G,K)/r | 1.42 bits per nudge of 10.7 bits decision entropy; within-day part 0.62 | permutation null p95 | above |
| decomposition (bits per nudge) | I(M;K) 1.03, I(M;G\|D) 0.93, I(M;K\|D,G) 0.39, I(M;D) 0.11; agent \| X 0.43; controller memory \| X 0.32 | within-stratum permutation |  |
| first-nudge ATT, A30 (strict isolation) | 1.45 [0.72, 2.20], n = 235 | 0 |  |
| first-nudge ATT, A30 (H04 isolation set) | 1.77 [1.24, 2.35], n = 456; placebo 0.57 [0.19, 1.01] | 0 |  |
| gate escape by trap age (un-nudged / nudged) | k 1: 0.49 (n 5773); k 1: 0.56 (n 48) nudged; k 2–3: 0.37 (n 4634); k 2–3: 0.58 (n 77) nudged; k 4–9: 0.22 (n 3811); k 4–9: 0.35 (n 149) nudged; k ≥10: 0.07 (n 3549); k ≥10: 0.07 (n 244) nudged |  |  |
| gate model (card), nudge × ln k | -0.32 ± 0.13 | 0 |  |
| value per nudge (escapes): random-gate / logged / once at k=1 / k=2 | 0.220 / 0.144 / 0.313 / 0.289 (ratios to logged 2.18, 2.01) |  |  |

Data: `data/processed/H35-nudger-maxwell-demon/G51/results.json` (built 2026-10-03).

## Round 1b native test (work bought, on three outcome definitions)
*Role of this section: native (round 1b), in addition to round 1.*
*Prediction written 2026-10-04, before computing any round-1b outcome (sustained runs, work commits) around a nudge.* What was known: H43's side finding (a first nudge after a 30-min quiet spell raises "any activity within 15 min" ×1.75 but not a sustained run of ≥ 3 active calls; lnHR 0.07) and H44/H50 on day-edge synchrony. Same past-only matched design, strata and trap-age bins as round 1; new outcomes per agent-minute epoch: **glance** (any active row in the next 30 min), **sustained** (a run of ≥ 3 consecutive active DQ1 ledger calls starts in the next 30 min) and **work** (DQ4 agent work commits in the next 30 and 60 min).
- **N1 (glance vs work):** first-nudge ATT on glance > 0 with a CI excluding 0; on sustained, point ≤ 0.05 or CI including 0; on work commits in 60 min, CI including 0 (point < 0.10 commits per nudge).
- **N2 (demon in work space):** in trap-age space the response on sustained runs and on work commits is flat (k 1–9 minus k ≥ 10 CI including 0), so the value of the nudger's information for *work* is ≈ 0 and η_SU, η_KW are undefined or have CIs spanning 0–1; the once-early (k = 2–3) policy's work-commit ratio over logged has a CI including 1.
- **N3 (accounting):** nudge-bought work commits (first-nudge ATT × nudges) are ≤ 1% of G51's work commits.
- What would change the card: a sustained-run or work-commit ATT with a CI excluding 0, which would make the once-early policy a work lever rather than a glance lever.

**Result (round 1b native, run 2026-10-04; `data/processed/H35-nudger-maxwell-demon/G51/r1b/results_r1b.json`, `results_r1b_did.json`).** 235 strictly isolated first nudges (222 with a full 60-min window); round-1 active minutes reproduce exactly (A30 +1.45 [0.73, 2.30]: the grids are unchanged, see card).

| Outcome (per first nudge) | Matched ATT | Placebo window | Post hoc rate DiD |
| --- | --- | --- | --- |
| glance (any active row, 30 min) | **+0.082** [+0.035, +0.132] (control 0.76) | +0.008 [−0.027, +0.041] (clean) | — |
| sustained run starts (≥ 3 active calls, 30 min) | +0.094 [+0.042, +0.151] (control 0.61) | **+0.058** [+0.015, +0.100] (not clean) | +0.29 runs/h [−0.16, +0.70] |
| work commits, 60 min | −1.16 [−1.82, −0.60] (control 4.2) | **−0.35** [−0.52, −0.17] (not clean) | +0.22 commits/h [−0.29, +0.82] |

- **N1:** glance clause holds; the sustained and work clauses **fail as worded** (CIs exclude 0) because the past-only design fails its placebo for these outcomes: nudged agents had just finished a burst (more run starts, fewer commits in the 15 min before). The post hoc rate DiD (label: post hoc) puts both at zero, as predicted in substance.
- **N2 holds:** sustained response is flat over trap age (k 1–9 minus k ≥ 10: +0.04 [−0.03, +0.13]; after differencing every bin shrinks to the same value, τ² = 0, so ΔV = 0 and η_SU is undefined). Work-commit DiD: ΔV +0.007/h per nudge, η_SU 0.19 [−1.39, 0.70], η_KW 0.05 [0, 0.43]; once-early (k = 2–3) / logged 1.29 with a CI spanning −20 … +18.
- **N3 holds:** nudge-bought commits (DiD) ≈ 0.22 × 656 nudges ≈ 0.4% of G51's 35,430 work commits (upper CI 1.5%).
- For glances alone the nudger is nearly efficient: η_SU 0.88 [0.26, 0.97], η_KW 0.79; the best bin for glances is k ≥ 10 (deep traps glance most), the opposite of active minutes.
- Gate level (a sustained run within 15 min of the pause expiry): card model nudge +0.90 ± 0.17 (log-odds), nudge × ln k −0.16 ± 0.11 (n.s.); η_SU −0.01, once(k = 2)/logged 1.03: targeting buys no extra sustained work.
- Native verdict: **mixed** (substance as predicted; two clauses fail as worded because of selection).

## Scorecard (period-specific axes)
C 1 (beats the random-nudging and permutation nulls; placebo window clean for the strict design) · D 1 (response heterogeneity and the off-step accounting predicted before the run) · E 1 (off-step accounting matches; the gate DiD is not attributable) · G 1 (H04's nudge A30 reproduced, 1.45 vs 1.54; H16's gate response).

## Notes
- 2026-10-03: folder created with the prediction, before the run.
- 2026-10-03: results filled from the round-1 run (after the prediction above).
