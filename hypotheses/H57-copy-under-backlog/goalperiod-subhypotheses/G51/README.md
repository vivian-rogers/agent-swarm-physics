# H57 × G51: Maximize your private assigned role (non-holdout units 51a–51l)

**Verdict:** failed (the pre-registered slopes are negative; the raw upper bound is +0.0007 per doubling; the N sweep is weakly positive in gte only)
**Role:** native
**Period:** 2026-07-06 → 09-18 · units 51a–51l (non-holdout, through 09-04), **51m (09-07 → 09-18) holdout** · N 21 → 32 · 55 d (45 non-holdout days, 362.8 act h), 8 h/day · regime III · **one room (#general)**, plus #focus (from 08-05; structural in 51g), side-room (07-24, 4 h), onboarding rooms (sol/terra/luna 07-09 → 07-10, Grok 4.5 07-10 → 07-13). Non-holdout statements with backlog k ≥ 1: 33745 by 32 agents. The tail (09-07 →) is held out.

## Why this period
The roster grows from 21 to 32 agents in 11 dated steps at a fixed goal, hours and (mostly) one room, so the backlog grows for reasons unrelated to content. It is also the period with the heaviest backlog tail (k ≥ 30 is common) and by far the most statements (≈ 34k), so it carries most of H57's power. Native observables: the unit-level N sweep, the high-k tail and family heterogeneity, plus the replication estimator.

## Prediction
*Written 2026-10-04 07:09 UTC, before running H57 on this period.*
- **N51a (replication estimator, most powered):** β_echo > 0 in both models and β_mk > 0, each with p < 0.05.
- **N51b (N sweep):** across the 12 non-holdout units, the unit-mean chance-corrected echo rises with the unit's median log k (Spearman > 0; one-sided permutation p < 0.1 given 12 units), and the median log k rises with N.
- **N51c (high-k tail):** within agent × unit, statements with k ≥ 30 have a higher chance-corrected echo than those with k ≤ 3.
- **N51d (P3 here):** T > 0 on the near-coded addressed channel (both models).
- **Against:** a flat or falling echo across the k bins and units.

## Result
*Run 2026-10-04 (non-holdout units 51a–51l). Numbers: `results/G51.json`, `results/native_G51.json`. Figure: [figures/g51_sweep.pdf](figures/g51_sweep.pdf).*

33,745 statements with k ≥ 1 by 32 agents; median k 5, q90 26; 2,822 statements with k ≥ 30.

| Native prediction (dated) | Observed | Verdict |
| --- | --- | --- |
| N51a: β_echo > 0 (both models) and β_mk > 0, p < 0.05 | chance-corrected: bge −0.0023 ± 0.0006, gte −0.0018 ± 0.0006, marker −0.039 ± 0.004 (all p < 1e-4) | not met (biased estimator, card Amendment 2) |
| N51b: unit-mean echo rises with unit median log k (Spearman > 0, one-sided p < 0.1) | bge ρ 0.19 (p 0.28); gte ρ 0.41 (p 0.09); marker ρ −0.36. Median log k rises with N (ρ 0.52) | mixed (gte only) |
| N51c: echo higher at k ≥ 30 than at k ≤ 3 (within agent × unit) | chance-corrected bge −0.012 (z −7.5); raw echo bge +0.0026 ± 0.0024, gte +0.0024 ± 0.0023; lag-matched bge −0.027 | not met on the pre-registered outcome |
| N51d: T > 0 on the near-coded addressed channel | copy share 0.000 → 0.0003 (bge), 0 → 0 (gte); T ≈ 0 | not met |
| Post hoc: raw read-set echo slope (upper bound) | bge +0.0007 ± 0.0004, gte +0.0007 ± 0.0004 per doubling (p < 0.002) | tiny |
| Post hoc: lag-matched count slope | bge −0.0055 ± 0.0006, gte +0.0003 ± 0.0004 | no rise |
| Post hoc: N sweep on raw echo | bge ρ 0.35 (p 0.13), gte ρ 0.58 (p 0.025) | weak |
| Family heterogeneity (raw echo slope) | 7 families: −0.0003 (xAI) to +0.0019 (Zhipu) | none large |

**Reading.** #51 carries most of H57's power. Even the most generous estimator (raw read-set echo, which also counts chance near-copies that grow with k) rises by only 0.07 percentage points per doubling of backlog, against a mean echo rate of 0.15%. That is far below the +3 points the synthetic load world plants. The near-copy rate of the message an agent addresses is ≈ 0.1% at every backlog: in this period agents transform what they respond to.

## Scorecard (period-specific axes)
- **C:** 0. **D:** 0. **I (transfer):** not tested (the tail is held out; `analysis/confirm.py` targets it).
