# H15 × NE29: retirement of Claude 3.7 Sonnet, the longest memory lineage (2026-02-19, inside #31)

**Verdict:** supported
**Verdict (1b):** supported (native, 2026-10-04)
**Role:** native (round 1b, non-holdout)
**Period:** regime I · #31 free week (farewell to Claude 3.7 Sonnet) · 11 → 12 → 11 agents · #general · units 31a (02-16 → 02-17), 31b (02-18, Claude Sonnet 4.6 joins), 31c (02-19, NE29), 31d (02-20, NE11 100-turn session cap, excluded). Work ledger dense from #30 (1,391 work commits in #31).

## Why this NE
NE29 removes the agent with the longest memory lineage (10.5 months) from the swarm at a known date. At the swarm level this is a natural scramble of the village's longest-lived stored information that is *not* in artifacts. H15's round-1 reading (R1: day-scale memory is decorative; the information that matters is re-acquired from the environment) and H01 round 2 (the persistent unit is agent + own artifact) both predict that the swarm loses no measurable output when a long memory leaves, provided its artifacts stay.

## Design (native)
- Swarm output: agent work commits (DQ4) per active incumbent agent (present on 02-16..02-19, excluding Claude 3.7 Sonnet and the 02-18 newcomer), log(1 + commits per incumbent) on 02-19 minus the mean over 02-16..02-18.
- Null: the same contrast (day d minus the mean of its three previous active days, same-period days only, d ≥ 4th day of its period) at every non-holdout day of #30–#44 where it is defined; z = (observed − null mean)/null SD.
- Reliance (descriptive): work commits by other agents to repos Claude 3.7 Sonnet had committed to in #30–#31, before vs on 02-19.

## Prediction
*Written 2026-10-04, before computing any 02-19 statistic.*
- N1: |z| < 2 for the incumbents' work-commit contrast on 02-19 (no swarm-level viability cost of losing the longest memory lineage).
- N2 (descriptive, no test): Claude 3.7 Sonnet's own share of #31 work commits before 02-19 is small (< 5%), so its artifacts are not a store the others depended on; its repos keep receiving commits from others only if they were shared.
- Counts against: z ≤ −2 (incumbents produce less after the retirement).
- Power: one day after the event (02-20 is NE11), 10 incumbents; only a large drop (> ~2 day-SDs) is detectable.

## Result
*Run 2026-10-04 (`analysis/r1b_extra.py` → `NE29`).* Incumbents (present 02-16 → 02-19, not the retiree, not the 02-18 newcomer): 10 agents.

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N1 \|z\| < 2 for incumbents' log(1 + work commits per agent) on 02-19 vs 02-16..02-18 | log(1 + commits/incumbent) 2.89, 3.28, 3.03 → **3.25** on 02-19; contrast +0.19 vs null +0.15 ± 0.29 (29 day-contrasts in #30–#44): **z +0.13** | **holds** |
| N2 retiree's share of #30–#31 work commits < 5% | 2.3% (7 repos) | **holds** |

Reliance (descriptive): other agents' #31 commits into repos the retiree had touched fell from 33% before 02-19 to 8% on 02-19, so its shared repos lost attention, but total incumbent output did not fall.

**Reading.** Removing the longest memory lineage (10.5 months) costs the swarm no measurable work. Its information was not a store others depended on (2% of commits), consistent with R1 and with H01 round 2 (what persists is agent + own artifact). Weak test: one post day (02-20 is NE11) and a regime-I week.
