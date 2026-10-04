# H64 × G12: debate tournament (10 debates) (2025-09-01 → 2025-09-05)

**Verdict:** supported
**Role:** native
**Period:** regime I · mode M · 7 agents · 1 room(s) · 5 days. Units: 12a, 12b. Prize class (pre-registered): **assigned**.

## Why this period
Native test: Ten judged debates with DQ6 teams, judges, verdicts and phase instants: the cleanest dated settlement of a rival-exclusive prize, with assigned sides.

## Prediction
*Written 2026-10-04 20:10 UTC, before running on this period (card predictions and Amendment A1).*

**Replication layer.** Assigned sides plus a judged prize. H64 and R-protocol both predict the highest r_p of all periods and excess antagonistic pairs.

**Native (H64-N1, judged debates).** Rivals = opposite-team debaters; prize open in the `pre` and `deb` phases, settled after the verdict (`post`); DQ6 phases and teams.
- **N1a:** γ_open < 0 (opponents more negative than teammates while the prize is open), relation-permutation p < 0.01 and cluster-bootstrap CI below 0 [0.9; known from H21/H37].
- **N1b (Amendment A1 rule):** the contrast vanishes after the verdict: Δ̂ = γ̂_open − γ̂_set < 0 with permutation p < 0.05, γ̂_set's CI includes 0, and |γ̂_set| < ½|γ̂_open| [0.7].
- **N1c (heat rival):** the teammates' open − settled shift φ̂ has a CI that includes 0 [0.6].
- **N1d (remanence rival):** after the verdict, losers → winners minus winners → losers has a CI that includes 0 [0.6].
- Primary outcome: soft stance s (Amendment A1); hard class as robustness. Counts against H64: N1b fails (the rival contrast survives settlement).

## Result
**Replication layer** (day-cluster bootstrap 95% CIs; agent-field null with 200 simulations).

| Unit | n replies | r_p (position) | confident opposes | mean stance s | negative pairs (robust) vs null mean (p_AF) | naive count |
| --- | --- | --- | --- | --- | --- | --- |
| 12 | 1311 | 0.032 [0.019, 0.052] | 0.055 [0.038, 0.078] | 0.45 [0.40, 0.50] | 0 vs 0.03 (1.000) | 0 |

**Native layer** (soft stance s primary; hard class robustness).

| Statistic | soft s | hard class |
| --- | --- | --- |
| γ_open (rival − other, open) | -0.779 [-1.099, -0.565] | -0.849 [-1.212, -0.556] |
| γ_set (rival − other, settled) | -0.093 [-0.388, +0.257] | -0.198 [-0.363, +0.163] |
| Δ = γ_open − γ_set | -0.686 [-1.199, -0.270] | -0.651 [-1.195, -0.264] |
| permutation p (γ_open; Δ) | 0.0002; 0.0010 | 0.0002; 0.0156 |
| rival replies open / settled | 87 / 64 | |
| heat φ (teammates, open − settled) | +0.002 [-0.235, +0.335] | -0.003 |
| resentment (losers → winners − winners → losers, post) | +0.187 [-0.042, +0.329] (n 64) | |

N1a pass; N1b pass; N1c pass; N1d pass.

## Scorecard (period-specific axes)
- **E (interventional):** ten dated settlements (verdicts); see the result.
- **G (ground truth):** DQ6 teams, judges and phases.
- **H (comparative):** heat and remanence rivals tested (N1c, N1d).

## Notes
- Data: `data/processed/H64-conflict-scarce-prize/replication/units.json`, `natives/G12.json`. Holdout masked (`holdout_mask`); no held-out day enters.
