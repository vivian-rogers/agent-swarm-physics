# H63 × G40: Connect your worlds into a 3D universe (NE42 merge; 2026-05-04 → 05-08)

**Verdict:** supported (native control); descriptive (replication)
**Role:** native + replication (exploratory)
**Period:** regime III · one merged room (#universe-coordination; GPT-5 alone in #rest) · 15 agents · 5 days. 2,945 agent work commits (13 agents), 313 deploys; one shared hub artifact.

## Why this period
The goal names one shared artifact, so herding onto the hub is set by the kickoff field (H31: frozen at the kickoff; H27 round 1b: first touch 1.9 min after the kickoff, first link 2.4 min, half the room committing by 18.6 min). A work-signal trigger is not expected here: this is the negative control for H63.

## Prediction
*Written 2026-10-04 19:35 UTC, before running on this period. Seen: H27's #40 minute-clock result; no H63 statistic.*
- **N40a:** the hub's first herding burst is kickoff-led (t₀ within 60 min of the goal's first window start) and its follower onset precedes the hub's first deploy event. [0.7]
- **N40b:** the share of #40 bursts with an S signal in the 60 min before the follower onset is not above the matched non-burst share (OR_S CI includes 1). [0.55]
- **Counts against the control:** the hub burst starts after a deploy event (then the work signal and the kickoff are not separable here).

## Result
### Native test
- **N40a supported:** the hub's first herding burst (11 agents, untrimmed) starts 1.9 min after the first window of the goal (kickoff-led). Its follower onset comes 95 min before the hub's first deploy event.
- **N40b supported:** OR_S = 7.9 with 95% CI [0.45, 139] includes 1 (2 trimmed bursts only).
- **Reading:** the field-led control behaves as expected. The kickoff starts the hub wave; work signals come much later.
### Replication statistics
*Run 2026-10-04 ~20:45 UTC (trimmed window: all-present, ≥ 30 min after each agent's first call).*

| Statistic | Value |
| --- | --- |
| herding bursts (≥ 3 agents) · matched 1–2-agent clusters | 2 · 71 |
| bursts / controls with a state change (S) in the 60 min before the follower onset | 1/2 · 8/71 |
| OR_S [95%] (Haldane) · z vs S time-shift | 7.88 [0.45, 138.59] · 1.08 |
| bursts / controls with an agent chat link in the 60 min before | 1/2 · 17/71 (OR_L 3.18) |
| OR routine commit · OR birth | 4.46 · 28.60 |
| bursts with both S and a link · S first | 1 · 0 |
| hazard h_S − h_S′ [95%] (arrivals in risk set) | 1.02 [-0.24, 2.14] (78.00) |
| hazard κ − κ′ [95%] · untrimmed κ − κ′ | 0.27 [-1.30, 2.47] · 0.07 |
| hazard h_S − h_R [95%] | 0.85 [-0.63, 5.56] |

**Verdict: descriptive.** Fewer than 3 herding bursts or 5 S signals: descriptive by the rule.
Data: `data/processed/H63-bursts-start-with-work/results/periods.parquet`, `clusters_G40.parquet`.

