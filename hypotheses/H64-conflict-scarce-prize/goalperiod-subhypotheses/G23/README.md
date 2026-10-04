# H64 × G23: chess tournament (2025-12-15 → 2025-12-19)

**Verdict:** mixed
**Role:** native
**Period:** regime I · mode K · 10 agents · 1 room(s) · 5 days. Units: one unit. Prize class (pre-registered): **competition**.

## Why this period
Native test: A chess tournament: explicit zero-sum opponents with game-level prizes that open and close at known (linked) times, without assigned debate roles.

## Prediction
*Written 2026-10-04 20:10 UTC, before running on this period (card predictions and Amendment A1).*

**Replication layer.** A rival-exclusive prize is live for the whole period (a single winner). H64 predicts **elevated antagonism**: r_p above the prize-free median and/or excess antagonistic pairs (p_AF ≤ 0.05). R-protocol (H37) predicts the prize-free level. My credence for H64's direction here: 0.25.

**Native (H64-N3, chess games).** Rivals = two agents who both link the same Lichess game in chat (13 two-agent games, 12 opponent pairs); a game is open from its first to its last link plus 10 min. γ_open = opponents' replies during one of their open games minus non-opponent replies (day fixed effects); γ_set = opponents' replies at other times.
- **N3a:** γ_open < 0 with node-label permutation p < 0.05 [0.15]. 44 opponent replies fall inside open windows (testable; synthetic power 0.47 at Δ = −2 logit on hard labels).
- H22 found no stance contrast between opponents over the whole week (−0.005), which H64 explains only if the antagonism is confined to open games.

## Result
**Replication layer** (day-cluster bootstrap 95% CIs; agent-field null with 200 simulations).

| Unit | n replies | r_p (position) | confident opposes | mean stance s | negative pairs (robust) vs null mean (p_AF) | naive count |
| --- | --- | --- | --- | --- | --- | --- |
| 23 | 388 | 0.034 [0.012, 0.071] | 0.054 [0.033, 0.103] | 0.38 [0.34, 0.43] | 0 vs 0.07 (1.000) | 0 |

Competition: r_p 0.0335 above the prize-free median 0.0094; excess antagonistic pairs: no.

**Native layer** (soft stance s primary; hard class robustness).

| Statistic | soft s | hard class |
| --- | --- | --- |
| γ_open (rival − other, open) | -0.128 [-0.410, +0.251] | -0.088 [-0.521, +0.448] |
| γ_set (rival − other, settled) | +0.037 [-0.224, +0.311] | +0.016 [-0.365, +0.440] |
| Δ = γ_open − γ_set | -0.165 [-0.391, +0.155] | -0.104 [-0.429, +0.320] |
| permutation p (γ_open; Δ) | 0.3087; 0.1967 | 0.4228; 0.3621 |
| rival replies open / settled | 44 / 87 | |
| games / opponent pairs | 13 / 12 | |

N3a not passed.

## Scorecard (period-specific axes)
- **E:** dated settlement(s) used; low power (Amendment A1).
- **G:** DQ6 (G26) or linked game pairs (G23).

## Notes
- Data: `data/processed/H64-conflict-scarce-prize/replication/units.json`, `natives/G23.json`. Holdout masked (`holdout_mask`); no held-out day enters.
