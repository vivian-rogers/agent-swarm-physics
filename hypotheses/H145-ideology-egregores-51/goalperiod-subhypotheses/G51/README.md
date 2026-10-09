# H145 × G51: #51, private-role village (2026-07-06 → 09-04, exploration span)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime III · 32 agents (11 joins during the period) · 8 labs · rooms #general, #rest, #focus (from 08-05) · 45 non-reserved active days. Step changes inside the period (covariates, not splits, in round 1): 07-29 NE38, 08-05 #focus and bookends, 08-20 nudges stop, roster joins. The reserved tail 51m (09-07 → 09-18) is masked.

## Why this period
#51 is the longest regime-III period with private role texts (a measurable field, e3), many joins (newcomers test host renewal) and a qualitative reading that names candidate ideologies (verify-and-correct, consent, governance, onboarding, frameworks).

## Prediction
*Written 2026-10-09, before running on this period.* The card's P1–P6 as amended in Round 1 (A1–A3; A4–A5 added after the P2/P3 synthetic check, before real P2/P3): ≥ 3 qualifying hub-free memeplexes beyond the A2 null; ≥ 2 of them renew their hosts (P2); ≥ 1 of those is a colonial individual beyond E at 2 h (P3); role-text patterns are fields (P4); the verify and onboarding patterns are among the P2 patterns (P5); colonial A peaks at 1 day (P6).

## Result
Data: `data/processed/H145-ideology-egregores-51/` (`memeplexes.json`, `results/p1.json`, `tests.json`, `p6.json`, `posthoc.json`). Figures: `../../figures/r1_synth.pdf`, `../../figures/r1_obs.pdf`.

| prediction | observed | null | verdict |
| --- | --- | --- | --- |
| P1 memeplexes exist | 15 hub-free qualifying | agent-scope rotation: mean 3.4, 95th pct 6 | supported |
| P2 host renewal (A4) | 3/15 pass (K03, K07; K14 on a degenerate null) | pseudo-pattern 95th pct | supported, fragile |
| P2 as written | 1/15 | — | untestable (power 0.20) |
| P3a colonial A (A5) | K03 z 2.96, excess 0.20 [0.07, 0.33] bits | pseudo-patterns, 200 draws | supported, fragile |
| P3 with Δ | not computed | — | untestable |
| P4 field controls | R0–R5 A* z ≤ 1.02, A z ≤ 1.37 | pseudo-patterns | failed (control uninformative) |
| P5 labels | P2 set = governance, frameworks, unlabelled; no verify/onboarding | — | failed |
| P6 time scale | K03, K07 peak at 30 min | — | failed (exploratory) |

## Scorecard (period-specific axes)
C 1 (held-out gains measured), D 1 (labels fixed before outcomes; P5, P6 failed), E 0, G 0 (field controls without A*).

## Notes
- 2026-10-09: memeplexes frozen in `data/processed/H145-ideology-egregores-51/memeplexes.json` before any test outcome.
