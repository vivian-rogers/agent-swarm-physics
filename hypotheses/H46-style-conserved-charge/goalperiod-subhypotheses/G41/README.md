# H46 × G41: Perform novel research! (2026-05-11 → 2026-05-15)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime III · 14 agents with eligible days · rooms [2, 3] · 5 days with eligible agent-days · units 41.

## Why this period
A replication point for the common estimator (layer 1): every eligible goal period gets the same statistics, so periods are comparable points, not independent tests.

## Prediction
*Written 2026-10-04 05:45 UTC, before running on this period. Templated replication prediction (layer 1), the same for every period.*
- **Entry boundary** (#40 → #41, adjacent; NE42 split): type-controlled style percentile T_s ≤ 0.60 while content T_c ≥ T_s + 0.10 (content moves, style stays in the agent's day-to-day band).
- **Cross-boundary fingerprint** (train on the predecessor's last ≤ 3 days, test on this period's first ≤ 3, day-demeaned): style balanced accuracy > content's and ≥ 2× chance.
- **Within period:** style identifies agents at least as well as content in a split-half test (first half of days → second half).
- **Kolchinsky–Wolpert** (periods #30 onward): within-agent style fluctuations carry no information about next-day output (scramble-null p ≥ 0.05).
- **Verdict rule:** supported if the entry-boundary and fingerprint conditions hold; failed if T_s > 0.60 and T_s ≥ T_c − 0.10, or style accuracy ≤ 1.5× chance; otherwise mixed. No entry boundary → descriptive.
- *Counts against:* style moving at the entry boundary as much as content does.

## Result
*Run 2026-10-04 06:10 UTC (`analysis/replication.py` → `data/processed/H46-style-conserved-charge/replication.json`). Templated replication point.*

- **Sample:** 14 agents, 5 days, 67 eligible agent-days (≥ 3 deduplicated chat messages).
- **Agent share of day-demeaned variance:** style 0.71, content 0.58.
- **Split-half fingerprint within the period:** style 0.63, content 0.35, chance 0.07.
- **Entry boundary 40->41 (NE42 split)** (adjacent; NE42 split, 14 agents): style T_s = 0.779 [0.649, 0.899] (raw 0.770); content T_c = 0.969 [0.918, 1.000].
- **Cross-boundary fingerprint:** style 0.36 vs content 0.26 at chance 0.07.
- **KW (next-day output, within agent):** style p = 0.149, content p = 0.124 (small periods are underpowered and their raw CV R² is inflated; Amendment 3).
- **Templated verdict:** mixed.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (beats the placebo band or not) and I (consistency across periods) in the main card.
