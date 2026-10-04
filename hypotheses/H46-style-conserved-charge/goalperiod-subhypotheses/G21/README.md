# H46 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-05)

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** regime I · 9 agents with eligible days · rooms [0] · 5 days with eligible agent-days · units 21a, 21b.

## Why this period
A replication point for the common estimator (layer 1): every eligible goal period gets the same statistics, so periods are comparable points, not independent tests.

## Prediction
*Written 2026-10-04 05:45 UTC, before running on this period. Templated replication prediction (layer 1), the same for every period.*
- **Entry boundary** (#20 → #21, adjacent; NE28 double retirement the same day): type-controlled style percentile T_s ≤ 0.60 while content T_c ≥ T_s + 0.10 (content moves, style stays in the agent's day-to-day band).
- **Cross-boundary fingerprint** (train on the predecessor's last ≤ 3 days, test on this period's first ≤ 3, day-demeaned): style balanced accuracy > content's and ≥ 2× chance.
- **Within period:** style identifies agents at least as well as content in a split-half test (first half of days → second half).
- **Kolchinsky–Wolpert** (periods #30 onward): within-agent style fluctuations carry no information about next-day output (scramble-null p ≥ 0.05).
- **Verdict rule:** supported if the entry-boundary and fingerprint conditions hold; failed if T_s > 0.60 and T_s ≥ T_c − 0.10, or style accuracy ≤ 1.5× chance; otherwise mixed. No entry boundary → descriptive.
- *Counts against:* style moving at the entry boundary as much as content does.

## Result
*Run 2026-10-04 06:10 UTC (`analysis/replication.py` → `data/processed/H46-style-conserved-charge/replication.json`). Templated replication point.*

- **Sample:** 9 agents, 5 days, 42 eligible agent-days (≥ 3 deduplicated chat messages).
- **Agent share of day-demeaned variance:** style 0.78, content 0.56.
- **Split-half fingerprint within the period:** style 0.92, content 0.58, chance 0.12.
- **Entry boundary 20->21** (adjacent; NE28 double retirement the same day, 8 agents): style T_s = 0.480 [0.239, 0.695] (raw 0.542); content T_c = 0.936 [0.852, 0.990].
- **Cross-boundary fingerprint:** style 0.88 vs content 0.54 at chance 0.12.
- **Templated verdict:** supported.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (beats the placebo band or not) and I (consistency across periods) in the main card.
