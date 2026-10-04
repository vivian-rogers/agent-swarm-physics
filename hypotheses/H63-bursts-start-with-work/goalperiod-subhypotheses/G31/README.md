# H63 × G31: Free week, farewell to Claude 3.7 Sonnet (2026-02-16 → 02-20)

**Verdict:** failed (native); failed (replication)
**Role:** native + replication (exploratory)
**Period:** regime I · #general · 11 → 12 → 11 agents · 5 days (units 31a–31d: a join, NE29, NE11). 1,391 agent work commits (13 agents), 17 new repos.

## Why this period
A free week with spontaneous condensation in dense git: about 9 agents converged on one UI task, and a time-capsule repo reached 11 agents (H27, H11). No goal field names the herded project. H27 round 1b found the work onsets of the wave coincide with its attention onsets (lag 0–1 window), and H28 found its links mark the burst (κ_lead > κ).

## Prediction
*Written 2026-10-04 19:35 UTC, before running on this period. Seen: H27/H28/H53 #31 results; commit count; no H63 statistic.*
- **N31a:** the largest herding burst of the week (by distinct agents) has an S signal (deploy event) or a birth on its project within 60 min before its follower onset. [0.45]
- **N31b:** in that burst, the first S signal or birth precedes the first chat link to the project. [0.5]
- **Counts against:** the follower onset precedes every deploy event and birth of the project (the wave starts before the artifact changes).
- Replication statistics (OR_S, h_S − h_S') follow the card's rule.

## Result
### Native test
- **N31a failed.** The week's largest trimmed burst (9 agents) has no deploy event or birth on its project in the 60 min before its follower onset. The project's first state change or birth comes 1.5 min *after* the follower onset. The largest untrimmed burst (11 agents) also has none within 60 min (its project was born the previous day).
- **N31b passes literally but not in substance.** The first state change precedes the first chat link (which comes 3.4 min after the follower onset), but both come after the wave has started.
- **Reading:** the time-capsule wave starts before any artifact state change and before any link. Commits and links follow the pile-on.
### Replication statistics
*Run 2026-10-04 ~20:45 UTC (trimmed window: all-present, ≥ 30 min after each agent's first call).*

| Statistic | Value |
| --- | --- |
| herding bursts (≥ 3 agents) · matched 1–2-agent clusters | 33 · 221 |
| bursts / controls with a state change (S) in the 60 min before the follower onset | 0/33 · 1/221 |
| OR_S [95%] (Haldane) · z vs S time-shift | 2.19 [0.09, 54.98] · -1.43 |
| bursts / controls with an agent chat link in the 60 min before | 8/33 · 14/221 (OR_L 4.73) |
| OR routine commit · OR birth | 2.48 · 3.06 |
| bursts with both S and a link · S first | 0 · 0 |
| hazard h_S − h_S′ [95%] (arrivals in risk set) | 0.41 [-0.65, 0.99] (518.00) |
| hazard κ − κ′ [95%] · untrimmed κ − κ′ | 0.04 [-0.10, 0.28] · -0.02 |
| hazard h_S − h_R [95%] | -0.06 [-1.48, 0.88] |

**Verdict: failed.** State changes precede few bursts; links precede most.
Data: `data/processed/H63-bursts-start-with-work/results/periods.parquet`, `clusters_G31.parquet`.

