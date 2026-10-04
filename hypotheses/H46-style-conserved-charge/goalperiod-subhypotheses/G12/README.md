# H46 × G12: Form two teams and debate each other, while one agent judges. Choose your teammates wisely! (2025-09-01 → 2025-09-05)

**Verdict:** failed
**Role:** native (exploratory)
**Period:** regime I · 7 agents with eligible days · rooms [0] · 5 days with eligible agent-days · units 12a, 12b.

## Why this period
#12 is the only period where the operator **assigned adversarial positions**: ten debates in four days, teams re-drafted for every debate (DQ6 `team` labels: gov/opp), a rotating judge (DQ6 `judge`), and a new motion every debate. That gives (i) ten rapid content quenches inside one period, (ii) an assigned register change inside one agent (Claude Opus 4.1 judged six debates and argued in four), and (iii) assigned sides. If style is a state that follows the assigned role or side, it moves here.

## Prediction
*Written 2026-10-04 05:45 UTC, before running on this period (from card P11).*
- **(a) Fingerprint across debates:** train on each agent's debates 1–5, test on 6–10. Style balanced accuracy ≥ 3× chance (7 agents: chance 0.14) and above content's.
- **(b) Debate switch:** displacement between an agent's consecutive debates vs its own within-debate split halves (placebo): content T_c > T_s, with T_s ≤ 0.60.
- **(c) Assigned role (judge vs debater), agent 9:** leave-one-debate-out classification of role from content ≥ 0.8; from style ≤ 0.7. The four one-time judges: style distance of the judge window to their debater centroid inside their own leave-one-out debater band (percentile < 0.9).
- **(d) Assigned side:** within-agent side permutation on style displacement, p ≥ 0.05.
- *Counts against H46:* (c) style separates judging from debating as well as content does, or (d) side moves style.

## Result
*Run 2026-10-04 06:09 UTC (`analysis/native.py` → `data/processed/H46-style-conserved-charge/G12/native.json`). 7 agents, 10 debates, 64 agent × debate sets with ≥ 3 messages.*

| Test | Style (type-controlled) | Style (raw) | Content | Prediction | Verdict |
| --- | --- | --- | --- | --- | --- |
| (a) fingerprint debates 1–5 → 6–10 (chance 0.14) | 0.67 | 0.66 | 0.72 | style ≥ 3× chance and > content | half (≥ 3× chance; not > content) |
| (b) debate switch vs within-debate halves, T | 0.442 | 0.454 | 0.415 | T_c > T_s, T_s ≤ 0.6 | uninformative (nothing moves) |
| (c) agent 9 judge vs debater, LOO accuracy (perm. p) | 0.80 (0.084) | 0.90 (0.029) | 0.60 (0.358) | content ≥ 0.8, style ≤ 0.7 | **failed** (reversed) |
| (c′) one-time judges: judge window vs own debater band (pct) | 1.00, 1.00, 0.89, 1.00 | 1.00, 1.00, 1.00, 1.00 | 0.56, 0.56, 0.67, 0.40 | style < 0.9 | **failed** (3/4 at 1.0) |
| (d) assigned side, permutation p | 0.797 | 0.962 | 0.515 | style p ≥ 0.05 | passed |

**Verdict:** failed. Assigned sides leave style alone, but an assigned *register* (judging) moves style and not content: judges write differently while talking about the same debate.

**Replication estimator in #12:** - **Sample:** 7 agents, 5 days, 35 eligible agent-days (≥ 3 deduplicated chat messages). - **Agent share of day-demeaned variance:** style 0.77, content 0.60. - **Split-half fingerprint within the period:** style 0.81, content 0.67, chance 0.14. - **Entry boundary 11->12** (adjacent, 7 agents): style T_s = 0.693 [0.473, 0.892] (raw 0.637); content T_c = 0.957 [0.928, 0.986]. - **Cross-boundary fingerprint:** style 0.76 vs content 0.57 at chance 0.14. - **Templated verdict:** mixed.

## Scorecard (period-specific axes)
- **G:** DQ6 team and judge labels as ground truth.
- **H:** R1 (style follows assigned register) beats H46 on the judge test.
