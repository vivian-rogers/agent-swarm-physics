# H86: Taylor's law as a shared-field gauge

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only). Mixed: Taylor's law across agents is not multiplicative (b ≈ 0.85, c_T ≤ 0: faster agents are more regular), so the HH's c is not a field gauge; the pair-covariance coefficient c_× is: it is small (0.008 trimmed; shared share φ 0.08), and trimming removes 77% of it in regime III.**
- **Private variance dominates:** about 90% of activity's excess variance is the agent's own.
- **Talk shares more** than activity (φ 0.21 vs 0.08 in 77% of units).
- **The gauge** `taylor_c_shared` (activity_trim / activity_raw) is written per unit to `per_period_estimates`.
- Card and predictions written 2026-10-04 20:05 UTC before any real-data statistic. `analysis/confirm.py` written and dry-run, **not run**.
**Question (GOALS.md):** **Q2** (what is field and what is coupling?): GOALS.md asks for "a per-period field gauge (Taylor c …) reported for every unit". H86 builds it and tests whether it measures the shared field.
**Fields:** stat mech, complex systems (fluctuation scaling)
**Literature:** none in `literature/`; Taylor 1961, de Menezes & Barabási 2004 and Eisler, Bartos & Kertész 2008 are quoted from memory in `physics-models/14-scaling-and-fluctuations/README.md` (marked †).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t) (*active population*); Regime; Driving / external field; H38's **joint silence**, **agent-state conditioning** and f_scaffold (cross-check); DQ8's **all-present window** (`infra/shared/nulls.py: all_present_window`). Proposed named variants (definitions under Observables): **Taylor coefficients (a, c_T, b)**, **shared-field coefficient c_×**, **shared share φ**, **within-day shared coefficient c_×w**.
**From:** HH310 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/14-scaling-and-fluctuations/` (primary: fluctuation scaling), `physics-models/02-nonequilibrium-ising/` (the external field h(t) that c should measure; secondary)
**Data inputs (shared tables first):** `period_units`, `calendar`, `activity_bins_fixed`, `call_windows` (per-call clock, H40), `chat_core` (messages), DQ4 `work_commits` (agent work), `per_period_estimates` (H38 `f_scaffold`, cross-check), H54's `kickoffs.parquet` (`S_text`, read only), `roster`.

## Source HH (verbatim from the HH list, including literature refinements)
Fluctuation scaling (Taylor's law) measures the shared field. Across agents within a unit: Var(Y) = aμ + cμ². The quadratic coefficient c is the variance share of a shared multiplicative field.
  - *Predictions:*
    - Raw activity: c large, with Taylor exponent b ≈ 2 (the scheduler).
    - Activity on the DQ8 trimmed window: b → 1–1.3, with c falling by the 70–80% schedule share (H38).
    - Commits: b between 1 and 2 with c tracking kickoff specificity (H54).
  - *Use:* c becomes a one-number impostor gauge reported in every hypothesis.
  - *Kill:* b ≈ 2 survives trimming, i.e. a non-scheduler shared field is unaccounted for. That would itself be an egregore lead.
  - *Models:* 02 · *Builds on:* H38, H50, H02

## Question
Does the quadratic Taylor coefficient of per-agent activity measure the shared (scheduler or exogenous) field, falling by H38's 70–80% when the scheduler's day edges are trimmed, so that it can serve as a one-number field gauge per unit?

## Design: two layers (Vivian, 2026-10-04)
- **Replication:** the Taylor fit and the shared-field coefficient on every eligible non-holdout unit (`period_units`), four channels, raw and trimmed. Role `replication`. Per goal period one README; the per-unit numbers are written to `per_period_estimates` as a gauge other hypotheses can join.
- **Natives (2):** NE14 (G36: the regime II → III switch to an always-on runner, which H38 found adds the scheduler's start/stop co-activation), NE43 (G51: operator bookends stop 08-05, nudges stop 08-21). Role `native`.

## Model
**From:** `physics-models/14-scaling-and-fluctuations/` (2. fluctuation scaling; de Menezes–Barabási split).

**H86 variant: a multiplicative-field count model.** Agent i's count in bin t is

  y_it ~ Poisson(μ_i · ξ_t · ζ_it),  E ξ = E ζ = 1,  Var ξ_t = c_×,  Var ζ_it = s_i,

with ξ_t a field shared by all agents present in bin t (scheduler, kickoff, operator) and ζ_it the agent's private burstiness (its own call bursts, pauses, erasures). Then

  V_i = μ_i + [c_× + s_i(1 + c_×)] μ_i²,   Cov(y_i, y_j) = c_× μ_i μ_j  (i ≠ j).

- **Taylor fit across agents:** V = a μ + c_T μ² gives c_T ≈ c_× + mean(s) (if s is unrelated to μ). So **c_T measures shared plus private multiplicative variance**: it is a field gauge only if private burstiness is small.
- **Taylor exponent b** (slope of ln V on ln μ) runs from 1 (Poisson, c μ ≪ 1) to 2 (c μ ≫ 1). At tens of records per bin, b ≈ 2 follows from *any* multiplicative variance, shared or private.
- **Shared-field coefficient c_×** = Σ_{i<j} Cov(y_i, y_j) / Σ_{i<j} μ_i μ_j estimates Var ξ directly, without μ variation and without private burstiness.
- **Shared share φ** = c_× Σ_i μ_i² / Σ_i (V_i − μ_i): the share of super-Poisson variance carried by the shared field. This is what the HH means by "the variance share of a shared multiplicative field".
- **Within-day part c_×w:** c_× on counts demeaned within agent-day (removes day-to-day field changes). c_× − c_×w is the day-level field.

**Why add c_× (dated design decision, 2026-10-04 20:05 UTC, before real data).** The HH's kill ("b ≈ 2 survives trimming ⇒ an unaccounted shared field") is ill-posed under this model: b ≈ 2 is expected from private burstiness alone. The kill is restated on c_× and φ (P4). The HH's c (c_T) and b are still reported with their own predictions.

**Rivals.**
- **R1 private burstiness:** super-Poisson variance is agent-specific (bursts of computer-use actions, pauses), not shared: b ≈ 2 and large c_T, but φ small.
- **R2 coupling as "field":** co-activity from agents responding to each other (read-out at the next call) also gives Cov > 0. c_× counts field + equal-time coupling. H50 found activity co-movement is field and talk spreads by coupling, so c_× on activity is read as field, on messages as field + coupling.
- **R3 scheduler only:** all shared variance is the day edges: c_× trimmed ≈ 0 (within its null).

## Data scheme (`scheme/`)
Script: `scheme/build.py` (shared tables only; holdout rows removed by `period_units.holdout` and `common.holdout_mask`, asserted).
- **Bins:** 15-minute clock bins of each day's calendar window (activity, calls, messages); 60-minute bins for commits (sparse).
- **Channels:** `activity` = records per bin (`turns + talk + other_event + consolidate` from `activity_bins_fixed`); `calls` = model calls per bin (`call_windows` rows by `t_call`; the per-call clock of H40); `msg` = agent chat messages (`chat_core`); `commit` = agent work commits (DQ4 default filter).
- **Presence:** an agent is present on a day if it has ≥ 1 record in `activity_bins_fixed`; its span is first to last record minute (DQ8's rule). Claude Code agent excluded.
- **Grids:** **raw** = every bin of the window for present agent-days (minutes outside the agent's span count as zeros: this is where the scheduler field lives); **trimmed** = bins lying wholly inside the day's all-present window (every present agent inside its span, `nulls.all_present_window`).
- **Units:** bins are assigned to the `period_units` unit containing the bin start. Eligible units: ≥ 4 agents with ≥ 8 bins on the grid and μ_i > 0.
- **Output:** `data/processed/H86-taylor-law-field-gauge/` (`bins.parquet`: unit, pt_date, bin, agent, grid flags, counts per channel; `gauge.parquet`: per unit × channel × grid statistics; `synthetic/`, `natives/`, `_provenance.json`).

## Observables
*Written 2026-10-04 20:05 UTC. Sampling facts already seen: the unit list, the activity-bin schema, H38's per-unit `f_scaffold` exists in `per_period_estimates` (values not looked at), H54's kickoff `S_text` table (looked at: 52 rows). No count variance or covariance has been computed.*

Per unit u, channel, grid:
- **μ_i, V_i** over the agent's bins in the unit; **F_i = V_i/μ_i** (Fano factor).
- **(a, c_T):** OLS of F_i on μ_i across agents (V = aμ + c_T μ²). CI by agent bootstrap.
- **b:** OLS slope of ln V_i on ln μ_i across agents (primary, the HH's "across agents"); agent-day points (secondary; more μ range).
- **c_×, c_×w, φ** as in Model; CI by day bootstrap (days resampled within the unit).
- **Within-day null for c_×w:** each agent's series circularly shifted within each day by an independent offset (49 surrogates), on the trimmed grid only (DQ8: never shift untrimmed days). p and the null-corrected c_×w.
- **Reduction under trimming:** r_T = 1 − c_T,trim / c_T,raw, r_× = 1 − c_×,trim / c_×,raw.
- **The gauge column** written to `per_period_estimates`: `taylor_c_shared` (c_×) and `taylor_phi_shared` (φ) for channels `activity_raw`, `activity_trim`, plus c_T, b for every channel and grid. Recommended join key for other hypotheses: (`period_unit`, `statistic = taylor_c_shared`, `channel = activity_trim`).

## Null / baseline
*Written 2026-10-04 20:05 UTC.*
- **Independent Poisson agents:** b = 1, c = 0. **Independent bursty agents (R1):** b → 2, c_T > 0, c_× = 0, φ = 0.
- **Within-day circular shift** (trimmed grid) for c_×w; size checked on synthetic R1 data at real counts.
- **Synthetic units** (`analysis/synthetic.py`) at the real presence grid of three units (one per regime) with planted scheduler, private burstiness and shared field.

## Impostor table (STANDARDS.md §1)
| Impostor | How it could fake this result | How H86 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | The object being measured on raw grids; the impostor is reading scheduler variance as anything else | Trimmed grid (DQ8 all-present window); raw − trimmed split; within-day shift null only on trimmed data | removed (for the trimmed gauge) |
| Exogenous field (kickoff, goal, operator) | A shared field by definition: c_× includes it. The impostor is calling it coupling or an "egregore" | c_× is labelled field + equal-time coupling; c_× vs c_×w splits day-level fields (kickoffs, goal days) from within-day ones; NE43 removes operator drives | partly |
| Shared model priors (family, style) | Families share burst patterns (e.g. a family's long tool calls) that are private per agent but correlated in time only through the scheduler | c_× needs co-timed bins, not similar marginals; family-level c_× not run (round 2) | partly |
| Contemporaneous convergence | Agents converging on the same activity at the same time without reading (e.g. all deploy after the same human message) appears as shared field | It *is* a shared field for the gauge; c_× does not claim coupling. Coupling (R2) is not separated; H50 says activity co-movement is field | n/a (gauge, not a coupling claim) |

## Prediction
*Written 2026-10-04 20:05 UTC, before running the analysis on real data.*

**Replication (card level).**
- **P1 raw activity (HH):** median b_raw ∈ [1.7, 2.3] over eligible units, and c_T,raw > 0 in ≥ 90%. Prior 0.75.
- **P2 trimmed activity b (HH):** median b_trim ≤ 1.3. Prior 0.25: under the model, private burstiness keeps b near 2 at tens of records per bin. If P2 fails with φ_trim < 0.3, the failure is R1 (private), not a shared field.
- **P3 reduction (HH, scoped to regime III where H38's 70–80% was measured):** median r_× ∈ [0.6, 0.9] in regime III units. c_T: median r_T reported against the same band (expected smaller: private burstiness survives trimming). In regime I the reduction should be small (H38: f 0.11): median r_× < 0.4.
- **P4 kill (restated on the shared field):** in regime III, the median trimmed shared share φ_activity,trim ≥ 0.5 **and** c_×w beats its within-day null (p < 0.05) in ≥ 2/3 of units ⇒ a non-scheduler shared field is unaccounted for (an exogenous-field or coupling lead). Expected: not met (φ_trim < 0.3).
- **P5 per-call clock:** on the `calls` channel, b_trim and c_T,trim are lower than on `activity` in ≥ 2/3 of regime-III units (counting calls removes within-call action bursts).
- **P6 commits (HH):** median b_commit ∈ (1, 2) on the trimmed 60-min grid; Spearman(c_×,commit,trim, S_text) > 0 with p < 0.05 across goal periods (goal-period mean over units; git-dense units). Prior 0.25 (H54: specificity is not a dial).
- **P7 unfitted cross-check:** across units, Spearman(r_×, H38's `f_scaffold` on activity) ≥ 0.3: the gauge's scheduler share agrees with H38's.
- **P8 talk vs activity (H50):** φ_msg,trim > φ_activity,trim in ≥ 2/3 of units with ≥ 300 messages (talk carries coupling on top of the field).

**Natives (dated predictions also in each folder).**
- **N1 NE14 (G35, 36a in regime II vs 36b, 36c, G37 in regime III):** c_×,raw (activity) rises across the boundary (III mean > II mean, day-bootstrap CI of the difference > 0); the trimmed change is less than half of the raw change. Placebos 35 → 36a and 36c → 37 move c_×,raw by less than the NE14 change. *Against:* the trimmed change ≥ the raw change (the regime switch added a non-scheduler shared field).
- **N2 NE43 (G51: 51f before 08-05, 51g between, 51h–51i after 08-21):** (i) bookends stop: c_×,raw changes by less than its 95% CI at 08-05 (the runner, not the bookends, drives the edges; H38 round 1b). (ii) nudges stop: c_×,trim does not change (CI includes 0) while c_T,trim rises (idle agents stay idle longer: private variance). *Against:* (i) a c_×,raw drop beyond its CI; (ii) a c_×,trim change beyond its CI.

**Overall reading (fixed now).** **Supported** (c is a usable field gauge) if P1 and P3 (regime III, on c_× or c_T) pass and P4's kill does not fire. **Mixed** if P3 passes only for c_× (the HH's c_T is contaminated by private burstiness) or P2 fails while P3 passes. **Failed** if r_× < 0.4 in regime III (trimming does not remove the shared field: the gauge does not see the scheduler) or the P4 kill fires.

## Synthetic validation (axis F; run 2026-10-04 20:11–20:12 UTC, before any real-data statistic)
`analysis/synthetic.py` → `data/processed/H86-taylor-law-field-gauge/synthetic/synthetic.json`. Real presence grids (agent spans, windows, trimmed bins) of units 13 (regime I, 6 agents, 10 days), 35 (II, 12, 5), 38a (III, 12, 8), 51c (III, 25, 5). Poisson counts inside spans (zero outside); rates lognormal (median 2/min in III, 0.7/min otherwise). 20 replicates; 39 shift surrogates (first 10 replicates).

| Scenario (planted) | b raw / trim | c_T trim | c_× trim | c_×w trim | φ trim | shift-null rejections |
| --- | --- | --- | --- | --- | --- | --- |
| S0 Poisson + scheduler | 0.93–1.58 / 0.93–1.01 | ≈ 0 | ≈ 0 | ≈ 0 | noise | – |
| S1 + private burstiness (s = 1) | 1.88–1.95 / 1.86–1.95 | 0.96–0.99 | −0.01 to 0.01 | ≈ 0 | ≈ 0 | 0.0 (size) |
| S2 S1 + within-day shared field (c = 0.1) | 1.90–2.02 / 1.89–2.02 | 1.07–1.23 | 0.095–0.111 | 0.07–0.09 | 0.07–0.08 | 0.3 (13), 0.9–1.0 (others) |
| S3 S1 + day-level shared field (c = 0.1) | 1.87–1.98 / 1.87–1.97 | 0.99–1.19 | 0.05–0.08 | ≈ 0 | 0.05–0.06 | 0.0–0.1 (size) |

Other checks: the day-bootstrap 95% CI of c_× (S2, trimmed) covered the planted value in 0.7–0.8 of 10 replicates. Under S0 the raw grid gives c_× 0.04 and φ 0.86 only in 51c, where agents' spans differ most; in the other three units the scheduler edges add almost nothing to count covariance.

Readings: (1) **b ≈ 2 after trimming is the signature of private burstiness**, not of a shared field (S1). The HH's P2 and its kill cannot separate R1 from a field; c_× and φ can. (2) c_× recovers the planted shared variance (bias ≤ 20%); c_×w separates a within-day field from a day-level one. (3) The shift null holds size and has power wherever ≥ 12 agents are present. (4) How much the scheduler adds to count covariance depends on how unequal the agents' spans are.

## Amendments (2026-10-04 20:12 UTC, after the synthetic validation, before any real-data statistic)
- **A1 (null resolution).** The shift null uses 49 surrogates (minimum p 0.02). A first run with 19 surrogates could not reject at p < 0.05 by construction; it was fixed before any real data.
- **A2 (CI under-coverage).** Day-bootstrap CIs of c_× cover 0.7–0.8 in synthetic runs. They are reported as indicative. Card-level verdicts use medians over units, sign counts and the shift null, not single-unit CIs.
- **A3 (reduction scope).** r_× and r_T are computed only for units where the raw coefficient exceeds 0.01 (below that the ratio is noise). P3 counts those units.

## Results by goal period
Roles: `replication` = the gauge on every eligible unit (templated; not independent tests); `native` = NE14 (G35–G37) and NE43 (inside G51). Per-period verdicts grade the shared-field gauge with a rule fixed after the card-level run (2026-10-04 20:22 UTC, `analysis/write_period_cards.py`): **supported** = c_× falls under trimming in most units and trimmed φ < 0.3; **descriptive** = no unit has c_×,raw > 0.01; **failed** = a unit trips the P4 kill (φ_trim ≥ 0.5 with shift p < 0.05). The HH's b ≈ 2 clause fails in every period.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | mixed | c_× raw 0.118 → trim 0.095; φ_trim 0.33; b_raw -0.37 (1 units) |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | mixed | c_× raw 0.024 → trim 0.137; φ_trim 0.51; b_raw 0.49 (1 units) |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | mixed | c_× raw 0.033 → trim nan; φ_trim nan; b_raw 0.15 (4 units) |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | c_× raw 0.003 → trim 0.009; φ_trim 0.24; b_raw -1.57 (1 units) |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | failed | c_× raw 0.549 → trim 0.548; φ_trim 0.42; b_raw -1.38 (2 units) |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | descriptive | c_× raw 0.007 → trim 0.007; φ_trim 0.32; b_raw -3.45 (1 units) |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | descriptive | c_× raw 0.008 → trim 0.017; φ_trim 0.18; b_raw 0.56 (1 units) |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | mixed | c_× raw 0.145 → trim 0.149; φ_trim 0.37; b_raw 1.79 (2 units) |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | supported | c_× raw 0.016 → trim 0.014; φ_trim 0.07; b_raw 1.16 (1 units) |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | mixed | c_× raw 0.024 → trim 0.026; φ_trim 0.18; b_raw 0.26 (2 units) |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | supported | c_× raw 0.010 → trim 0.004; φ_trim 0.04; b_raw 0.34 (1 units) |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | supported | c_× raw 0.015 → trim 0.013; φ_trim 0.09; b_raw 0.62 (1 units) |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | supported | c_× raw 0.080 → trim 0.069; φ_trim 0.21; b_raw -0.29 (1 units) |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | supported | c_× raw 0.024 → trim 0.017; φ_trim 0.14; b_raw 0.36 (3 units) |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | mixed | c_× raw 0.025 → trim 0.014; φ_trim 0.09; b_raw 0.13 (2 units) |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | mixed | c_× raw 0.020 → trim 0.016; φ_trim 0.22; b_raw 0.74 (4 units) |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | c_× raw 0.085 → trim 0.090; φ_trim 0.46; b_raw 1.68 (2 units) |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | descriptive | c_× raw 0.003 → trim -0.001; φ_trim -0.01; b_raw 1.84 (1 units) |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | descriptive | c_× raw 0.005 → trim 0.004; φ_trim 0.08; b_raw 1.47 (1 units) |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | mixed | c_× raw 0.021 → trim 0.021; φ_trim 0.13; b_raw 0.96 (1 units) |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | supported | c_× raw 0.071 → trim 0.032; φ_trim 0.17; b_raw 1.89 (1 units) |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | supported | c_× raw 0.019 → trim 0.019; φ_trim 0.16; b_raw 1.18 (1 units) |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | c_× raw 0.008 → trim 0.003; φ_trim 0.05; b_raw 1.06 (2 units) |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | descriptive | c_× raw 0.002 → trim -0.001; φ_trim -0.01; b_raw 0.69 (4 units) |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | supported | c_× raw 0.031 → trim 0.019; φ_trim 0.15; b_raw 1.14 (1 units) |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | c_× raw 0.007 → trim 0.007; φ_trim 0.13; b_raw 1.71 (1 units) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | supported | c_× raw 0.001 → trim 0.000; φ_trim 0.01; b_raw 1.04 (3 units) |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | supported | c_× raw 0.709 → trim 0.001; φ_trim 0.01; b_raw 1.21 (1 units) |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | supported | c_× raw 0.010 → trim 0.003; φ_trim 0.03; b_raw -0.59 (5 units) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | supported | c_× raw 0.017 → trim -0.005; φ_trim -0.06; b_raw 1.15 (1 units) |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | descriptive | c_× raw 0.005 → trim 0.008; φ_trim 0.10; b_raw 0.14 (1 units) |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | c_× raw 0.069 → trim 0.078; φ_trim 0.31; b_raw 2.83 (1 units) |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | c_× raw 0.006 → trim 0.003; φ_trim 0.04; b_raw 1.93 (2 units) |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | supported | c_× raw 0.037 → trim -0.003; φ_trim -0.02; b_raw 0.45 (2 units) |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | supported | c_× raw 0.022 → trim 0.006; φ_trim 0.04; b_raw 1.05 (12 units) |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | native | failed | raw +0.31 [−0.01, 0.93] (one off-gap day); trimmed +0.001 [−0.007, 0.011]; III→III placebo larger |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | mixed | bookends: raw +0.001 [−0.003, 0.006]; nudges: trim −0.005 [−0.011, 0.003], c_T +0.008 |

## Outcome vs prediction
*Run 2026-10-04 20:16–20:18 UTC (`analysis/gauge.py`, `analysis/natives.py`). 70 eligible units (one unit has < 4 agents); activity = records per 15-min bin; medians over units [IQR].*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 raw activity b ∈ [1.7, 2.3]; c_T,raw > 0 in ≥ 90% | b_raw 0.85 [0.21, 1.21]; agent-day points 0.51; c_T,raw > 0 in 31% (median −0.08) | **fail** |
| P2 trimmed b ≤ 1.3 | b_trim 0.82 [0.12, 1.34] | pass (trivially: raw b is already < 1) |
| P3 regime III r_× ∈ [0.6, 0.9]; regime I r_× < 0.4 | regime III r_× 0.77 [0.07, 0.98] (13 units with c_×,raw > 0.01); regime I 0.06 [−0.01, 0.35] (25). r_T meaningless (c_T ≤ 0) | **pass for c_× only** |
| P4 kill: regime III φ_trim ≥ 0.5 and c_×w beats the shift null in ≥ 2/3 | φ_trim 0.04 [0.01, 0.06]; shift null p < 0.05 in 38% (regime I 49%) | **not fired** (two regime-I units, 6a and 21b, trip it at unit level) |
| P5 per-call clock lowers b and c_T in ≥ 2/3 of regime-III units | lower b in 58%, lower c_T in 50% | **fail** |
| P6 commits b ∈ (1, 2); Spearman(c_×,commit, S_text) > 0, p < 0.05 | b_commit 1.26 [1.19, 1.32] (13 units); ρ 0.14 (6 goal periods, p 0.39) | b pass; specificity **fail** (n = 6) |
| P7 Spearman(r_×, H38 f_scaffold) ≥ 0.3 | ρ 0.19 (13 units, p 0.53); raw − trimmed difference vs f_scaffold ρ −0.01 (18) | **fail** |
| P8 φ_msg,trim > φ_activity,trim in ≥ 2/3 of units | 77% of 64 units; φ_msg 0.21 vs φ_activity 0.08 | **pass** |
| N1 NE14: raw c_× rises (CI > 0); trimmed change < half | raw +0.31 [−0.01, 0.93], one off-gap day (03-31: 2.17); III → III placebo +0.71; trimmed +0.001 [−0.007, 0.011] | **failed** (raw clause) |
| N2 NE43: raw c_× flat at bookends; trimmed c_× flat and c_T up at nudge stop | raw +0.001 [−0.003, 0.006]; trimmed −0.005 [−0.011, 0.003]; c_T +0.008 [−0.034, 0.047] | **mixed** |

**Overall (pre-registered reading):** P1 fails, P3 passes only for c_×, and the kill does not fire, so H86 is **mixed**. The HH's Taylor coefficient c_T and exponent b are not field gauges in this swarm. The pair-covariance coefficient c_× is: it is small, trimming removes about three quarters of it in regime III, and operator drives do not move it.

## Results
**1. Across agents, activity variance grows no faster than the mean.** Taylor's exponent across agents is b ≈ 0.85 on raw grids and 0.82 trimmed (0.51 and 0.48 on agent-day points). The quadratic coefficient c_T is negative in most units (median −0.08). Activity is super-Poisson (median Fano factor ≈ 5), but faster agents are more regular: the Fano factor falls with the agent's mean (Spearman −0.26), also within active bins (−0.15, post hoc). Whole-bin on/off switching carries ≈ 0 of the variance at 15 minutes (post hoc). This is the signature of a rate-limited call clock, not of a multiplicative field. The HH's b ≈ 2 premise fails, and with it c_T as a gauge.

**2. The shared field is small.** The pair-covariance coefficient is c_× = 0.016 raw and 0.008 trimmed (medians over 70 units). The shared share of super-Poisson variance is φ = 0.12 raw and 0.08 trimmed (regime III 0.04). So about 90% of activity's excess variance is private to the agent. This agrees with H58 (the agent + own artifact is the unit) from the fluctuation side.

**3. Trimming removes about three quarters of the shared field in regime III.** Where the raw coefficient is above noise, r_× = 0.77 [0.07, 0.98] in regime III and 0.06 in regime I, matching H38's 70–80% and its regime-I 0.11. Per unit, r_× does not track H38's f_scaffold (ρ 0.19, n 13), so the agreement is at the regime level only. Raw c_× is dominated by off-gaps inside windows: the 03-31 day with a 513-min all-silent gap reaches 2.17, against ≤ 0.03 on every other regime-III day around NE14.

**4. No unaccounted shared field.** Within-day shared co-movement survives the circular-shift null in 38% of regime-III units and 49% of regime-I units, but it is small (φ_trim 0.04 in regime III). The kill does not fire. Two regime-I units do trip it at unit level: 6a (4 agents, a competition goal; c_× 1.10, φ 0.87) and 21b (9 agents; φ 0.51). They are leads for an exogenous field, not an egregore claim.

**5. Talk shares more of its variance than activity.** On trimmed grids, φ_msg = 0.21 vs φ_activity = 0.08 (77% of units). Messages also follow a Taylor-like law (b 1.18–1.24). This matches H50: talk carries a coupling or a talk-specific shared drive on top of the scheduler.

**6. Commits are near-independent.** b_commit 1.26 on 60-min trimmed bins, c_× 0.013, φ 0.02. Kickoff specificity cannot be tested: only 6 git-dense goal periods have a commit gauge (ρ 0.14).

**7. Operator drives do not move the gauge.** At NE43, neither the bookend stop nor the nudge stop changes c_×. NE14 changes trimmed c_× by +0.001.

**The gauge to report.** Use `taylor_c_shared` on `activity_trim` (and `activity_raw` to see the scheduler) and `taylor_phi_shared`. Do not use `taylor_c_T` or `taylor_b` as field gauges. All per unit in `per_period_estimates` (hypothesis H86).

Figures: `figures/summary_obs.pdf` (Taylor plot across agents for 38a and 51c; c_× raw vs trimmed per unit), `figures/summary_obsb.pdf` (daily c_× around NE14; φ for talk vs activity). Data: `data/processed/H86-taylor-law-field-gauge/` (`bins15.parquet`, `bins60.parquet`, `spans.parquet`, `replication/gauge.parquet`, `replication/daily.parquet`, `natives/`, `synthetic/`, `confirm/confirm_dryrun.json`). Estimates: 1,643 rows in `per_period_estimates`.

## Faithfulness scorecard
*Round 1, 2026-10-04.* Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed.
**Rival models:** R1 private burstiness; R2 coupling read as field; R3 scheduler only.
**Locked holdout used for confirmation:** none yet (`analysis/confirm.py`, dry-run only).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Counts, presence spans and the trimmed window come from shared tables with DQ8's rule. "Activity" mixes computer-use actions and events, whose clocks differ by regime. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | The multiplicative count model fails across agents (variance grows sublinearly in the mean). c_× and φ do not need it; c_T and b do. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Within-day shift null calibrated (size ≤ 0.1, power 0.3–1.0); significant in ~40% of units. No held-out-day test. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The regime-III trimming share (0.77) reproduces H38's independent 70–80%; the per-unit cross-check with f_scaffold fails (ρ 0.19). |
| E interventional | predicts the change across a natural experiment | 1 | NE43: no change, as predicted for the shared field; private clause fails. NE14: trimmed flat as predicted, raw clause fails (one off-gap day). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Real presence grids: c_× recovers the planted field (bias ≤ 20%), separates day-level from within-day fields, and b ≈ 2 from private burstiness was found before real data; null resolution fixed (A1); CI under-coverage stated (A2). |
| G ground truth | agrees with known structure | 1 | Detects the documented 03-31 off-gap day; agrees with H38 at regime level; commits nearly independent as H58 found. |
| H comparative | beats the named rivals | 1 | R1 (private) explains most excess variance (φ ≈ 0.08); R3 holds in regime III (77% removed); R2 (coupling vs field) not separated except that talk shares more than activity. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | b < 1 and small φ hold in all three regimes (70 units); holdout not run. |

## Confirmatory predictions (written 2026-10-04 20:20 UTC after round 1, before any holdout use; `analysis/confirm.py`, dry-run only, **not run**)
Targets: held-out period units; the NE21+NE23 window (hours reversals) for C5.
- **C1:** median b_raw < 1.2 and median c_T,raw < 0.05 (activity).
- **C2:** regime III: median r_× ≥ 0.5 over units with c_×,raw > 0.01, and median c_×,trim < 0.01.
- **C3:** regime III: median φ_trim < 0.15.
- **C4:** φ_msg,trim > φ_activity,trim in ≥ 2/3 of units with ≥ 300 messages.
- **C5 (descriptive):** NE21+NE23: daily c_×,trim differs by < 0.01 between longer- and shorter-window days.
- **Overall:** confirmed if C1, C2 and C3 pass. Dry run on the non-holdout units: C1–C4 pass (b_raw 0.89, r_× 0.77 over 16 units, φ_trim 0.04).
- **Reuse disclosure:** the NE21+NE23 window is also targeted by activity-synchrony scripts (H02, H04, H05 families); disclose if run.

## Caveats
- **Across-agent fits have few points** (4–32 agents) and a narrow μ range in regime III, so unit-level b is unstable (−1.9 to 1.5 in G38). The card uses medians over units.
- **Day-bootstrap CIs under-cover** (0.7–0.8 in synthetic runs).
- **c_× counts equal-time coupling as field** (R2). It is a shared co-movement gauge; it does not say why agents move together.
- **15-minute bins.** Taylor statistics depend on the bin width; 60-min bins were used only for commits.
- **Commits** have a gauge in 13 units only; the kickoff-specificity test has 6 goal periods.
- **Post hoc:** the duty-cycle and regularity checks in Result 1 and the per-period verdict rule.

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **Where round 1 went sideways:** the HH assumed agents emit Poisson events modulated by multiplicative fields. Agent activity is a clocked, rate-limited process, so variance grows more slowly than the mean, and Taylor's c and b measure clock regularity, not fields.
- **What the direction is really after:** one number per unit that says how much of the swarm's fluctuation is shared, after the scheduler is removed.
- **H86-R1. Clock-aware Taylor law.** Fit variance against mean with a renewal model of each agent's call clock (inter-call CV²) and report the residual shared term; check whether CV² is a family constant.
- **H86-R2. Lagged vs equal-time c_×.** Split c_× into equal-time and one-call-lagged covariance on the per-call clock (H40). That separates field (equal time) from read-out coupling (lag one call), the R2 confound.
- **H86-R3. Off-gap detector.** Use raw − trimmed c_× per day as an automatic flag for village-off gaps inside windows (DQ7 calendar repair).
- **H86-R4. Units 6a and 21b.** Check the shared within-day field in these two regime-I units against operator and human messages (kickoff-matched placebos).


## Notes
- 2026-10-04: the first draft carried hand-written timestamps (20:20, 20:50–21:00 UTC) that ran ahead of the clock; corrected from file times at 20:25 UTC: card 20:05, build 20:10, synthetic.json 20:12:10, amendments 20:12:30, gauge.py run 20:16, natives 20:18. The order is unchanged.
- 2026-10-04: runs used one process at a time (≤ 2 threads; gauge.py 42 s). Outputs ≈ 1 MB with `_provenance.json`. No code imported from another hypothesis.
- 2026-10-04 20:05 UTC: card written by the round-1 agent before any real-data statistic. H54's processed `kickoffs.parquet` is read as data (no code imported).
