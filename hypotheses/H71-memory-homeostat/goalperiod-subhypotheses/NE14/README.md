# H71 × NE14: NE14/NE41: regime II → III (perma-computer-use, forced consolidation at the 41-call cap), 2026-03-24

**Verdict:** mixed (set point up; gain change small)
**Role:** native
**Period:** see "Why this period".

## Why this period
#36 splits at 03-24 (G36a regime II | G36b–c regime III); the same agents run #33, #35 (regime II) and #37–#39 (regime III). HH269 names a gain change here. The compression cycle changes from a session end after many appends to one append and one compression per ~40 calls.

## Prediction
*Written 2026-10-04 19:55 UTC, before running this native test.*
- **N1a (gain change):** within agents present on both sides (#33, #35, #36a vs #36b–c, #37, #38, #39), the paired mean Δφ⁺ (after − before) differs from 0 (CI excludes 0) with |Δφ⁺| ≥ 0.15.
- **N1b (set point):** the paired set point μ_i (mean x⁺) rises by ≥ 20% (Δ ln ≥ 0.18), as H09's NE14 V (+20%) suggests.
- **Counts against HH269's 'gain change':** |Δφ⁺| < 0.1 with the CI inside ±0.15.

## Result
*Run 2026-10-04.* Paired over agents present on both sides.

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N1a Δφ⁺ ≠ 0 with \|Δφ⁺\| ≥ 0.15 (wide: #33, #35, #36a → #36b–c, #37–#39) | +0.12 [+0.05, +0.20] (13 agents; 0.56 → 0.68) | CI excludes 0, magnitude below 0.15: not met |
| N1a within #36 only (36a → 36b–c) | +0.03 [-0.15, +0.20] (12 agents) | not met |
| N1b set point +20% (Δ ln μ ≥ 0.18) | wide +0.15 [+0.07, +0.27]; within #36 +0.27 [+0.13, +0.47] | met within #36 (+31%); wide +17% |

**Reading.** The regime II → III step raises the memory set point (+17% to +31%) and makes memory size slightly more persistent per cycle (+0.12 across periods; +0.03 inside #36). HH269's "gain change at NE41" is small: per compression cycle the regulation is about as strong before and after, although a cycle changes from a session end after many appends to one append and one compression per ~40 calls. Regime III cycles are shorter in wall time, so per hour the regulation is faster.

## Scorecard (period-specific axes)
- **E:** the NE14/NE41 step is the intervention; the set point moves, the per-cycle gain barely does. **A:** the same estimator applies on both sides of the regime boundary.

## Notes
- Data: `data/processed/H71-memory-homeostat/results/natives.json` (key `NE14`).
