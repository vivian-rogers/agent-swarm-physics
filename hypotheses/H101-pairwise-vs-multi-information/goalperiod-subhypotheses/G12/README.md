# H101 × G12: debate teams as a known block structure (#12, 2025-09-01 → 09-05)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** goal #12 (debates) · regime I · 7 agents, one room · units 12a (4 days), 12b (1 day) · 10 debates of 15–45 min, each with assigned gov and opp teams (DQ6 `team` labels; the bench and judges are excluded).

## Why this period
The only period with assigned, changing teams. Inside a debate, team-mates share a case and opponents rebut each other. Teams are a known block structure, so this period tests whether co-usage reads the blocks as pairwise couplings (J within team ≠ J across) or needs a team-level higher-order term. H37 found that opposite-team debaters "oppose" in 33% of replies vs 6% within teams.

## Prediction
*Written 2026-10-04 20:39 UTC, before running on this period.*
- **G12-a (blocks are pairwise).** The ensemble is one debate (items = markers used inside the debate window; spins = its gov and opp members). In K-pairwise fits, mean J for same-team pairs exceeds mean J for opposite-team pairs (permutation p < 0.05, labels shuffled within debate). [0.5] *Against:* J_same ≤ J_opp (rebuttal quotes the opponent's terms as often as team-mates share them).
- **G12-b (no team-level higher order).** The T-weighted r_HO over debates is not above the replication median for regime-I units by more than 0.05, and fewer than half the debates have z ≥ 2.33. [0.5]
- Power caveat (Amendment A1): with T ≈ 30–150 items per debate and n = 4–6, a team-level term of the Y3 size would not be detected; G12-b can only be *descriptive*.

## Result
Data: `data/processed/H101-pairwise-vs-multi-information/natives/g12.json`. Ten debates, 777 items (39–122 per debate), 5–6 team members each.

- **G12-a supported: teams are pairwise blocks.** Mean K-pairwise J for same-team pairs is +0.15, for opposite-team pairs −0.60: difference +0.75, permutation p = 0.0005 (56 same, 84 opposite pairs; labels shuffled within debate). Opponents *avoid* each other's terms beyond the shared-field model; team-mates share them.
- **G12-b failed narrowly (descriptive power).** The T-weighted remainder over debates is r_HO = 0.087, against the regime-I replication median 0.030 (difference 0.057 > 0.05). No debate has z ≥ 2.33 (T is 39–122 items, below the power of the A1 test). ρ_F (T-weighted) is 0.86, raw I₂/I_N 0.82, φ 0.43.
- Replication units of #12 (day ensembles, conventions): 12a ρ_F = 0.909, r_HO 0.026 (z 3.9; field reference 0.148): pairs + fields; 12b ρ_F = 0.793, r_HO 0.100 (z 6.5; field reference 0.178): within the field reference.
- Reading: assigned teams appear as signed pairwise couplings (ferromagnetic within, antiferromagnetic across), as H37 found for stance. A team-level higher-order term is not resolved at debate-sized samples.

## Scorecard (period-specific axes)
G (ground truth: assigned teams), E (teams switch between debates).

## Notes
