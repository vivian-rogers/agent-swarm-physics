# H27 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-11)

**Verdict:** descriptive (no evaluable onset)
**Verdict (1b):** mixed (native: hub wave in minutes)
**Role:** native (round 1b: the hub wave at the minute clock; round 1: exploratory transfer / false-alarm period)
**Period:** regime III · mode C · N = 15 · 5 active days in the series · W = 15: 85 windows, q = 4, 94% of windows with ≥ 3 labeled agents (mean 11.0); W = 30: 89%.

## Why this period
Own worlds plus a fixed hub given by the goal. Arms: W = 15 (primary) and W = 30 (coverage rule: ≥ 50% of windows with ≥ 3 labeled agents).

## Prediction
*Written 2026-10-04, before running on this period.*
- **P0 (onsets, O1 at W = 15):** 0–1 herding onsets.
- **P1 (early warning):** if ≥ 2 onsets are evaluable at lead ℓ = 4 (1 h), the composite AUC (τ_AR1 + τ_SD, onset vs placebo segments) is < 0.6, i.e. at chance. If 1 is evaluable, its composite sits inside the placebo bulk (percentile < 0.9).
- **P2:** any apparent signal comes from τ_SD or flickering, and shrinks after binomial standardization (rising mean, R3).
- **P3 (operator alarm, frozen τ*):** hits at most half of the onsets; its false-alarm rate per (project, window) is ≥ the synthetic 5%; the naive level alarm (share ≥ 0.3) gives the same or more lead.
- **Verdict rule:** with ≥ 2 evaluable onsets, **supported** if AUC ≥ 0.7 and the alarm hits ≥ half the onsets; **failed** if AUC < 0.6 and it hits < half; **mixed** otherwise. With 1 evaluable onset: **descriptive** (percentile reported). With none: **descriptive** (false alarms only).
- **What would count against my negative prior:** a supported verdict here, especially with the level alarm giving less lead.

## Result
Arm W = 15 min. τ* = 0.538 (frozen from synthetic S0). Onsets (O1): 0; O1-slow variant: 0. Onsets dropped at ℓ = 4: 0 too early (< 24 windows of history), 0 too sparse, 0 not low at t_e.

| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P0 onsets | 0–1 | 0 | – | as expected |
| P3 EWS alarm | hits ≤ half; FAR ≥ 5% | 0/0 hit (0 watchable); 7 false alarms in 186 watched (project, window) = 3.8%; PPV 0.00 | level alarm 0/0 hit, FAR 0.0% | as predicted |
| W = 30 arm | – | onsets 0; evaluable 0; AUC –; EWS hits 0/0 | – | robustness |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| G ground truth | 0 | onsets found by the rule: 0 (compare H11's narrative for this period) |

## Notes
- 2026-10-04: prediction written before running this period.
- 2026-10-04: round 1 run (`analysis/explore.py`); data in `data/processed/H27-herding-early-warning/G40/round1_w*.json`.

## Round 1b: the hub wave at the minute clock (native; H27-R2)
*Design and predictions written 2026-10-04 07:30 UTC, before computing anything below.* Round 1 found no onset in #40 (the hub was dominant from the first windows), and H53 found that the hub was link-seeded 2.4 min into the kickoff. A 15-min share series with 6 h of history cannot see a wave that starts at the kickoff; the round-2 redirect H27-R2 asks for a finer clock.

**What I had seen:** round 1's #40 results; H53's note (link 2.4 min into the kickoff, an 8-agent wave).

**Design.** Hub = the period's top attention project (label 1 in the shared labels). For each agent in #universe-coordination, the time of its first strict mention of the hub (`artifact_mentions`, agent speakers, how ∈ {url, output, bare}; same project map as the labels) after the first chat link to the hub; t₅₀ = the time until half of the room's agents have mentioned it. Work clock: the same with each agent's first work commit to the hub repo, if the hub is a repo.
- **M40-a:** ≥ 50% of the room's agents mention the hub within 30 min of the first link (t₅₀ ≤ 0.5 h).
- **M40-b:** the 15-min share series has no evaluable onset (no low baseline after ≥ 6 h of record): H27's design is structurally blind to this wave.
- **M40-c:** work follows attention: the work t₅₀ (if the hub carries work commits) is ≥ 1 h later than the attention t₅₀.

### Result (round 1b, run 2026-10-04)
`analysis/round1b.py compare` → `data/processed/H27-herding-early-warning/r1b/compare_r1b.json` (`g40`). Hub = the period's top attention project (a GitHub repo; 0.74 of labelled agent-windows). Room: the 14 agents in #universe-coordination.

| Test | Prediction | Observed | Verdict |
| --- | --- | --- | --- |
| M40-a t₅₀ after the first link | ≤ 30 min | first chat link 2.4 min after the kickoff; half the room (7/14) had a strict mention of the hub 1.5 min after that link (3.8 min after the kickoff); 11 of 14 within 8 min, the last three after ≈ 2.5 h | **supported** |
| M40-b no evaluable onset at 15 min | none | 0 onsets (W = 15 and 30), as in round 1 | **supported** |
| M40-c work t₅₀ ≥ 1 h after attention's | ≥ 1 h later | 13 of 14 agents committed to the hub (1,708 work commits in the week); half the room by 18.6 min after the kickoff, ≈ 15 min after the attention t₅₀; 9 committers within 20 min | **failed** (work follows within a quarter-hour) |

**Reading.** #40's pile-on is a kickoff wave that runs in minutes: the first agent touched the hub 1.9 min after the kickoff, posted its link at 2.4 min, and the room followed within 8 min, in attention and then in commits. A 6-hour early-warning window on 15-min shares cannot see it, by construction; the only usable signal is the announcement itself. Note: one agent's first mention (1.9 min) precedes the first chat link (an action, not a message), so "from the first link" understates the wave by about half a minute.
