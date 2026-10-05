# H46 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-22)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime III · 15 agents with eligible days · rooms [2, 3] · 5 days with eligible agent-days · units 42a, 42b.

## Why this period
A replication point for the common estimator (layer 1): every eligible goal period gets the same statistics, so periods are comparable points, not independent tests.

## Prediction
*Written 2026-10-04 05:45 UTC, before running on this period. Templated replication prediction (layer 1), the same for every period.*
- **Entry boundary** (#41 → #42, adjacent): type-controlled style percentile T_s ≤ 0.60 while content T_c ≥ T_s + 0.10 (content moves, style stays in the agent's day-to-day band).
- **Cross-boundary fingerprint** (train on the predecessor's last ≤ 3 days, test on this period's first ≤ 3, day-demeaned): style balanced accuracy > content's and ≥ 2× chance.
- **Within period:** style identifies agents at least as well as content in a split-half test (first half of days → second half).
- **Kolchinsky–Wolpert** (periods #30 onward): within-agent style fluctuations carry no information about next-day output (scramble-null p ≥ 0.05).
- **Verdict rule:** supported if the entry-boundary and fingerprint conditions hold; failed if T_s > 0.60 and T_s ≥ T_c − 0.10, or style accuracy ≤ 1.5× chance; otherwise mixed. No entry boundary → descriptive.
- *Counts against:* style moving at the entry boundary as much as content does.

## Result
*Run 2026-10-04 06:10 UTC (`analysis/replication.py` → `data/processed/H46-style-conserved-charge/replication.json`). Templated replication point.*

- **Sample:** 15 agents, 5 days, 62 eligible agent-days (≥ 3 deduplicated chat messages).
- **Agent share of day-demeaned variance:** style 0.70, content 0.62.
- **Split-half fingerprint within the period:** style 0.67, content 0.69, chance 0.08.
- **Entry boundary 41->42** (adjacent, 14 agents): style T_s = 0.890 [0.832, 0.954] (raw 0.830); content T_c = 0.906 [0.822, 0.976].
- **Cross-boundary fingerprint:** style 0.55 vs content 0.29 at chance 0.07.
- **KW (next-day output, within agent):** style p = 0.970, content p = 0.060 (small periods are underpowered and their raw CV R² is inflated; Amendment 3).
- **Templated verdict:** failed.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (beats the placebo band or not) and I (consistency across periods) in the main card.

## Round 2 (2026-10-05)
**Round-2 result (replication, regime III):** context-held style state ΔC(1) 1.22 [-1.77, 3.53]; self-pull context minus erased 0.090 [-0.314, 0.232].
*Pre-registered in the card (Round 2, 2026-10-05 02:44 UTC), synthetic validation and amendments R2-A1..A5 before this run; `analysis/r2_run.py` → `data/processed/H46-style-conserved-charge/r2/`. Non-reserved data.*
- Templated R2 statistics (no period verdict): cross-product of the 17-d style (genre + position removed) for lag-1 message pairs within a context segment minus pairs across a forced erasure, gap-matched (234 across pairs, 15 agents); the pull coefficient toward the agent's last ≤ 3 messages in context vs erased.
- NE41 forced-erasure style percentile (gp) in this period's units: 42b 0.60.
