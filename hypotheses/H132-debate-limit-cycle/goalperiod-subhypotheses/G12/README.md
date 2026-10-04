# H132 × G12: The debate tournament (2025-09-01 → 2025-09-05)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · one room (#general) · 7 agents · 10 Asian-Parliamentary debates on 09-01 → 09-04 (unit 12a; 12b on 09-05 has no debate). Each debate has its own judge, motion and drafted Government/Opposition teams (re-drafted every debate except #7 = #6).

## Why this period
It is the only non-holdout period with drafted opposing teams and a turn schedule, so the two sublattices and the update order are known (DQ6, H21 labels). The judge's verdict is a dated switch-off of the debate in each of ten debates, and re-drafting lets the same agent pair be seen as opponents and as teammates.

## Prediction
*Written 2026-10-04 22:24 UTC, before running on this period.*
- **Replication (card P1–P6):** Λ > 0 beyond the turn-shuffled null (credence 0.15), ρ₁ < 0 and ρ₂ > 0; A_γ ≠ 0 (0.10); no alternation within teams at message level (0.80); topic echo in the full vector, ρ₁^vec > 0 (0.60). Per debate: ρ₁ < 0 in ≥ 7/10 debates if P1 holds. Against: Λ not beyond the null (kill K).
- **N1 verdict switch-off (native).** In the 10-min post phase (H21's rule), turns keep alternating speakers but no motion is contested. Prediction: Λ_post < Λ_deb, and Λ_post is not beyond the shuffle null (p ≥ 0.05). If P1 fails, N1 is uninformative and is reported as such. **Credence 0.7 conditional on P1; 0.2 that N1 is informative at all.** Against: Λ_post ≥ Λ_deb with Λ_deb > 0.
- **N2 read gate (native).** For each lag-1 turn pair (t → t+1), the responding turn's first message is *visible-exposed* if its producing call started after the previous turn's last message was posted (`producing_calls.t_call_prod` > that message's time), else *in flight*. Prediction under the limit cycle: ρ₁(visible) < ρ₁(in flight), with ρ₁(in flight) ≈ 0. Statistic: Δρ₁ = ρ₁(visible) − ρ₁(in flight), shuffle null within debate × team × visibility class. **Credence 0.15** (conditional on P1: 0.6). Against: Δρ₁ ≥ 0.
- **N3 re-drafting within pairs (native).** Message-level consecutive pairs (a then b, a ≠ b, both debaters). For each unordered pair seen both as opponents and as teammates, the mean product of team-centred projections as opponents minus as teammates; sign-flip test over pairs. Prediction (limit cycle): negative (pairs anti-correlate only when drafted opposite). **Credence 0.15.** Against: contrast ≥ 0.

**A1 note (2026-10-04 23:10 UTC, before running):** P1 passes when Λ and ρ₁ are significant and ρ₂ exceeds its null mean (the both-significant clause had power 0.20–0.33 in cycle worlds). Kill K unchanged.

## Result
*Run 2026-10-04 23:11 UTC, 5,000 turn shuffles per statistic. Data: `data/processed/H132-debate-limit-cycle/results/results.json`. Figure: `../../figures/summary_obs_col.pdf`.*

| Statistic | bge masked (primary) | gte masked | bge unmasked | gte unmasked | Shuffle null (bge m, 5–95%) |
| --- | --- | --- | --- | --- | --- |
| ρ₁ (lag 1, cross-team) | +0.161 (p_hi 0.002) | +0.086 | +0.133 | +0.131 | −0.096 to +0.097 |
| ρ₂ (lag 2, same team) | +0.209 (p_hi 0.0002) | +0.129 | +0.162 | +0.142 | |
| Λ = ρ₂ − ρ₁ | +0.047 (p 0.081) | +0.043 (0.105) | +0.029 (0.110) | +0.010 (0.174) | |
| A_γ | +0.048 (p 0.71) | +0.020 | +0.108 | +0.039 | |
| L | −0.071 (p 0.39) | −0.150 (0.09) | −0.168 (0.04) | −0.130 (0.13) | |
| ρ₁^vec (topic) | +0.145 (p 0.0002) | +0.178 | +0.182 | +0.187 | |
| msg ρ_same / ρ_cross | +0.30 / +0.12 | +0.20 / +0.05 | +0.20 / +0.09 | +0.22 / +0.12 | |

- Per debate (bge masked) ρ₁: +0.32, +0.36, −0.10, +0.66, +0.16, +0.24, +0.36, +0.07, −0.41, +0.27; raw Gov − Opp > 0 in 8/10 debates.
- **N1 verdict switch-off:** Λ_post −0.18 (p 0.61); uninformative because there is no cycle during the debate.
- **N2 read gate:** ρ₁(visible) − ρ₁(in flight) = −0.006 (p 0.47). Failed.
- **N3 re-drafted pairs:** opponents − teammates −0.047 over 18 pairs (sign-flip p 0.29; gte +0.08). Failed.

## Scorecard (period-specific axes)
C 1 (persistence beats the null; the cycle does not); D 1 (cycle signature absent; within-team prediction holds); E 0 (switch-off uninformative); G 1 (DQ6 teams verified; static tilt reproduced).

## Notes
- 2026-10-04 22:24 UTC: folder created from the template; predictions written before any H132 statistic.
- 2026-10-04 23:13 UTC: results added.
