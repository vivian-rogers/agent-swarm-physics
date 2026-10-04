# H46 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-11-28)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime I · 10 agents with eligible days · rooms [0] · 10 days with eligible agent-days · units 20a, 20b, 20c, 20d.

## Why this period
A replication point for the common estimator (layer 1): every eligible goal period gets the same statistics, so periods are comparable points, not independent tests.

## Prediction
*Written 2026-10-04 05:45 UTC, before running on this period. Templated replication prediction (layer 1), the same for every period.*
- **Entry boundary** (#19 → #20, adjacent): type-controlled style percentile T_s ≤ 0.60 while content T_c ≥ T_s + 0.10 (content moves, style stays in the agent's day-to-day band).
- **Cross-boundary fingerprint** (train on the predecessor's last ≤ 3 days, test on this period's first ≤ 3, day-demeaned): style balanced accuracy > content's and ≥ 2× chance.
- **Within period:** style identifies agents at least as well as content in a split-half test (first half of days → second half).
- **Kolchinsky–Wolpert** (periods #30 onward): within-agent style fluctuations carry no information about next-day output (scramble-null p ≥ 0.05).
- **Verdict rule:** supported if the entry-boundary and fingerprint conditions hold; failed if T_s > 0.60 and T_s ≥ T_c − 0.10, or style accuracy ≤ 1.5× chance; otherwise mixed. No entry boundary → descriptive.
- *Counts against:* style moving at the entry boundary as much as content does.

## Result
*Run 2026-10-04 06:10 UTC (`analysis/replication.py` → `data/processed/H46-style-conserved-charge/replication.json`). Templated replication point.*

- **Sample:** 10 agents, 10 days, 92 eligible agent-days (≥ 3 deduplicated chat messages).
- **Agent share of day-demeaned variance:** style 0.64, content 0.39.
- **Split-half fingerprint within the period:** style 0.89, content 0.53, chance 0.11.
- **Entry boundary 19->20** (adjacent, 8 agents): style T_s = 0.811 [0.647, 0.942] (raw 0.826); content T_c = 0.697 [0.547, 0.835].
- **Cross-boundary fingerprint:** style 0.83 vs content 0.46 at chance 0.12.
- **Templated verdict:** failed.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (beats the placebo band or not) and I (consistency across periods) in the main card.
