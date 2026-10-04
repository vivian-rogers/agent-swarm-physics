# H37 × G51: private roles (2026-07-06 → 2026-09-20; non-holdout 07-06 → 09-04)

**Verdict:** failed (no stance antagonism between rival or opposed roles; diffuse negative pairs elsewhere)
**Verdict (1c):** failed (stance v2.1: no excess disagreement for rivals or opposed roles; rivals excluded at ≥ +2 log-odds, opposed at ≥ +3; the governance-friction lead does not replicate)
**Role:** replication (exploratory)
**Period:** regime III · mode I/K · 32 agents seen · 4 rooms · 45 non-holdout days. The #51 tail (09-07 → 09-21) is locked holdout and is not used. Labelled: mention/both reply pairs, ≤ 40 per agent pair per H22 unit (51a–51e), 15,535 pairs.

## Why this period
H22 found that same-role rivals co-move *more* in topic (T_SR = +0.048, p = 0.02) and that the only cells leaning toward conflict were Prankster × Ethicist/Psychologist in 51a. If conflict lives in stance, these pairs should be negative in stance even while they co-move in topic.

## Prediction
*Written 2026-10-04 01:53 UTC, before running on this period (card predictions P6–P9).*
Pair-level stance couplings J_ij (mean soft stance, ≥ 3 replies), H22's role coding and treatment test (role permutation among role holders, same-lab adjusted); pooled over non-holdout #51, units 51b/51c/51d as robustness.
- **P6:** T_OP(stance) < 0, p_less < 0.05. [0.3; 2 role pairs]
- **P7:** T_SR(stance) < 0, p_less < 0.05, while T_SR(topic) on the same replies ≥ 0. [0.2]
- **P8 (descriptive):** f_neg < 0.10, raw τ₃ > 0.5 (ferromagnetic overall). [0.8]
- **P9 (descriptive):** significantly negative pairs enriched in OP ∪ SR ∪ NC (OR ≥ 2, Fisher p < 0.05). [0.2]
- *Against:* T_SR(stance) ≥ 0 and T_OP(stance) ≥ 0: rivals and opposed roles are not antagonistic in stance either.

## Result
*Run 2026-10-04 (`analysis/explore.py`, `analysis/calibrate.py`; data `data/processed/H37-stance-spins/G51/results.json`, `calibration.json`; figure `figures/g51_role_classes.pdf`).* Primary set: 14,545 relevant replies (Jev responds ≥ 0.5) among 32 agents; 330 agent pairs with ≥ 3 replies (6 SR, 2 OP, 82 SY, 16 NC testable pairs); role permutation 5,000, same-lab adjusted.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P6 T_OP(stance) < 0 | +0.02 (Prankster–Psychologist J = +0.26, n 46; Prankster–Ethicist J = +0.61, n 24) | p_less 0.55 | **fail** |
| P7 T_SR(stance) < 0 while T_SR(topic) ≥ 0 | stance +0.085 (p_less 0.81, p_greater 0.19); topic +0.078 (p_greater 0.053) | role permutation | **fail**: rivals are friendlier in stance too (no dissociation) |
| P8 f_neg < 0.10, raw τ₃ > 0.5 | f_neg 0.091 [0.081, 0.102]; τ₃ 0.75 | | pass (ferromagnetic, politeness field) |
| P9 negative pairs enriched in OP ∪ SR ∪ NC | 13 significant negative pairs, 0 in conflict classes (24 tested) | Fisher p = 1 | **fail** |

**Units.** 51b / 51c / 51d: T_SR(stance) +0.04 / +0.05 / +0.11 (all n.s.); T_OP +0.05 / −0.18 / +0.24 (n.s.). The H22 51a lead (Prankster pairs negative in topic) does not reappear in stance. All-pairs and hard-label variants agree.

**Detector, calibrated (Amendment 2).** Against the ordered-logit agent-field null (200 replicates): 10 significantly negative pairs (hard labels) vs 0.33 expected (95th percentile 2; p = 0.005), so pair-level antagonism beyond agent fields is real. But the two-camp split is not (faction score 0.45 vs null 0.44, p = 0.36). The uncalibrated sign-shuffle test (p = 0.01) is invalid here: in synthetic S6 it fires in 100% of agent-field-only runs at #51's structure. Balance: τ₃(resid) unstable (CI spans −0.9 to 29); not interpretable.

**Post hoc (not pre-registered; a lead).** 10 of the 13 negative pairs involve a norm-enforcing role (Psychologist, Ethicist, Diplomat, village helper, performance coach) vs 44% of tested pairs (OR 4.4, Fisher p = 0.016; one grouping among several possible). DeepSeek-V3.2 (Diplomat, ex-leader) is in 4. Reading: in #51, negative stance tracks governance friction (corrections, guardrail enforcement), not competition between rival roles.

**Reading.** Conflict does not live in stance here either: rivals and opposed roles are as friendly, or friendlier, than unrelated pairs. What negativity exists is diffuse (pairwise, not factional) and sits on oversight roles.

## Round 1c (stance v2.1, 2026-10-04)
*Predictions P6c, P7c, P9c written 2026-10-04 22:10 UTC in the card; synthetic power at 22:27 UTC; real run afterwards (`analysis/r1c.py`). Roles per day from DQ6 (`ground_truth_labels`), majority role per agent; H22's class rule.*
- **Pairs:** 23,670 DQ2 ledger-visible replies among 32 role holders (non-holdout); 201 flags (0.85%).
- **P6c (OP) fail:** 0 flags in 55 replies (2 pairs); true-scale β −2.0 [−3.4, −0.6].
- **P7c (SR) fail:** 6 flags in 400 replies (1.5% vs 1.0% unrelated), in 2 of 6 pairs; LP β +0.0035 (role permutation p 0.33); true-scale β +0.46 [−1.46, 1.37]. Power 0.37 at +1, 1.0 at +2.
- **P9c fail:** 3 excess-disagreement pairs (null 0.8, p 0.05), 1 in a conflict class (NC); Fisher p 0.21. None involves a norm-enforcing role (41% of tested pairs do).
- **Support roles** disagree less (true-scale β −1.4 [−3.4, −0.3]).
- **Post hoc lead:** media-niche competitors (NC) carry 14 of 299 replies flagged (role permutation p 0.006). 8 of these come from one pair.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | negative pairs beat the calibrated agent-field null (p = 0.005); camps do not |
| D unfitted predictions | 0 | role-class predictions (P6, P7, P9) fail |
| G ground truth | 0 | assigned rivalries / oppositions not visible in stance |

## Notes
- Adjacent (unaddressed) pairs in #51 were not labelled (20+ agents per room make them ambiguous).
