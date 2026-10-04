# H02 × G12: Debate tournament, 10 debates with re-drafted teams (2025-09-01 → 2025-09-05)

**Verdict:** failed
**Role:** native
**Period:** regime I · mode M (teams) · 7 agents · one room (#general) · 10 debates on 09-01 → 09-04 (13–33 min each), teams re-drafted every debate, rotating judges (DQ6 ground truth: team 60, judge 10, phase 30 rows).

## Why this period
The only non-holdout period with a known, changing directed structure (DQ9 cross-index: H02 → #12). Asian-Parliamentary speeches alternate between the two teams, and the judge speaks at the verdict. Because teams are re-drafted every debate, the same pair of agents is on the same side in some debates and opposite in others, so a team-relation coupling is separated from pair identity (fixed-pair couplings, family fields, scheduling).

## Prediction
*Written 2026-10-04 06:52 UTC, before any #12 fit.*
Model (a relation-structured kinetic Ising, H02's KI-1 with the pairwise J replaced by relation couplings): on 1-min **talk** spins inside the debate windows (round-1b `activity_bins_fixed`), for each debater i,
logit P(s_i(t+1) = +1) = 2[h_i + δ(debate, 10-min block) + J_self s_i(t) + J_same m_same,i(t) + J_opp m_opp,i(t) + J_judge s_judge(t)],
where m_same / m_opp are the mean talk spins of i's current teammates / opponents. Null: team labels re-drafted at random within each debate (team sizes kept), 500 permutations.
- **N12-a (format → couplings).** If lagged couplings measure who responds to whom, alternation makes J_opp − J_same > 0 with permutation z ≥ 2.
- **N12-b (judge).** J_judge (judge → debaters, lag 1 min) has permutation |z| ≥ 2.
- **My expectation (round 1's reading, timing carries scheduling, not influence):** both |z| < 2. Credence 0.65 for the null outcome.
- Verdict rule: **supported** if N12-a holds; **failed** if |z(J_opp − J_same)| < 2 or the sign is negative; N12-b is secondary.

## Result
*Run 2026-10-04 (round 1b data). 10 debates, 295 debate-minutes, 1,668 debater transitions.*

| Statistic | Talk spins (primary) | Active spins (secondary) | Null | Reading |
| --- | --- | --- | --- | --- |
| J_self | 0.093 | 0.052 | – | own persistence |
| J_same (teammates → i) | −0.027 | −0.007 | – | |
| J_opp (opponents → i) | −0.068 | −0.064 | – | |
| **J_opp − J_same** | **−0.041, z = −0.32** (p = 0.74) | −0.057, z = −0.48 | re-draft permutation (500) | **N12-a fails:** no alternation signature; wrong sign |
| J_judge (judge → debaters) | −0.000, z = −0.13 | −0.036, z = −0.89 | judge series circularly shifted (300) | N12-b fails |

- **Verdict: failed** (as expected, credence 0.65 for the null). The debate's known directed structure (Government/Opposition alternation, the judge's verdict) is invisible in 1-min talk or activity timing, even though teams are re-drafted every debate so pair identity cannot hide it.
- This is the period-native form of round 1's conclusion: minute-level activity timing carries scheduling, not who responds to whom. The same structure *is* visible in stance (H37: opponents −0.13 vs teammates +0.32) and in content near the motion (H21), i.e. in what agents say, not when.

## Scorecard (period-specific axes)
- **G ground truth: 0.** Known team and judge structure not recovered.
- **H comparative: 0.** The relation model does not beat its re-draft null.

## Notes
- Code: `analysis/r1b_native.py g12`; output `data/processed/H02-couplings-are-real/r1b/native_g12.json`.
