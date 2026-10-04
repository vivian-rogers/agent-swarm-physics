# H64 × G26: elect a leader who sets the goal (2026-01-05 → 2026-01-09)

**Verdict:** mixed
**Role:** native
**Period:** regime I · mode C · 10 agents · 1 room(s) · 5 days. Units: one unit. Prize class (pre-registered): **competition**.

## Why this period
Native test: An election with exact ballots (DQ6): a 9–9–9 approval tie, a runoff among three candidates and a dated result, then an uncontested re-election.

## Prediction
*Written 2026-10-04 20:10 UTC, before running on this period (card predictions and Amendment A1).*

**Replication layer.** A rival-exclusive prize is live for the whole period (a single winner). H64 predicts **elevated antagonism**: r_p above the prize-free median and/or excess antagonistic pairs (p_AF ≤ 0.05). R-protocol (H37) predicts the prize-free level. My credence for H64's direction here: 0.25.

**Native (H64-N2, an election).** Rivals = pairs among the three tied approval-vote candidates (agents 0, 6, 17), who contested the runoff. Prize open from the first agent message of 2026-01-05 to the result (19:35:22 UTC); settled from the result to the confirmatory vote (01-09 18:45 UTC); the confirmatory window (an uncontested 9–0 re-election) reported separately.
- **N2a:** γ_open < 0 with exact rival-set permutation p < 0.05 (all 120 three-agent sets) [0.15]. 14 rival replies fall in the open window, so the expected verdict is **inconclusive** (synthetic power ≤ 0.33 at Δ = −2 logit on hard labels).
- **N2b (descriptive):** the confirmatory window looks like the settled one (the rival contrast there has a CI that includes 0).

## Result
**Replication layer** (day-cluster bootstrap 95% CIs; agent-field null with 200 simulations).

| Unit | n replies | r_p (position) | confident opposes | mean stance s | negative pairs (robust) vs null mean (p_AF) | naive count |
| --- | --- | --- | --- | --- | --- | --- |
| 26 | 1023 | 0.011 [0.006, 0.017] | 0.027 [0.015, 0.039] | 0.56 [0.52, 0.60] | 0 vs 0.04 (1.000) | 0 |

Competition: r_p 0.0108 above the prize-free median 0.0094; excess antagonistic pairs: no.

**Native layer** (soft stance s primary; hard class robustness).

| Statistic | soft s | hard class |
| --- | --- | --- |
| γ_open (rival − other, open) | +0.250 [-0.515, +0.454] | +0.210 [-0.782, +0.551] |
| γ_set (rival − other, settled) | -0.035 [-0.168, +0.120] | -0.036 [-0.205, +0.178] |
| Δ = γ_open − γ_set | +0.284 [-0.484, +0.520] | +0.246 [-0.757, +0.597] |
| permutation p (γ_open; Δ) | 0.8632; 0.8889 | 0.7094; 0.7863 |
| rival replies open / settled | 14 / 65 | |
| confirmatory window: rival contrast | +0.012 [-0.162, +0.193] (n 33) | |

N2a not passed (exact permutation over 116 rival sets).

## Scorecard (period-specific axes)
- **E:** dated settlement(s) used; low power (Amendment A1).
- **G:** DQ6 (G26) or linked game pairs (G23).

## Notes
- Data: `data/processed/H64-conflict-scarce-prize/replication/units.json`, `natives/G26.json`. Holdout masked (`holdout_mask`); no held-out day enters.
