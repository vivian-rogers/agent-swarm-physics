# H48 × G51: private roles, newcomer assimilation across 11 joins (2026-07-06 → 09-04, head)

**Verdict:** failed
**Role:** native
**Period:** regime III · one room (#general) · 8 active h/day · N 21 at the kickoff → 32 · head only (the tail 09-07 → 09-21 is held out). Joins in the head: GPT-5.6 Sol, Terra, Luna (07-09, each first in an isolated onboarding room for ~1.5–2 h; see NE32), Grok 4.5 (07-10, onboarding room ~2.4 h), Kimi K3 (07-17), Claude Opus 5 (07-24), GLM-5.3 Flash (08-28), Claude Fable 5.1 (09-01), Muse Spark 1.3 and Gemini 3.8 Flash (09-03), GPT-6 Astra (09-04).

## Why this period
N is a within-period control parameter at fixed goal, room and hours. A newcomer arrives with an empty memory into a broadcast room: under H48 its content assimilates to the swarm as fast as it reads the incumbents (and they read it), so assimilation should take longer when there are more incumbents to read and when the newcomer's own coverage is slower. The field rival says newcomers settle onto their private role on their own clock (H54: each #51 agent lands on its own private goal within a day), independent of N and coverage.

## Prediction
*Written 2026-10-04 ~07:10 UTC, before running settling on this period.*
- **Observable:** for newcomer n, the assimilation gap g_n(t) = b(t) − s_n(t) in 2-active-hour bins from its join, where s_n = cos(v_n, unit(mean of incumbents' vectors)) and b = the incumbents' mean leave-one-out alignment; fit g_n(t) = g_∞ + (g_0 − g_∞)e^{−t/τ_a} over the first 16 active hours (2 days). Coverage: T90_in (time until n has read ≥ 1 message from 90% of incumbents) and T90_out (until 90% of incumbents have read n).
- **N3a (primary):** Spearman(τ_a, T90_in) > 0 over newcomers with a detected decay (one-sided permutation p < 0.10; n ≤ 11).
- **N3b:** Spearman(τ_a, N at join) > 0.
- **N3c:** g_0 > g_∞ (newcomers start further from the swarm than incumbents) in ≥ 70% of newcomers.
- **Field rival:** τ_a unrelated to T90_in and N.
- **Credence:** N3a 0.25, N3b 0.3, N3c 0.6. Power is low (≤ 11 newcomers; the last three have only 1–2 days).

## Result
11 newcomers in the head (the last three with only 1–2 active days). Gap g_n(t) in 2-active-hour bins over the first 16 active hours from the join (from the merge for the four onboarding-room arms).

| Native prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| N3c (premise): g_0 > g_∞ (newcomers start further from the swarm and close in) in ≥ 70% | 3/11 (27%) in both models (7/11 rise, 1 too short); a decaying fit is detected for 1/11 (bge) and 0/11 (gte). Newcomers start *closer* to the incumbents' centroid than incumbents are to each other (median gap −0.16 over the first 7 active h, both models) and the gap rises to ≈ 0 by 9–13 h | – | **failed** |
| N3a (primary): Spearman(τ_a, T90_in) > 0 | not testable (≤ 1 detected decay) | permutation | n/a |
| N3b: Spearman(τ_a, N at join) > 0 | not testable | permutation | n/a |

Read-out coverage itself is fast and grows with N, as expected: the newcomer has read 90% of the incumbents within 3.0–6.2 active h of joining (T90_in; ∞ for the 09-03/04 joiners with < 2 days), and 90% of the incumbents have read the newcomer within 0.16–2.6 h (T90_out).

**Reading.** In #51 there is nothing for read-out to drive: newcomers do not assimilate toward the swarm. They start generic (closer to the shared centroid than the incumbents) and individuate within about a day, consistent with H54's finding that each #51 agent lands on its own private goal. The N sweep therefore cannot test H48's settling clock. Figure: [`figures/newcomer_gaps.pdf`](figures/newcomer_gaps.pdf). Data: `data/processed/H48-settling-mixing-time/G51/` (`newcomers.parquet`, `newcomer_series.parquet`, `natives.json`).

## Scorecard (period-specific axes)
- **D:** failed (the assimilation premise). **G:** agrees with H54 (private-goal pinning) and with the ledger (newcomers read 0 agent messages in isolation; see NE32).

## Notes
- N rises in steps of 1–3; N at join is confounded with calendar time (drive withdrawal NE43 at 08-05 / 08-21, role reassignment NE38).
