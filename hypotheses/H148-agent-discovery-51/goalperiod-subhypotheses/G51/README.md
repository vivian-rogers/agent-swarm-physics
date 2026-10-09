# H148 × G51: autonomous agent discovery in #51 (2026-07-06 → 09-04; 51m reserved)

**Verdict:** failed
**Role:** exploratory
**Period:** regime III · 32 panel agents (Claude Code agents excluded) · #general and #focus (from 08-05) · 45 non-reserved active days, 8 h each. Step changes inside the period (NE38 07-29, #focus and bookends 08-05, nudges stop 08-20, roster joins) are not splits here; the odd/even day split crosses all of them.

## Why this period
#51 is the longest single goal period with many agents, own repos, shared repos and a rich element set (H145). It is the paper-2 period. The 51m tail is the frozen confirmation window.

## Prediction
*Written 2026-10-09, before running on this period (after the synthetic check; see the card's Round 1 amendments A1-A8).*
The card's P1-P7 apply as written, with the amended estimator. Expected: most agents are single-atom individuals; few agent + own-repo systems pass both directions (synthetic power for that link is low); the Echoes pair is the one candidate multi-agent individual; at most a few element systems; no role-text or operator-topic system; the time-rotated search finds no multi-atom system. What counts against the card: P1 < 50%; any role-text or operator-topic discovery (P5, K2); rotated data as rich as real data (P7, K1).

## Result
*Run 2026-10-09 on non-reserved days (07-06 → 09-04), 30-min bins; data in `data/processed/H148-agent-discovery-51/results/`.*

| Prediction | Observed (95% CI) | Null / calibrator | Verdict |
| --- | --- | --- | --- |
| P1 agents found (≥ 90%) | 1/27 = 0.04 [0.01, 0.18] single-atom individuals (DeepSeek-V3.2); post hoc cross-day null: 20/27 = 0.74 [0.55, 0.87] | within-(day, E) permutation of the agent's own states | failed |
| P2 agent + own repo | 0/25 | — | untestable (synthetic power ≤ 0.08) |
| P3 ≥ 3 agents' worth | no multi-atom system; 0/16 local maxima hold out of sample | day-permutation of the candidate | not identifiable (K3) |
| P4 memeplex individual | no element system; 1/72 local maxima holds in one direction only | day-permutation | not identifiable (K3) |
| P5 no field system | 0 discovered element systems | — | supported (vacuous) |
| P6 κ > 0 | no candidate | — | not testable |
| P7 rotated ≤ 10% of real | local maxima 13.3 vs 16 (agents), 69.0 vs 72 (elements) | within-day rotation of every atom | failed (K1) |

Figure: `../../figures/g51.pdf` (single-atom z per agent; search summary).

## Scorecard (period-specific axes)
C 0 (in-sample maxima match rotated data); D 0 (nothing to test); E 0 (no candidate for κ); G 0 (1/27 agents found as pre-registered).

## Notes
- 2026-10-09: agents hold one project for most of a day, so at 30 min the self-information of an agent is day-level; the pre-registered within-day null puts it in the null. The synthetic agents lacked day-level persistence.
- 2026-10-09: a diagnostic script computed plug-in lagged information for the 12 real agent–own-repo pairs before the synthetic commit (median 0.047 bits); see the card's Round 1 disclosure.
