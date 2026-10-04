# H56 × NE14: regime II → III, perma-computer-use (scored at 2026-03-24)

**Verdict:** failed
**Role:** native (exploratory, round 1, non-holdout)
**Period:** spans the NE14 boundary inside goal #36 (named exception (c): the transition is the object). Pre = 03-19, 03-20 (#35) and 03-23 (#36 kickoff day), regime II; post = 03-24, 03-25 (before NE16 on 03-26), regime III. 12 agents present on both sides. The 03-11 → 03-16 rollout dates are held out (NE30 window).

## Why this period
The one scaffold change whose effect on the turn chain is certain from the logs alone: on 03-24 computer-use sessions (≈ 500–600 session start/stop events a day in 03-16 → 03-23) are replaced by consolidations (0 before, ≈ 200 a day after) and WAIT events stop (21–64 a day → 0). If entropy production fingerprints the platform, this is where it must jump, and the jump should sit in the scaffold transitions (session/consolidate boundary), not in the agent's own action choices.

## Prediction
*Written 2026-10-04 06:00 UTC (card P8), before any real-data EP.* V1 and V3 per-transition EP fall across 03-24 for ≥ 80% of agents, with |t| beyond every weekday-matched placebo [0.8]. The coarse fall is ≥ 50% carried by scaffold transitions: |Δ̄(V4)| ≤ 0.5 |Δ̄(V3)| [0.5]. Native design: 3 pre + 2 post days, within-agent count-matched Newton bound with (day × quarter) folds; null = the same statistic on 35 eligible Tuesdays (any regime) more than 2 days from any scaffold-tool event (Amendment 3; the pre-registered placebo pool had 6 Tuesdays).

## Result
| chain | Δ̄ (nats/transition) | relative | agents falling | t | p (35 Tuesdays) | max placebo \|t\| |
| --- | --- | --- | --- | --- | --- | --- |
| V1 fine, all records | −0.037 | −28% | 8/12 | −1.33 | 0.33 | 2.91 |
| V2 fine, agent-only (cut) | −0.030 | −33% | 9/12 | −1.82 | 0.17 | 2.73 |
| V5 fine, agent-only + burn-in | −0.030 | −35% | 8/12 | −1.91 | 0.11 | 2.79 |
| V3 coarse, all records | −0.021 | −45% | 8/12 | −1.54 | 0.33 | 3.18 |
| V4 coarse, agent-only (cut) | −0.013 | −77% | 9/12 | −2.21 | 0.08 | 2.27 |
| V6 coarse, agent-only + burn-in | −0.015 | ≈ −100% | 9/12 | −2.96 | 0.03 | 2.78 |

- EP falls in two thirds to three quarters of agents (coarse median 0.028 → 0.007 nats/transition; fine median 0.095 → 0.055), but the within-agent t is inside the Tuesday-to-Tuesday spread on every all-records chain. Responses are heterogeneous: on the fine chain both Gemini agents and 4 of 5 Claude agents fall while 3 of 4 GPT agents rise (figure).
- Scaffold carriage on coarse states: |Δ̄(V4)| / |Δ̄(V3)| = 0.62 (V6: 0.71), i.e. most of the coarse fall is in the agent's own transitions, not in the scaffold records. (A first run with different subsampling seeds gave 0.50 / 0.55: the ratio is noisy at 12 agents.)
- The coarse consolidate/session sector alone (Newton on pairs involving the boundary state, V3): Δ̄ −0.011, relative −36%, t −1.04.
- The replication-layer event (3 + 3 days, window includes the NE16 day 03-26): V1 t −1.18 (p 0.38 against the Amendment-3 null), V3 t −2.40 (p 0.017).
- P8 fails on both counts: 67% (not ≥ 80%) of agents fall and |t| is not beyond the placebos; the change is not carried by scaffold transitions.

Figure: `figures/ne14_agents.pdf`. Data: `data/processed/H56-ep-platform-fingerprint/native/NE14.json`.

## Scorecard (period-specific axes)
- **E (interventional):** 0. The largest scaffold change in the dataset moves per-transition EP by −28% (fine) to −45% (coarse), within day-to-day variability.
- **G (ground truth):** the switch is unambiguous in the event types (sessions → consolidations exactly on 03-24); EP does not single it out.

## Notes
- 2026-10-04: the "consolidate" act class is regime-specific (session start/stop in regime II, CONSOLIDATE in regime III); the coarse states merge them, so only coarse sector statistics are comparable across the boundary.
- The 03-24 date is where the switch shows in the logs, although the changelog places related work from 03-11; the 03-11 → 03-13 provider-staggered rollout is in the holdout and is targeted by `analysis/confirm.py`.
- **2026-10-04, ep_newton recheck (post hoc).** Held-out Newton bound. V1: 7/12 agents fall (was 8/12), −18% (was −28%), t −0.83 (was −1.33), Tuesday p 0.56 (was 0.33). Coarse V3: −31%, t −0.99. Carriage: fine V2/V5 1.06/1.03 (was 0.82/0.82), coarse V4/V6 0.55/0.88 (was 0.62/0.71). The verdict stays **failed**.
