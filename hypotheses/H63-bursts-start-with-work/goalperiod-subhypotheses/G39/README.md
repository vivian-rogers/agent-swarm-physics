# H63 × G39: Build your own interactive world (2026-04-27 → 05-01)

**Verdict:** failed (native); descriptive (replication)
**Role:** native + replication (exploratory)
**Period:** regime III · #best / #rest (reshuffled on day 1) · 15 agents · 5 days. 2,232 agent work commits (14 agents), 515 deploys; each agent builds and deploys its own world.

## Why this period
Each agent owns one world. It builds it, deploys it, and advertises it; others visit. H28 found links *lead* visits here (directed recruitment, κ − κ_lead +1.01), unlike shared weeks. If a work → link → visit chain exists anywhere, it is here, so this is the cleanest positive test.

## Prediction
*Written 2026-10-04 19:35 UTC, before running on this period. Seen: H28's #39 result (lag > lead for links); no H63 statistic.*
- **N39a:** for worlds (projects with an identifiable builder = the author of the birth commit) with ≥ 2 non-builder visitors, the builder's first deploy event precedes the first non-builder arrival in ≥ 70%. [0.55]
- **N39b:** the builder's first deploy event precedes the builder's first chat link to the world in ≥ 60%. [0.55]
- **N39c:** in the hazard model, h_S − h_S' > 0 (visits follow deploys, not the reverse). [0.5]
- **Counts against:** first visitors arrive before the first deploy in ≥ 50% of worlds (agents visit the repo before it is live).

## Result
### Native test
12 worlds (projects born in #39 by one builder, ≥ 2 non-builder visitors).
- **N39a failed:** the first deploy event precedes the first visitor in 3/12 worlds (25%; predicted ≥ 70%). The median first visit comes 4.9 min *before* the first deploy.
- **N39b failed:** the builder's first deploy precedes the builder's first chat link in 2/12 (17%; predicted ≥ 60%). Builders link first, then deploy.
- **N39c failed:** h_S − h_S′ = −0.28 [−0.65, 0.48].
- **Reading:** even in the own-world week, visitors arrive on the announcement or the repo, before the site is live. The order is link → visit → deploy, not deploy → link → visit.
### Replication statistics
*Run 2026-10-04 ~20:45 UTC (trimmed window: all-present, ≥ 30 min after each agent's first call).*

| Statistic | Value |
| --- | --- |
| herding bursts (≥ 3 agents) · matched 1–2-agent clusters | 2 · 86 |
| bursts / controls with a state change (S) in the 60 min before the follower onset | 0/2 · 4/86 |
| OR_S [95%] (Haldane) · z vs S time-shift | 3.67 [0.15, 88.28] · 0.51 |
| bursts / controls with an agent chat link in the 60 min before | 1/2 · 25/86 (OR_L 2.44) |
| OR routine commit · OR birth | 10.82 · 11.40 |
| bursts with both S and a link · S first | 1 · 0 |
| hazard h_S − h_S′ [95%] (arrivals in risk set) | -0.28 [-0.65, 0.48] (170.00) |
| hazard κ − κ′ [95%] · untrimmed κ − κ′ | -0.14 [-0.90, 4.42] · 0.03 |
| hazard h_S − h_R [95%] | -0.02 [-0.79, 0.28] |

**Verdict: descriptive.** Fewer than 3 herding bursts or 5 S signals: descriptive by the rule.
Data: `data/processed/H63-bursts-start-with-work/results/periods.parquet`, `clusters_G39.parquet`.

