# H46 × G37: Pick your own goal! (2026-03-30 → 2026-04-01)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime III · 10 agents with eligible days · rooms [2, 3] · 3 days with eligible agent-days · units 37.

## Why this period
A replication point for the common estimator (layer 1): every eligible goal period gets the same statistics, so periods are comparable points, not independent tests.

## Prediction
*Written 2026-10-04 05:45 UTC, before running on this period. Templated replication prediction (layer 1), the same for every period.*
- **Entry boundary** (#36 → #37, adjacent): type-controlled style percentile T_s ≤ 0.60 while content T_c ≥ T_s + 0.10 (content moves, style stays in the agent's day-to-day band).
- **Cross-boundary fingerprint** (train on the predecessor's last ≤ 3 days, test on this period's first ≤ 3, day-demeaned): style balanced accuracy > content's and ≥ 2× chance.
- **Within period:** style identifies agents at least as well as content in a split-half test (first half of days → second half).
- **Kolchinsky–Wolpert** (periods #30 onward): within-agent style fluctuations carry no information about next-day output (scramble-null p ≥ 0.05).
- **Verdict rule:** supported if the entry-boundary and fingerprint conditions hold; failed if T_s > 0.60 and T_s ≥ T_c − 0.10, or style accuracy ≤ 1.5× chance; otherwise mixed. No entry boundary → descriptive.
- *Counts against:* style moving at the entry boundary as much as content does.

## Result
*Run 2026-10-04 06:10 UTC (`analysis/replication.py` → `data/processed/H46-style-conserved-charge/replication.json`). Templated replication point.*

- **Sample:** 10 agents, 3 days, 27 eligible agent-days (≥ 3 deduplicated chat messages).
- **Agent share of day-demeaned variance:** style 0.68, content 0.58.
- **Split-half fingerprint within the period:** style 0.55, content 0.35, chance 0.10.
- **Entry boundary 36->37** (adjacent, 10 agents): style T_s = 0.721 [0.597, 0.813] (raw 0.671); content T_c = 0.826 [0.730, 0.900].
- **Cross-boundary fingerprint:** style 0.57 vs content 0.38 at chance 0.10.
- **Templated verdict:** mixed.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (beats the placebo band or not) and I (consistency across periods) in the main card.

## Round 2 (2026-10-05)
**Round-2 result (replication, regime III):** context-held style state ΔC(1) 0.63 [-0.54, 2.63]; self-pull context minus erased 0.051 [-0.111, 0.367].
*Pre-registered in the card (Round 2, 2026-10-05 02:44 UTC), synthetic validation and amendments R2-A1..A5 before this run; `analysis/r2_run.py` → `data/processed/H46-style-conserved-charge/r2/`. Non-reserved data.*
- Templated R2 statistics (no period verdict): cross-product of the 17-d style (genre + position removed) for lag-1 message pairs within a context segment minus pairs across a forced erasure, gap-matched (116 across pairs, 10 agents); the pull coefficient toward the agent's last ≤ 3 messages in context vs erased.
- NE41 forced-erasure style percentile (gp) in this period's units: 37 0.63.
