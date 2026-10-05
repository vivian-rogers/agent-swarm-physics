# H34: Idea cascades follow a power law whose exponent reads off the distance to criticality

**Status:** running. **Exploratory round 1 done (2026-10-04).**
- **Subcritical and real:** idea cascades are strongly subcritical in all 32 non-holdout periods (R̂ 0.06–0.39). Adoption is time-locked to visible exposure beyond a common field in 27/32 (HR₁₀ lower CI > 1).
- **No s^−3/2:** the pure critical law is rejected 32/32. The apparent exponent τ_app (2.4–4.3) is a near-deterministic readout of R̂ (ρ = −0.95), so it adds nothing.
- **Heavier tails than one branching law:** this is idea-level heterogeneity.
- **The pre-registered criticality link failed:** R̂ vs H03's activity n̂ gives ρ = 0.06.
- **The pre-registered forecast was overconfident:** 36–46% coverage at 90% nominal. A post-hoc rule (R̂ from the last two days + day drift) reaches 70–84% and is frozen for confirmation.
- **Post hoc:** R̂ tracks H25's *content* dial (partial ρ 0.41 given N; daily ρ 0.28), not its activity dial.
- Scorecard A1 B1 C1 D1 E0 F1 G1 H1 I1. `analysis/confirm.py` frozen and dry-run, not run. Not promoted.
- **Round 1b (2026-10-04, context-ledger visibility):** contagion beyond the field now holds in **32/32** periods (round 1: 27/32); regime I was mismeasured by the call-start rule (median HR₁₀ 2.3 → 6.4). **But about half of the exposure-locked hazard is contemporaneous convergence:** uses not yet read predict adoption too (HR_unread5/HR_seen5 median 0.56; read > unread in 30/32). Natives: designated lead designers seed no more spreadable ideas (#35, ratio 1.11 [0.82, 1.45]); the elected leader's ideas spread *less* (#26, 0.36 [0.27, 0.46]). Verdicts 9 supported / 23 mixed / 0 failed. Scorecard unchanged.

Predictions were written 2026-10-04 01:30 UTC, before any real-data run.

**Fields:** stat mech, sociophysics, info theory
**Origin:** HH122 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`); tests HH108 at the idea level.
**Definitions used:** Population N(t); Regime; Interaction (broadcast; the shared `exposure` room rule) with the named variant *Interaction (visible exposure)* below; Contagion / adoption event, with the marker set fixed by the *Idea (H34 marker rule)* below. **New here, proposed for `physics-models/DEFINITIONS.md`** (not edited; outside H34's scope): *Idea (H34 marker rule)*, *Interaction (visible exposure)*, *Adoption cascade (exposure tree)*, *Branching ratio (content, adopter-level)*.

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. Every entry rests on this card and its round-1b section.*

**Question served:** Q3. Idea cascades are subcritical in 32/32 periods, so there is no near-critical collective order. Q1 second: HR₁₀ measures coupling through reading.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | HR₁₀ is a hazard per at-risk talk turn, stratified by idea. The jitter null (N0) keeps each agent's turn rate. | removed |
| Exogenous field (kickoff/goal/operator) | yes | Human and automated parents make roots; roster names are excluded from markers. N0 failed its synthetic guard (A2). S2 simulated only a constant field; a bursty field also gives HR₁₀ > 1 (Caveats). R̂ is 1.5× higher on kickoff days. Close with a kickoff-matched placebo and goal-text marker exclusion (§1, row 2). | partly |
| Shared model priors | partly | Not handled. Shared pretraining can coin the same marker without exposure (field ε, Model). Close with a cross-family HR₁₀ and a first-day control (§1, row 3). | open |
| Contemporaneous convergence | yes | Round 1b H57 placebo: read uses beat unread ones in 30/32; unread uses carry about half the hazard ratio. HR₁₀ and R_c are not net of the unread term. | partly |

**Inputs:** round 1b uses the context ledger for every exposure quantity. Embeddings, activity bins, work and failures are not inputs (ideas are hashed text markers). P4 still reads H03's and H19's round-1 activity-gain tables as comparators.

**Two layers:** no folder has role `replication`. The common estimator runs on 32 period folders under role `exploratory`. Native tests: 2 (`G35` lead designers as seeders, mixed; `G26` elected leader as seeder, failed).

**Confirm script:** `analysis/confirm.py` exists, dry-run only, built on H18's call-start visibility. **Re-freeze on ledger visibility before any holdout run** (holdout.md items 8 and 15). Add the unread placebo as a clause at re-freeze.

## Question
Track adoption cascades of new terms or ideas after exposure. Cascade sizes P(s) ~ s^−τ, with cutoff and exponent set by the branching ratio, tie to HH107's dial and predict how far misinformation spreads. *Check:* cascade trees from exposure plus first use; fitted branching vs HH107.

Practical aim (usefulness-first batch): produce a number or rule an operator of an LLM agent swarm could compute from logs and act on. Here that is a **spread-forecast rule**: from a period's measured branching ratio R̂, predict how many agents a new idea (or claim) will reach, with uncertainty.

## Model
**From:** `physics-models/03-contagion` (SIR on the room, with a field ε) and `physics-models/09-hawkes` (cluster/branching picture). H34 variant:

- **Galton–Watson (GW) cascade with a field, on a finite room.** An idea enters through a *root*: an agent invents it, an agent adopts it from a human, or an agent produces it with no visible exposure (field ε: shared pretraining, the goal, a web page, a common source). Every adopter has a random number of offspring, i.e. agents whose first use follows visible exposure to *its* use. Offspring are i.i.d. negative binomial with mean R (branching ratio) and dispersion k. Tree size s ≤ N (room or roster size).
- **Size distribution** (Lloyd-Smith et al. 2005; Borel when k → ∞):
  P(s | R, k) = Γ(ks+s−1) / (Γ(ks) Γ(s+1)) · (R/k)^{s−1} / (1+R/k)^{ks+s−1}, truncated and renormalized at s ≤ N.
  For R < 1 the tail is s^{−3/2} e^{−s/s_c} with 1/s_c = R − 1 − ln R (Borel): **the exponent is universal (3/2); the distance to criticality sits in the cutoff s_c ≈ 2/(1−R)².** A pure power law fitted over the short range 1 ≤ s ≤ N without a cutoff gives an *apparent* exponent τ_app that steepens as R falls. This is the precise reading of "the exponent reads off the distance to criticality"; H03's apparent activity-burst exponents 2.1–4.2 are of this kind.
- **Idea reach** (distinct agents using an idea) = the sum of the idea's trees: 1 + M roots, M ~ Poisson(μ_field), each root carrying a GW tree (Borel–Tanner when k → ∞), capped at N.
- **Simple vs complex contagion.** Per at-risk talk turn, adoption hazard h(k_src) where k_src is the number of distinct visible sources. Simple: h = 1 − (1 − p)^{k_src} (hazard ratio HR(2 vs 1) ≈ 2 for small p). Complex: h(1) ≈ 0 with a jump at 2 (HR ≫ 2). Pure field: HR ≈ 1.

## Operational definitions (pre-registered 2026-10-04 01:30 UTC)

**Idea (H34 marker rule).** Markers are extracted from `chat_text.text` of every non-holdout chat message (any speaker kind). Held-out text is never read. Each marker is counted once per message and stored only as a 64-bit hash of `class:normalized form`; text never leaves memory.
- **U, artifact:** artifacts of kind repo, site or file in `artifact_mentions` (source chat, how ∈ {url, bare}) for that message. Domains are excluded as too generic.
- **D, number (claim proxy):** numeric tokens with ≥ 3 significant digits after removing URLs, dates (YYYY-MM-DD, d/m[/y]), times (hh:mm) and versions (x.y.z). Bare 4-digit integers 1900–2099 (years) are excluded. Normalization: drop thousands separators and trailing decimal zeros; keep a currency or % unit tag.
- **N, name or coinage:** (i) runs of 2–5 consecutive capitalized tokens within one sentence, after dropping leading function words (fixed list in `scheme/markers.py`); (ii) CamelCase, snake_case or kebab-case identifiers of length ≥ 6; (iii) hashtags of length ≥ 3. Normalized to lower case.
- **W, rare word:** lower-cased alphabetic tokens of length ≥ 6 that are not in `/usr/share/dict/words` (sha1 6d17bc9e…), also after stripping the suffixes -s, -es, -ed, -ing, -ly.
- **Exclusions:** markers containing a roster-name token (agent names, model-family and lab words: the "who is present" field), and URL fragments.
- **Novelty:** a marker is an *idea of period g* if its first use in the non-holdout chat corpus falls inside g. Periods with fewer than 10,000 earlier non-holdout chat messages are excluded because their novelty baseline is too thin (this drops #2–#4). Analyzed: non-holdout #5–#51 (32 periods; #51 without its held-out tail).
- Embedding-cluster novelty: not in round 1.

**Interaction (visible exposure).** Agent j's use u at time t_u has call start s_u = j's latest logged turn before t_u − 1 s. Turns are `actions` rows minus `pause` mirrors plus agent `events_core` events; this is H18's rule, imported from `../H18-attention-dilution/scheme/build.py`. A message m is a *visible exposure* of j at u if three conditions hold: m contains the idea, its sender is not j, and m has an `exposure` row for recipient j with t_m < s_u. If j has no earlier turn that day, s_u = t_u − 1 s (flagged).

**Adoption cascade (exposure tree).** For each idea, each speaker's first use is classified as follows:
- **seed:** the idea's first use in the period;
- **exposed:** at least one visible exposure;
- **unexposed:** earlier uses exist but none was visible to j.

An exposed agent's parent is the sender of the most recent visible exposing message (the earliest one is the alternative rule). Trees contain agent nodes only (Claude Code agents excluded). A node is a root if it is a seed, unexposed, or its parent is a human or the `automated` speaker. Tree size s = number of agent nodes. Also recorded per first use:
- k_src, the number of distinct visible sources;
- n_exp, the number of visible exposing messages;
- the lag in j's own talk turns from the first visible exposure to adoption.

Trees rooted on a period's last active day are flagged as right-censored.

**Branching ratio (content, adopter-level).** R̂ = (agent nodes with an agent parent) / (agent nodes), per period and idea class. This is the GW mean offspring. Over a complete forest the mean tree size equals 1/(1 − R̂) identically, so the mean is not a test; the *shape* is. k̂ is the negative-binomial maximum-likelihood dispersion of the per-node offspring counts.

## Data scheme (`scheme/`)
Shared tables in `data/processed/shared/` (see `infra/README.md`, including Known issues): `chat_core`, `chat_text` (in memory only), `exposure`, `artifact_mentions`/`artifacts`, `events_core`, `actions`, `roster`, `rooms_timeline`, `calendar`. Text is used in memory only and never written.
- `scheme/markers.py`: the marker rule. `scheme/build_markers.py` → `markers/uses.parquet` (message row, marker hash, class; non-holdout only), `markers/first_seen.parquet`.
- `scheme/build.py` → per period `G<NN>/`:
  - `first_uses.parquet`: idea, agent, status, parent, k_src, lag, tree;
  - `trees.parquet`: idea, tree, root type, size, censored;
  - `atrisk.parquet`: per idea × k_src: at-risk talk turns and adoptions, for the dose response;
  - `jitter.parquet`: per adopter, the exposed probability under the jitter null;
  - `rooms.parquet`: the exposed vs never-exposed adoption contrast.
- **Output:** `data/processed/H34-idea-cascades/` (one subfolder per goal period, plus `markers/`, `synthetic/`, `results/`), with `_provenance.json`. Budget ≤ 200 MB.

## Candidate goal periods
Primary (card): **#20** (regime I, one room, Substack niches), **#42** (regime III, two rooms #best/#rest, YouTube channels), **#51** (regime III, 21–29 agents, private roles; non-holdout part). Secondary, for the cross-period criticality link (step 4): every non-holdout period from #5 on (32 in total). Per-period folders go in `goalperiod-subhypotheses/G<NN>/`.

## Observables
*Written 2026-10-04 01:30 UTC.*
- **O1.** Per period and class: number of ideas, agent nodes, R̂ with an idea-cluster bootstrap 95% CI, k̂, the root mix (invented / human / field), and the excess branching R̂ − R̂_jitter (see N0).
- **O2.** The tree-size distribution P(s) and the idea-reach distribution; P(s ≥ 2), P(s ≥ 3), P(s ≥ 5), s_max.
- **O3.** Fits on 1 ≤ s ≤ N_max:
  - discrete power law with exponential cutoff (τ, s_c);
  - pure power law (τ_app), with the likelihood ratio between the two;
  - the unfitted GW-NB(R̂, k̂) prediction of P(s ≥ 3) and P(s ≥ 5), with a parametric-bootstrap 90% band;
  - R estimated from the sizes alone (GW-NB size likelihood), compared with R̂ from the offspring counts;
  - root vs non-root offspring means (the i.i.d.-offspring assumption).
- **O4. Exposure ordering:** the fraction of non-seed agent first uses that are exposed, against the jitter null (N0); the fraction adopting at their first talk turn after first exposure, also against the null.
- **O5. Dose response:** adoption hazard per at-risk talk turn vs k_src. Hazard ratios HR(2 vs 1) and HR(3+ vs 2) are Mantel–Haenszel-pooled with idea strata, with an idea-bootstrap CI.
- **O6. Cross-room field** (periods with ≥ 2 active rooms): P(adopt | ever visibly exposed) vs P(adopt | never exposed), among agents who post in the idea's first day; their odds ratio; ε̂.
- **O7. Criticality link** across analyzed periods: Spearman ρ of (R̂, P(s ≥ 3)) with H03 n̂_talk (`period_table`, TALK, B2) and H19 g_eq,talk (`estimates`). H25's per-day loop gains are added if they appear in `data/processed/H25-criticality-dial/` before the round ends.
- **O8. Forecast skill:** day-ahead forecasts of each day's tree-size distribution from R̂ and k̂ of earlier days in the same period. Measures: 90% PI coverage of P(s ≥ 2) and P(s ≥ 3) on days with ≥ 20 trees, and log score against the rivals (N1–N3).

## Null / baseline
*Written 2026-10-04 01:30 UTC, before any real-data run.*
- **N0, field / independent invention (strongest, local):** adoption times are unrelated to exposure at the turn scale. Each non-seed adopter's first-use turn is redrawn uniformly among its own talk turns within ±1 h (active time) of the observed one, after the idea's first use; ±30 min and ±2 h are secondary. This keeps topical bursts, agent rates and the room structure, and removes only the turn-level ordering of exposure → adoption. It yields R̂_jitter (the field floor), the null exposed fraction and the null lag.
- **N1, heterogeneous salience (no transmission):** each other agent adopts independently with an idea-specific probability, beta-binomial reach. Fitted per period as a forecast rival.
- **N2, homogeneous field:** binomial reach, 1 + Bin(N − 1, ε̂). Forecast rival.
- **N3, activity loop gain plug-in:** GW-Poisson with R = H03 n̂_talk. Forecast rival; also tests whether activity criticality reads out idea spread (HH107/HH122 link).
- **N4, empirical:** the earlier days' empirical size distribution (add-one smoothed). The naive forecast to beat.
- **Signature null:** critical branching (R = 1, s^{−3/2} up to N), against the subcritical cutoff.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** independent invention / field (N0, N2), heterogeneous salience (N1), activity-gain plug-in (N3), critical branching (signature null); complex contagion (vs simple).
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (C1–C6) targets the #51 tail (T1, primary), #15, #28 and #22. It is written and dry-run on non-holdout stand-ins (#51 08-24 → 09-05, #13, #25, #16), not run. It refuses without `--confirm --i-understand-this-uses-the-locked-holdout`. Reuse disclosure is under "Confirmatory predictions".

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Ideas (hashed markers), visible exposure (H18 call-start rule on `exposure`), trees and R̂ all come from shared tables; assumptions are listed under Operational definitions. **Not invariant:** HR₁₀'s size depends on the scaffold (median 2.3 in regime I, 14 in II, 39 in III); the marker mix shifts across eras (N ideas are dominated by code identifiers in regime III); room structure changes what "exposed" means. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | **Violated:** i.i.d. offspring (roots 0.18 vs non-roots 0.30 median offspring) and stationarity: R̂ is higher on kickoff days (0.30 vs 0.19) and drifts down within periods (median ρ −0.38), with day-to-day spread of logit P(s ≥ 2) 0.46 vs 0.13 from sampling. **Checked:** censoring (R̂ without last-day trees moves ≤ 0.035) and the call-start fallback (0.1–1.7% of talk turns). **Assumed:** the recency window W = 3 call windows. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | **Field null (N0, A2):** HR₁₀ lower CI > 1 in 27/32 periods; the test had 0/36 false positives and 18/18 power in S2. **Day-ahead held-out days:** the pre-registered FN-GW beats the homogeneous field (31/32) and the H03 plug-in (29/32) but loses to the beta-binomial (9/32) and the empirical (12/32) rivals. The post-hoc GW-NB V3 beats the empirical rival in 20/32 periods and ties the beta-binomial (16/32, +313 nats in total). |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | **Unfitted shape:** FN-GW covers P(s ≥ 3) in 27/32, but P(s ≥ 5) is heavier than its band in 25/32. **Signature:** pure s^−3/2 rejected 32/32. τ_app (2.4–4.3) matches S1's τ_app(R) calibration within ±0.27, though this is nearly mechanical. The mean tree size is an identity, not a test. |
| E interventional | predicts the change across a natural experiment | 0 | Not attempted. Natural experiments that would test it: the NE15 room split, the 05-04 merge, and roster joins in #51. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | **S1:** FN-GW recovers Reed–Frost R0 within 0.01; τ with a cutoff is not identifiable at N ≤ 25. **S2:** the full pipeline on real #20, #42 and #51 timelines. R_c recovers the true contagion R (bias +0.02 to +0.07, up to +0.15 with a strong field). R̂ alone is inflated by up to +0.5 under a pure field. The jitter test fails its guard (17% false positives). The shape test is not specific. **Not checked:** alternative marker rules and embedding novelty. |
| G ground truth | agrees with known structure | 1 | In two-room periods (#35–#44), never-exposed agents adopt an idea 13–970× less often than exposed ones within 24 h, consistent with rooms gating spread. But room-specific fields confound this (rooms often worked on different projects). There is no labeled transmission ground truth. |
| H comparative | beats the named rivals | 1 | **Beats:** the homogeneous field (31/32) and the activity-gain plug-in N3 (29–31/32). **Does not clearly beat:** heterogeneous salience N1 (pre-registered model 9/32; post hoc 16/32). **Simple vs complex contagion:** unresolved, because the bias bracket [0.5, 4.2] straddles both. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Subcritical R̂ holds in 32/32 periods across all modes and regimes; HR₁₀ > 1 holds in 27/32 (all 11 regime II/III periods, 16/21 regime I). Magnitudes are regime-dependent. Holdout not run. |

## Prediction
*Written 2026-10-04 01:30 UTC, before running the analysis on real data. Seen beforehand: schemas, per-period message counts by speaker kind, H03's per-period n̂ table and H19's estimate table (column names and a few rows). No marker, idea, exposure-to-adoption or cascade statistic had been computed.*

"Periods" means analyzed periods with ≥ 20 non-seed agent first uses (all classes pooled); the primary statistic pools all classes.

| # | Prediction | Counts against |
| --- | --- | --- |
| P1 | **Subcritical everywhere.** R̂ < 1 with the upper 95% CI < 1 in every period, and in ≥ 90% of period × class cells with ≥ 30 agent nodes. Typical R̂ is 0.05–0.5. Class ordering U > N > D (artifacts spread most, numbers least) in most periods | any period with lower CI ≥ 1 (content near-critical: HH108 holds at the idea level) |
| P2 | **HH108 at the idea level: not supported.** Pooled R̂ < H03 n̂_talk in ≥ 60% of periods, and the excess branching R̂ − R̂_jitter is smaller still | R̂ > n̂_talk in most periods, by margins outside the bootstrap CI |
| P3 | **Signature: subcritical branching, not s^{−3/2}.** (a) The unfitted GW-NB(R̂, k̂) puts observed P(s ≥ 3) and P(s ≥ 5) inside its 90% band in ≥ 2/3 of periods with ≥ 50 trees. (b) The power-law-with-cutoff fit has a finite s_c; pure s^{−3/2} without a cutoff is rejected (LR p < 0.05) in #20 and #51; τ_app ≥ 2. (c) τ with a cutoff is *not* identifiable at village N (synthetic check S1 decides; if it is identifiable, its CI includes 1.5) | (a) the GW-NB band misses in > 1/3 of periods (shape not branching); (b) s^{−3/2} not rejected in the large periods while R̂ < 1 |
| P4 | **Criticality link.** Across periods, Spearman ρ(R̂, H03 n̂_talk) > 0 at one-sided p < 0.05. Holm correction over 4 tests: {R̂, P(s ≥ 3)} × {H03 n̂_talk, H19 g_eq,talk} | ρ ≤ 0: activity loop gains do not read out idea spread |
| P5 | **Contagion beats independent invention.** (a) The exposed fraction of non-seed first uses exceeds the N0 jitter null (p < 0.05) in ≥ 2/3 of periods. (b) More adopters adopt at their first talk turn after exposure than the null predicts. (c) In multi-room periods, exposed agents adopt more than never-exposed agents (pooled OR > 3), and ε̂ > 0: independent invention exists | (a) fails in > 1/3 of periods → "cascades" are a common field; R̂ is then a field floor, not a branching ratio |
| P6 | **Simple, not complex, contagion.** Pooled HR(2 vs 1 source) in [1, 2.5] in most periods; no class shows HR(2 vs 1) > 3 with the CI excluding 2.5 | HR(2 vs 1) > 3 (CI) in most periods → complex contagion (threshold) |
| P7 | **Forecast rule works and beats activity.** Day-ahead GW-NB forecasts cover the observed P(s ≥ 2) and P(s ≥ 3) inside 90% PIs on ≥ 80% of eligible days. Held-out log score: GW-NB beats N2 (homogeneous field) in ≥ 2/3 of periods and beats N3 (H03 plug-in) in ≥ 2/3 of periods | coverage < 70%, or N3 ≥ GW-NB in most periods |

Prior credences (Claude, 2026-10-04): P1 0.75, P2 0.6, P3 0.45, P4 0.25, P5 0.55, P6 0.6, P7 0.4.

**Per-period verdict rule** (also written in each G card before its run):
- **supported:** P5a passes (contagion beats the jitter null at p < 0.05) *and* P3a passes (the GW-NB band covers P(s ≥ 3) and P(s ≥ 5)). R̂ is then a valid readout of the distance to criticality in that period.
- **failed:** both fail, or R̂'s lower CI ≥ 1.
- **mixed:** exactly one passes.
- **n/a:** fewer than 20 non-seed agent first uses.

**Synthetic validation (axis F), planned before real data.**
- **S1, finite-N GW:** Reed–Frost SIR on a complete graph and GW-NB, at N ∈ {8, 15, 25}, R ∈ {0.1, 0.3, 0.5, 0.7, 0.9, 1.0}, and the actual tree counts. Checks recovery of R from offspring counts and from sizes alone, and identifiability of τ and s_c; calibrates τ_app(R).
- **S2, contagion on village exposure graphs:** the real message times, senders, rooms, `exposure` rows and turn times of #20, #42 and a #51 segment, with synthetic markers seeded at real messages. Adoption per talk turn follows 1 − (1−q)^{k_src} (simple) or a threshold (complex), plus field ε per turn; adopters re-use the marker. Grid: q ∈ {0, 0.03, 0.1, 0.25}, ε ∈ {0, 0.003, 0.01}. The full pipeline must:
  - recover the true contagion share and R within ±0.1, or report the bias;
  - keep the P5a test's false-positive rate ≤ 10% at q = 0, and give its power at the real sample sizes;
  - separate simple from complex (HR(2 vs 1)).

  If the guard fails for a statistic, that statistic is reported as uninterpretable.

## Synthetic validation (axis F; run 2026-10-04 before any real-data cascade statistic)
Code: `analysis/synthetic.py`. Outputs: `data/processed/H34-idea-cascades/synthetic/s1.parquet`, `s2.parquet`. The real marker table had been built (counts only) but no idea, exposure-to-adoption or tree statistic had been computed.

**S1, finite-N branching** (Reed–Frost chain binomial and GW-NB capped at N; N ∈ {8, 15, 25}; R ∈ {0.1 … 1.0}; 300 and 3,000 trees; 12 replicates each; 864 runs).
- **R from offspring counts is the *realized* branching ratio.** It is depleted near criticality: Reed–Frost R = 0.7 / 0.9 / 1.0 at N = 15 gives R̂ = 0.60 / 0.71 / 0.75. Calibrating a finite-N GW with depletion (FN-GW; each node's offspring are NB with mean R0·S/(N−1), where S is the number of susceptibles left) to the observed mean tree size recovers the nominal R0: 0.70 / 0.90 / 1.00.
- **R from sizes alone** has a supercritical dual (R e^{−R} is invariant). It is restricted to R < 1 and recovers R ≤ 0.5.
- **Tail shape:**
  - The renormalized GW-NB band covers P(s ≥ 3) only for R ≲ 0.3–0.5 (coverage 0–0.3 at R ≥ 0.7).
  - The FN-GW band covers Reed–Frost data in 58–100% of runs for R ≤ 0.7, and in 25–100% near R = 1. It fails for hard-capped GW-NB at R ≥ 0.5 with 3,000 trees, which is a different finite-size mechanism.
- **Exponents:**
  - τ fitted *with* a cutoff on 1 ≤ s ≤ N is biased and model-dependent: 0.5–1.3 for Reed–Frost, 1.4–2.9 for GW-NB. It is not the universal 3/2, so it does not read out criticality at village N.
  - The apparent exponent τ_app (pure power law on 1 ≤ s ≤ N) is a monotone calibration curve of R: 3.9 / 2.6 / 2.1 / 1.7 / 1.5 at R = 0.1 / 0.3 / 0.5 / 0.7 / 0.9 for GW-NB, and ≈ 0.4 lower for Reed–Frost near R = 1.
  - Pure s^{−3/2} is rejected at p < 0.05 in 100% of runs with R ≤ 0.7.

**S2, contagion on village exposure graphs** (#20, #42 and #51 07-27 → 08-07; real messages, rooms, `exposure` rows and turns; 600–900 synthetic ideas per run; simple contagion with a 3-call-window memory, q ∈ {0, 0.005, 0.015, 0.04}; field ε ∈ {0.0005, 0.002} per talk turn for 24 h; plus complex and no-field runs; 6 replicates at q = 0, 3 at q = 0.005; 72 runs).
- **The field masquerades as branching.**
  - With no contagion at all (q = 0), R̂ = 0.15–0.42 in #20, 0.05–0.18 in #42 and 0.22–0.52 in #51.
  - 98% (#20), 58–75% (#42) and 86–93% (#51) of field adoptions are classified as "exposed", because exposure in a shared room is saturated.
  - The GW-NB shape test also passes on pure-field data.
  - **R̂ alone measures how far an idea gets, not contagion.**
- **The pre-registered jitter test (P5a) fails the guard.**
  - False-positive rate at q = 0 is 6/36 (17%), above the 10% limit.
  - Its excess is ≤ 0.012 even with contagion. Power is 27% (#42), 45% (#51) and 82% (#20).
  - Its result is reported but treated as uninterpretable.
- **HR₁₀** passes the guard. It is the adoption hazard at talk turns with ≥ 1 visible source in the agent's last 3 call windows vs turns with none, stratified by idea, estimated by conditional likelihood with a profile 95% CI.
  - Lower CI > 1 in 0/36 null runs and in 18/18 runs at q = 0.005.
  - **The contagion share R_c = R̂ (1 − 1/HR₁₀)** recovers R_true, with a mean bias of +0.02 (#42), +0.07 (#51) and +0.07 (#20). It is worst, up to +0.15, when the field is strong (ε = 0.002, #20). For comparison, R̂'s mean bias is +0.06 to +0.15 with contagion and +0.12 to +0.37 without. R_c = 0 in 30/36 null runs and ≤ 0.053 in all 36.
  - Cumulative k fails here: k = 0 turns are too rare in one room (2 adoptions in a #20 run).
- **Simple vs complex.**
  - Mantel–Haenszel stratified by idea is biased: a second source exists only after an adoption at k = 1 (outcome-dependent exposure). It gives HR(2 vs 1) ≈ 0.3–0.7 for true simple contagion.
  - The *pooled* recency-k HR(2 vs 1) recovers simple contagion (1.25–2.41; lower CI ≤ 1.88 in all 33 simple runs) and flags complex contagion (18.6 and 22.0, lower CI > 12).
- **Cross-room contrast (P5c)**, P(adopt | exposed) / P(adopt | never exposed) within 24 h:
  - 1.2–1.8 under a pure field in #42, slightly above 1 because the never-exposed agents are less active;
  - ≥ 9 with contagion.
- **Tail shape on village graphs.** The FN-GW band covers P(s ≥ 3) in 36% (#20 and #51) to 82% (#42) of contagion runs, and the renormalized GW-NB band in 0–64%. The S2 process (memory windows, re-use, uneven agent activity, a time-limited field) is not an i.i.d. GW, and with about 1,000 trees the band is narrow. So **a P3a miss on real data counts against the GW idealization, not against contagion.** Both bands also cover pure-field data about half the time, so the shape does not separate field from contagion.

## Amendments (2026-10-04 01:57 UTC, after the synthetic validation, before any real-data cascade statistic)
- **A1 (shape; from S1).** The primary tail predictor for P3a and the forecast rule becomes FN-GW, calibrated to the observed mean tree size, with NB dispersion k̂ and N = the period's median room size (recipients + sender of agent messages). The renormalized GW-NB is reported as secondary. P3(b)'s "τ_app ≥ 2" is read through S1's calibration curve (τ_app ≥ 2 ⇔ R ≲ 0.5). P3(c) is resolved by S1: τ with a cutoff is not identifiable as 3/2 at village N, so it is dropped as a criticality readout.
- **A2 (contagion vs field; from S2).** P5a (jitter) is kept as pre-registered but is uninterpretable (it failed the guard). The **contagion criterion becomes HR₁₀ > 1 with lower 95% CI > 1** (recency k, idea-stratified conditional likelihood). The per-period verdict rule changes accordingly:
  - **supported** = HR₁₀ lower CI > 1 *and* the FN-GW band covers P(s ≥ 3) and P(s ≥ 5);
  - **failed** = neither, or R̂ lower CI ≥ 1;
  - **mixed** = one of the two;
  - **n/a** = < 20 non-seed agent first uses.
- **A3 (simple vs complex; from S2).** P6 uses the pooled recency-k HR(2 vs 1) with an idea-bootstrap CI. Idea heterogeneity biases it *upward*, so HR ≤ 2.5 is conservative evidence against complex contagion; > 3 is ambiguous (complex contagion or heterogeneity).
- **A4 (what R means).** P1, P2 and P4 are evaluated on both R̂ (observable branching: what the forecast rule needs) and R_c (contagion branching: the distance-to-criticality readout). The forecast rule (P7) uses R̂, since an operator wants reach whatever the mechanism.
- **A5 (marker rule details, pre-data).** N also includes short double-quoted phrases (2–6 words) and hex identifiers (7–40 characters, commit-like). W's dictionary check also strips -d, -er, -ers, -est, -ness, -ment(s), restores a final e, undoubles consonants, and maps -ies/-ied/-ier/-iest/-ily to -y.

- **A6 (post hoc; after the real-data run; NOT pre-registered).** P7 failed (coverage 36% / 46%). Diagnosis: kickoff-day inflation of R̂, downward drift within periods, and day-level extra-binomial variance. Three candidate forecast rules were scored on the same day-ahead design (`analysis/forecast_posthoc.py`): V1 = GW-NB from all prior days, V2 = without the kickoff day, V3 = the previous two days. All add a day drift R_d = R̂·e^η, η ~ N(0, σ_η²), with σ_η estimated leave-one-period-out (median 0.254). V3 is frozen as the candidate operator rule and is tested only by `analysis/confirm.py` (C4). Choosing among three variants on the same 219 days is mild multiplicity, disclosed.

## Results by goal period
Verdict rule A2 (written in every G card at 02:00 UTC, before its run). **4 supported, 26 mixed, 2 failed, 0 n/a.**
- **Supported:** G05, G06, G37, G42. G05 and G06 pass the shape test trivially: rooms of 4 cap trees at 4.
- **Failed:** G11, G16. HR₁₀ includes 1 and the tail is heavier than FN-GW.
- **Mixed:** almost all because the FN-GW tail band misses at s ≥ 5 while HR₁₀ passes.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G05](goalperiod-subhypotheses/G05/README.md) | exploratory | supported | regime I, N_room 4, 592 trees; R̂ 0.20 [0.17, 0.23]; R_c 0.10; HR₁₀ 2.0 [1.5, 2.9]; P(s ≥ 2) 0.18; s_max 4; tail ok |
| [G06](goalperiod-subhypotheses/G06/README.md) | exploratory | supported | regime I, N_room 4, 1171 trees; R̂ 0.10 [0.08, 0.12]; R_c 0.06; HR₁₀ 2.1 [1.3, 3.4]; P(s ≥ 2) 0.10; s_max 4; tail ok |
| [G07](goalperiod-subhypotheses/G07/README.md) | exploratory | mixed | regime I, N_room 4, 194 trees; R̂ 0.06 [0.03, 0.10]; R_c 0.03; HR₁₀ 1.7 [0.7, 4.1]; P(s ≥ 2) 0.06; s_max 3; tail ok |
| [G08](goalperiod-subhypotheses/G08/README.md) | exploratory | mixed | regime I, N_room 4, 1560 trees; R̂ 0.13 [0.11, 0.14]; R_c 0.01; HR₁₀ 1.1 [0.7, 1.7]; P(s ≥ 2) 0.11; s_max 4; tail ok |
| [G10](goalperiod-subhypotheses/G10/README.md) | exploratory | mixed | regime I, N_room 7, 294 trees; R̂ 0.17 [0.13, 0.22]; R_c 0.14; HR₁₀ 4.8 [2.4, 10.2]; P(s ≥ 2) 0.15; s_max 5; s ≥ 5 heavier than FN-GW |
| [G11](goalperiod-subhypotheses/G11/README.md) | exploratory | failed | regime I, N_room 7, 565 trees; R̂ 0.16 [0.12, 0.19]; R_c 0.04; HR₁₀ 1.3 [0.9, 1.9]; P(s ≥ 2) 0.12; s_max 6; s ≥ 5 heavier than FN-GW |
| [G12](goalperiod-subhypotheses/G12/README.md) | exploratory | mixed | regime I, N_room 7, 1024 trees; R̂ 0.23 [0.20, 0.26]; R_c 0.10; HR₁₀ 1.8 [1.4, 2.2]; P(s ≥ 2) 0.17; s_max 7; s ≥ 5 heavier than FN-GW |
| [G13](goalperiod-subhypotheses/G13/README.md) | exploratory | mixed | regime I, N_room 6, 1261 trees; R̂ 0.14 [0.11, 0.16]; R_c 0.08; HR₁₀ 2.3 [1.6, 3.3]; P(s ≥ 2) 0.10; s_max 6; s ≥ 5 heavier than FN-GW |
| [G16](goalperiod-subhypotheses/G16/README.md) | exploratory | failed | regime I, N_room 7, 967 trees; R̂ 0.09 [0.06, 0.11]; R_c 0.00; HR₁₀ 0.9 [0.6, 1.5]; P(s ≥ 2) 0.06; s_max 7; s ≥ 5 heavier than FN-GW |
| [G17](goalperiod-subhypotheses/G17/README.md) | exploratory | mixed | regime I, N_room 7, 399 trees; R̂ 0.18 [0.14, 0.23]; R_c 0.02; HR₁₀ 1.1 [0.7, 1.8]; P(s ≥ 2) 0.12; s_max 7; tail ok |
| [G18](goalperiod-subhypotheses/G18/README.md) | exploratory | mixed | regime I, N_room 8, 3294 trees; R̂ 0.31 [0.29, 0.32]; R_c 0.18; HR₁₀ 2.4 [2.2, 2.7]; P(s ≥ 2) 0.22; s_max 8; s ≥ 5 heavier than FN-GW |
| [G19](goalperiod-subhypotheses/G19/README.md) | exploratory | mixed | regime I, N_room 7, 2909 trees; R̂ 0.21 [0.19, 0.23]; R_c 0.15; HR₁₀ 3.3 [2.8, 4.1]; P(s ≥ 2) 0.15; s_max 8; s ≥ 5 heavier than FN-GW |
| [G20](goalperiod-subhypotheses/G20/README.md) | exploratory (card) | mixed | regime I, N_room 10, 3388 trees; R̂ 0.25 [0.23, 0.27]; R_c 0.15; HR₁₀ 2.5 [2.2, 2.9]; P(s ≥ 2) 0.15; s_max 9; s ≥ 5 heavier than FN-GW |
| [G21](goalperiod-subhypotheses/G21/README.md) | exploratory | mixed | regime I, N_room 8, 1968 trees; R̂ 0.19 [0.17, 0.22]; R_c 0.09; HR₁₀ 1.9 [1.5, 2.3]; P(s ≥ 2) 0.12; s_max 9; s ≥ 5 heavier than FN-GW |
| [G23](goalperiod-subhypotheses/G23/README.md) | exploratory | mixed | regime I, N_room 10, 1196 trees; R̂ 0.18 [0.15, 0.21]; R_c 0.10; HR₁₀ 2.3 [1.6, 3.6]; P(s ≥ 2) 0.11; s_max 10; s ≥ 5 heavier than FN-GW |
| [G24](goalperiod-subhypotheses/G24/README.md) | exploratory | mixed | regime I, N_room 10, 2870 trees; R̂ 0.14 [0.13, 0.16]; R_c 0.11; HR₁₀ 4.6 [3.5, 6.2]; P(s ≥ 2) 0.10; s_max 9; s ≥ 5 heavier than FN-GW |
| [G25](goalperiod-subhypotheses/G25/README.md) | exploratory | mixed | regime I, N_room 10, 3013 trees; R̂ 0.21 [0.19, 0.23]; R_c 0.16; HR₁₀ 4.7 [3.9, 5.8]; P(s ≥ 2) 0.13; s_max 10; s ≥ 5 heavier than FN-GW |
| [G26](goalperiod-subhypotheses/G26/README.md) | exploratory | mixed | regime I, N_room 10, 2343 trees; R̂ 0.24 [0.22, 0.27]; R_c 0.18; HR₁₀ 4.0 [3.3, 4.8]; P(s ≥ 2) 0.14; s_max 10; s ≥ 5 heavier than FN-GW |
| [G27](goalperiod-subhypotheses/G27/README.md) | exploratory | mixed | regime I, N_room 10, 5629 trees; R̂ 0.39 [0.37, 0.41]; R_c 0.28; HR₁₀ 3.6 [3.2, 4.1]; P(s ≥ 2) 0.23; s_max 10; s ≥ 5 heavier than FN-GW |
| [G30](goalperiod-subhypotheses/G30/README.md) | exploratory | mixed | regime I, N_room 11, 2357 trees; R̂ 0.33 [0.31, 0.36]; R_c 0.27; HR₁₀ 5.3 [4.5, 6.4]; P(s ≥ 2) 0.20; s_max 11; s ≥ 5 heavier than FN-GW |
| [G31](goalperiod-subhypotheses/G31/README.md) | exploratory | mixed | regime I, N_room 11, 3699 trees; R̂ 0.29 [0.27, 0.31]; R_c 0.24; HR₁₀ 6.3 [5.5, 7.4]; P(s ≥ 2) 0.17; s_max 11; P(s ≥ 3) outside band |
| [G33](goalperiod-subhypotheses/G33/README.md) | exploratory | mixed | regime II, N_room 11, 3730 trees; R̂ 0.33 [0.31, 0.35]; R_c 0.29; HR₁₀ 8.0 [7.0, 9.0]; P(s ≥ 2) 0.21; s_max 10; P(s ≥ 3) outside band |
| [G35](goalperiod-subhypotheses/G35/README.md) | exploratory | mixed | regime II, N_room 9, 3350 trees; R̂ 0.33 [0.32, 0.35]; R_c 0.32; HR₁₀ 22.7 [20.1, 25.8]; P(s ≥ 2) 0.24; s_max 12; P(s ≥ 3) outside band |
| [G36](goalperiod-subhypotheses/G36/README.md) | exploratory | mixed | regime III, N_room 8, 4076 trees; R̂ 0.22 [0.21, 0.24]; R_c 0.21; HR₁₀ 14.2 [12.5, 16.0]; P(s ≥ 2) 0.17; s_max 9; s ≥ 5 heavier than FN-GW |
| [G37](goalperiod-subhypotheses/G37/README.md) | exploratory | supported | regime III, N_room 9, 862 trees; R̂ 0.21 [0.17, 0.24]; R_c 0.20; HR₁₀ 64.8 [43.6, 102.0]; P(s ≥ 2) 0.17; s_max 7; tail ok |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory | mixed | regime III, N_room 8, 7997 trees; R̂ 0.26 [0.25, 0.27]; R_c 0.25; HR₁₀ 75.4 [66.7, 85.6]; P(s ≥ 2) 0.22; s_max 7; P(s ≥ 3) outside band |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory | mixed | regime III, N_room 11, 3185 trees; R̂ 0.09 [0.07, 0.10]; R_c 0.07; HR₁₀ 7.2 [5.3, 10.0]; P(s ≥ 2) 0.07; s_max 8; s ≥ 5 heavier than FN-GW |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory | mixed | regime III, N_room 14, 6100 trees; R̂ 0.24 [0.22, 0.25]; R_c 0.22; HR₁₀ 18.5 [15.6, 22.2]; P(s ≥ 2) 0.17; s_max 11; s ≥ 5 heavier than FN-GW |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory | mixed | regime III, N_room 11, 6150 trees; R̂ 0.23 [0.22, 0.25]; R_c 0.23; HR₁₀ 32.8 [28.5, 37.5]; P(s ≥ 2) 0.19; s_max 10; s ≥ 5 heavier than FN-GW |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory (card) | supported | regime III, N_room 11, 3944 trees; R̂ 0.13 [0.12, 0.15]; R_c 0.13; HR₁₀ 45.2 [34.8, 58.9]; P(s ≥ 2) 0.11; s_max 9; tail ok |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory | mixed | regime III, N_room 12, 2917 trees; R̂ 0.20 [0.18, 0.21]; R_c 0.20; HR₁₀ 62.5 [49.4, 79.4]; P(s ≥ 2) 0.16; s_max 7; s ≥ 5 heavier than FN-GW |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory (card) | mixed | regime III, N_room 25, 53355 trees; R̂ 0.22 [0.22, 0.23]; R_c 0.21; HR₁₀ 18.4 [16.9, 20.1]; P(s ≥ 2) 0.18; s_max 26; s ≥ 5 heavier than FN-GW |

## Outcome vs prediction
| # | Prediction (written 01:30 UTC; A1–A5 at 01:57 UTC) | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 | R̂ < 1 (upper CI < 1) in every period, and in ≥ 90% of class cells; typical 0.05–0.5; class order U > N > D | R̂ 0.06–0.39 (median 0.21); upper CI < 1 in 32/32 periods and 113/113 class cells. Class medians: U 0.35, D 0.27, W 0.27, N 0.19. U > N in 18/21 periods, but U > N > D in only 3/21 | **pass** (subcritical); class order **fail**: numbers spread more than names |
| P2 | HH108 not supported at the idea level: R̂ < n̂_talk (H03) in ≥ 60% of periods | R̂ < n̂ in 25/32 (78%), R_c < n̂ in 28/32. R̂ > n̂ beyond its CI in 6 periods (all with n̂ ≤ 0.13) | **pass** |
| P3a | Unfitted FN-GW (A1) covers P(s ≥ 3) and P(s ≥ 5) in ≥ 2/3 of periods | Both covered in 7/32; P(s ≥ 3) alone in 27/32. P(s ≥ 5) is *heavier* than the band in 25/32; the renormalized GW-NB covers both in 9/32 | **fail**: tails are heavier than a single branching law |
| P3b | Pure s^−3/2 rejected in #20 and #51; τ_app ≥ 2 | Rejected in 32/32 (LR 10²–4×10⁴); τ_app 2.4–4.3 | **pass** |
| P3c | τ with a cutoff not identifiable at village N (S1 decides) | S1: biased (0.5–2.9) and model-dependent, so dropped as a readout. Real τ_app tracks R̂ (ρ = −0.95) and matches S1's calibration within ±0.27 | **pass** (as predicted); the "exponent" is just R̂ in another form |
| P4 | ρ(R̂, H03 n̂_talk) > 0 at one-sided p < 0.05 (Holm over 4) | ρ = 0.06 (R̂ ~ n̂), 0.03 (R̂ ~ H19 g_eq talk), 0.12 / 0.11 (P(s ≥ 3)); all Holm p = 1. R̂ rises with N_room (ρ = 0.45) while n̂ falls with it (−0.35) | **fail** |
| P5a | Jitter exposure-ordering excess, p < 0.05 in ≥ 2/3 of periods | 0/32. The test failed its synthetic guard (A2), so this is uninterpretable | **fail / uninterpretable** |
| P5 (A2) | HR₁₀ > 1 with lower CI > 1 in ≥ 2/3 of periods | 27/32. Regime I median 2.3 (16/21 pass), regime II 14, regime III 39 (11/11). Contagion share R_c median 0.15, R_c/R̂ median 0.77 | **pass** |
| P5b | More adoptions at the first talk turn after exposure than the null | 32/32 (median 0.27 vs 0.07). Weakly discriminating in S2 | pass (descriptive) |
| P5c | Multi-room periods: exposed / never-exposed adoption ratio > 3; ε̂ > 0 | 9/9 two-room periods, ratios 13–970 (room-specific fields confound). Unexposed ("field") roots are 2% of trees (median) | **pass**, confounded |
| P6 (A3) | Pooled recency HR(2 vs 1) ≤ 2.5 in most periods; no class HR > 3 with lower CI > 2.5 | ≤ 2.5 in 4/32 (median 4.2); flagged in 20/32 periods and 28 class cells (mostly N). The idea-stratified estimate (biased low) has median 0.51. The bracket [0.5, 4.2] contains the simple value 2 and S2's simple-contagion values | **fail as stated; ambiguous** (simple contagion + heterogeneous salience, or complex contagion) |
| P7 | Day-ahead FN-GW 90% PIs cover P(s ≥ 2), P(s ≥ 3) on ≥ 80% of days; beat N2 and N3 in ≥ 2/3 of periods | Coverage 36% / 46% over 219 days; beats N2 31/32 and N3 29/32; loses to the beta-binomial (9/32) and the empirical (12/32) rivals | **fail** (coverage). Post hoc V3: 70% / 84% |

## Results
`analysis/explore.py` → `data/processed/H34-idea-cascades/results/{period_table.parquet, summary.json, forecast_days.parquet}`; figures in `figures/`.

**1. Ideas spread, but subcritically, everywhere.**
- **Scale:** 32 non-holdout periods; 132,323 ideas with at least one agent user, 177,407 agent first uses.
- **Reach:** a new marker reaches a second agent 6–24% of the time, a third 0.5–13%, and five or more 0–6%.
- **R̂:** 0.06 to 0.39 with tight CIs (#51: 0.221 [0.217, 0.225]). Not one period, and not one of 113 class cells, comes near R = 1.
- **What spreads most:**
  - Artifacts (repo, site and file URLs; median R̂ 0.35, P(s ≥ 3) 15%) spread most.
  - Numbers (the claim proxy) and rare words come next (0.27).
  - Capitalized names, quoted phrases and identifiers come last (0.19); many of them are one-off headings.
- **Misinformation proxy:** a typical numeric claim reaches 1/(1 − 0.27) ≈ 1.4 agents on average. About 6% of numbers reach three or more agents.

**2. It is exposure-driven, not only a common field, but the field is large in one-room swarms.**
- **What S2 showed:** in a shared room almost every adopter has "seen" the idea, so R̂ alone can't separate contagion from independent invention. A pure field produces R̂ up to 0.5.
- **HR₁₀ separates them.** It compares the adoption hazard right after a visible use (within the agent's last 3 call windows) with the hazard otherwise. It exceeds 1 in 27/32 periods. Its size depends on the scaffold: about 2 in regime I (sessions; 5 periods inconclusive), 14–75 in regimes II/III. With always-on computer use, agents reuse a term within a turn or two of reading it, or not at all.
- **Contagion share:** R_c = R̂(1 − 1/HR₁₀) is 0.0–0.18 in regime I but ≈ R̂ in regime III (0.07–0.32).
- **Two-room weeks:** agents who never saw an idea almost never use it (13–970× less). This is consistent with contagion, but rooms also worked on different things.

**3. The tail is not s^−3/2, and the "exponent" is just R̂ again.**
- **Pure critical law:** rejected in every period.
- **Apparent exponent:** τ_app (2.4–4.3) falls monotonically with R̂ (ρ = −0.95) and matches the S1 calibration curve τ_app(R) within ±0.27. So "the exponent reads off the distance to criticality" holds, but only as a reparametrization of R̂. An operator gains nothing from fitting a power law.
- **Tails heavier than branching:**
  - Size-5+ cascades are more frequent than a homogeneous finite-N branching law with the same mean predicts (25/32).
  - Adopters have more offspring than inventors (0.30 vs 0.18).
  - A beta-binomial with heterogeneous salience forecasts as well as or better than branching.
  - Reading: **a mixture of subcritical branching processes with idea-specific R.** A few ideas (shared URLs, goal-defining names, numbers everyone must use) are "hot"; most die with their inventor.

**4. Activity criticality does not predict idea spread (P4 failed).**
- **Activity gains:** R̂ is unrelated to H03's activity branching ratio (ρ = 0.06) and to H19's talk gain.
- **Room size:** R̂ rises with room size (more potential adopters; ρ = 0.45), while per-pair branching R̂/(N−1) falls as (N−1)^−0.55 (`figures/rpair_vs_N.pdf`). That matches H18's attention dilution, J ∝ N^−0.6.
- **H25's content dial (post hoc; `analysis/h25_link.py`):**
  - Period level: R̂ tracks it (ρ = 0.58; partial ρ = 0.41 given N_room, p = 0.018).
  - Within periods: daily R̂ tracks the daily content dial (ρ = 0.28, p = 5×10⁻⁶, 250 days) and the talk dial (0.23), but not the activity dial (−0.03).
  - Reading: what agents *say* and *when they act* are separate channels, as HH108 proposed, but both are subcritical.
  - Caveat: R̂ and the content dial come from the same chat text, so they share variance by construction.

**5. Simple vs complex contagion is unresolved.** Two exposures raise the per-turn adoption hazard by between 0.5× and 4.2×, depending on which bias you accept:
- idea-stratified, biased low by outcome-dependent exposure;
- pooled, biased high by idea heterogeneity.

S2's simple-contagion values (0.3–0.7 stratified, 1.25–2.4 pooled) sit inside the real bracket (0.15–0.9 stratified, 1.3–18 pooled). The real pooled values are higher, which is what heterogeneity does. #51, the largest period, gives pooled 1.31 [1.16, 1.46]: simple.

**6. Forecasting how far an idea spreads.**
- **Pre-registered rule:** FN-GW from all prior days. It was overconfident: coverage 36% / 46% at 90% nominal. R̂ is inflated on kickoff days and drifts down within periods; day-to-day variance is about 3.5× the sampling variance.
- **Post-hoc V3:** GW-NB from the previous two days' R̂ and k̂, plus a log-normal day drift (σ_η = 0.25). Coverage 70% / 84%. It beats the homogeneous field and the activity plug-in in 31/32 periods and the empirical rival in 20/32, and ties the beta-binomial. Frozen for the holdout (C4).

## Operator-facing forecast rule (round 1; post hoc, frozen for confirmation)
1. From the last two days of logs, mark novel terms, URLs, numbers and names (rule above).
2. Build exposure trees: each agent's first use, parented to the latest visible earlier use.
3. Compute **R̂ = (first uses with an agent parent) / (all agent first uses)**, and the offspring dispersion k̂ (median 1.3).
4. Tomorrow, a new idea's cascade size S is GW-NB(R̂·e^η, k̂) truncated at the room size, with η ~ N(0, 0.25²).

Values for N = 15 and k = 1.28 (`results/operator_table.json`). The bracket is the 90% range for a day's rate.

| R̂ | E[S] | P(S ≥ 2) | P(S ≥ 3) | P(S ≥ 5) | 99.9% of ideas reach ≤ |
| --- | --- | --- | --- | --- | --- |
| 0.1 | 1.11 | 0.09 [0.06, 0.13] | 0.015 [0.007, 0.03] | 0.0007 | 4 agents |
| 0.2 | 1.25 | 0.17 [0.12, 0.24] | 0.05 [0.03, 0.10] | 0.007 [0.002, 0.02] | 7 |
| 0.3 | 1.43 | 0.24 [0.17, 0.32] | 0.09 [0.05, 0.16] | 0.02 [0.007, 0.06] | 10 |
| 0.4 | 1.65 | 0.29 [0.22, 0.38] | 0.14 [0.08, 0.23] | 0.05 [0.02, 0.11] | 13 |

Use it as follows. In this village R̂ ≈ 0.2, so 83% of new ideas or claims never reach a second agent, about 5% reach three, and about 1 in 150 reaches five. Expect day-1 values about 1.5× higher. **Do not use activity loop gains (Hawkes n̂) as a proxy; they carry no information about idea spread here.** Per-pair spread falls as N^−0.55, so bigger rooms spread an idea to *more* agents in total but each agent is less likely to pick it up.

## Figure summary
- `figures/summary_obs.pdf` (page figure):
  - (a) CCDF of tree sizes for #20, #42 and #51 with the GW-NB law from R̂ and k̂ (dashed) and the critical s^−3/2 (dotted): tails sit between, steep but heavier than GW-NB;
  - (b) R̂ vs H03 activity n̂ for 32 periods, colored by regime: no relation; most periods lie below R̂ = n̂.
- `figures/hr10_by_period.pdf`: HR₁₀ with CIs per period, a step change from regime I (≈ 2) to regimes II/III (14–75).
- `figures/rpair_vs_N.pdf`: per-pair branching vs room size, slope −0.55.
- `figures/forecast_calibration.pdf`: day-ahead observed vs forecast P(s ≥ 2) and P(s ≥ 3), pre-registered vs post-hoc V3.
- `figures/synthetic_validation.pdf`: (a) τ_app(R) calibration; (b) depleted R̂ vs FN-GW R0; (c) S2: R̂ inflated by the field, R_c tracks truth.

## Caveats
- **What counts as an "idea"** is a rule (hashed markers), not a semantic unit. R̂ depends on the rule: names have many one-off headings, which pull R̂ down. Embedding-cluster novelty was not done.
- **Field vs contagion rests on HR₁₀.** A *bursty* common field (an external trigger reaching several agents within minutes) would also give HR₁₀ > 1; S2 only simulated a constant field. Copying from tool output or the web (hidden sources) is invisible here.
- **Assumptions:**
  - Visible exposure uses H18's call-start rule, whose invisible-message placebo failed in H18 for mentions.
  - The recency window (3 call windows) is an assumption.
  - Regime I turn logging differs, which may explain its smaller HR₁₀.
- **Novelty baseline:** novelty is relative to the non-holdout corpus only. A marker first used in a held-out period counts as novel when it reappears later. This mostly affects early-regime-III periods after #34 and #45–#50.
- **Same text, no independent instrument:** the H25 content-dial link is post hoc and shares its source text with R̂.
- **Multiplicity:**
  - P4 used Holm over 4 tests.
  - Class-level flags (28 cells) are descriptive.
  - Post-hoc variants (A6, the H25 link, the per-pair slope, the HR bracket) are labeled and not counted as confirmations.
- **N = 4 periods** (#5–#8) cannot show tails, so their "supported" verdicts rest on HR₁₀ alone.

## Confirmatory predictions (written 2026-10-04 after round 1, before any holdout use; `analysis/confirm.py`, not run)
Targets:
- **T1:** #51 tail (09-07 → 09-21), the primary target;
- **T2:** #15 (regime I, mode C);
- **T3:** #28 (regime I, mode C);
- **T4:** #22 (regime I, mode F).

Frozen tests:
- **C1, subcritical:** R̂ upper CI < 1 and R̂ ∈ [0.08, 0.40] in every target.
- **C2, contagion beyond the field:** HR₁₀ lower CI > 1 in ≥ 3/4 targets, including T1.
- **C3, per-pair dilution:** log(R̂/(N−1)) inside the 90% PI of the non-holdout fit (−2.547 − 0.549 log(N−1), s = 0.380) in ≥ 3/4 targets.
- **C4, the V3 forecast rule:** pooled day-ahead coverage ≥ 0.75 for P(s ≥ 3) and ≥ 0.60 for P(s ≥ 2); V3 beats the binomial field rival in every target with ≥ 2 scored days.
- **C5, signature:** pure s^−3/2 rejected and τ_app ≥ 2 wherever there are ≥ 200 trees.
- **C6, heterogeneity:** T1's P(s ≥ 5) above the FN-GW band, and roots have fewer offspring than non-roots in ≥ 3/4 targets.

**Supported** if C1, C2 and C5 pass. **Forecast rule confirmed** if C4 passes.

The dry run on stand-ins passes all six, as it should on seen data (`results/confirm_dryrun.json`). The script seals a SHA-256 of the frozen predictions before reading held-out text.

**Reuse disclosure** (policy in `../holdout.md`):
- The #51 tail is also targeted by the unrun scripts of H14, H18, H20 and H22.
- #22 and #28 are targeted by H11 and H10.
- None of those has run, and H34's observable (first-use cascades of novel markers) is a different statistic from all of them.
- Avoided: #45 (H23's content copying), #14 (H24's numbers), #34 (six scripts).

## Round 1b (improved data, 2026-10-04)

### Inputs changed
- **Visibility (DQ1 context ledger).** Round 1 imported H18's call-start rule on the `exposure` room table (the known issue "H34's cascade trees use H18's call-start visibility rule"). Round 1b: a use m is a visible exposure of agent j's use u iff m reached one of j's receiving calls (`context_ledger_items` ⋈ `call_windows`) no later than the call that produced u (j's latest `t_call` before u). The same rule sets k_src, the parent, the lag, the at-risk sets (HR₁₀, dose-response), the jitter null and the room contrast. The fallback share is 0 in every period (round 1: 0.1–1.7%).
- **Copying vs convergence (H57).** New placebo at every at-risk talk turn: HR_seen5 = adoption hazard when another agent's use of the idea was posted in the last 5 min *and* already read by the producing call; HR_unread5 = the same when such a use exists but was still in flight (same room, read by a later call). Both against turns with no use in the last 5 min; idea-stratified conditional likelihood, profile CIs. Copying predicts HR_seen5 > 1 ≈ HR_unread5; contemporaneous convergence predicts HR_unread5 ≈ HR_seen5.
- **Not used here:** activity bins, outages, embeddings and reply threading (H34's ideas are hashed text markers and its trees are exposure-based). Markers are unchanged.
- **Code.** Switch `H34_DATA=r1b` in `scheme/h34core.py` (also read by `scheme/build.py` and `analysis/explore.py`); the default reproduces round 1 byte for byte (checked on #42: first uses, trees, at-risk, jitter and room tables identical). New: `analysis/r1b_natives.py` (natives, estimates). Outputs: `data/processed/H34-idea-cascades/r1b/` (9 MB; `results/period_table.parquet`, `summary.json`, `natives.json`). 162 rows in `per_period_estimates` (method `H34.r1b_ledger`, `H34.r1b_leader_seed`).

### Old → new (32 non-holdout periods)
| Statistic | Round 1 (H18 rule) | Round 1b (ledger) |
| --- | --- | --- |
| R̂ range (median) | 0.06–0.39 (0.21) | 0.09–0.40 (0.22); upper CI < 1 in 32/32, 113/113 class cells |
| HR₁₀ lower CI > 1 (P5, A2) | 27/32 | **32/32** |
| HR₁₀ median, regime I / II / III | 2.3 / 15 / 33 | **6.4** / 20 / 47 |
| R_c median (R_c / R̂) | 0.15 (0.77) | 0.21 (0.89) |
| Per-period verdicts (supported / mixed / failed) | 4 / 26 / 2 | **9 / 23 / 0** |
| P3a FN-GW band covers P(s ≥ 3) and P(s ≥ 5) | 7/32 | 9/32 |
| P4 ρ(R̂, H03 n̂_talk) | 0.06 (Holm p 1) | 0.19 (Holm p 0.33) |
| P6 pooled HR(2 vs 1) median | 4.2 | 4.1 |
| P7 pre-registered forecast coverage P(s ≥ 2) / P(s ≥ 3) | 36% / 46% | 38% / 47% |
| P5a jitter excess p < 0.05 | 0/32 | 3/32 (test still fails its guard) |
| **New (H57):** HR_seen5 > HR_unread5 | — | **30/32**; HR_unread5 lower CI > 1 in 25/32 |
| **New:** HR_unread5 / HR_seen5, median (regime I / II / III) | — | **0.56** (0.60 / 0.61 / 0.31); on the log scale unread carries 69% of the seen effect |

### Verdict changes
- **Regime I was mismeasured, not weak.** Round 1's five regime-I failures of HR₁₀ (#7, #8, #11, #16, #17) came from the call-start rule (scheduled chat-mode calls and pauses): on the ledger all 21 regime-I periods pass and the regime-I median HR₁₀ nearly triples (2.3 → 6.4). G11 and G16 move from failed to mixed (HR₁₀ now passes, tail still heavy); G07, G08, G10, G17 and G23 move from mixed to supported. The regime step in HR₁₀ (I ≪ III) shrinks but stays (6 vs 47).
- **The exposure-locked adoption is partly convergence.** Uses that were posted in the last 5 min but not yet read predict adoption too (25/32 periods with CI > 1), at about half the strength of read ones. Read uses beat unread ones in 30/32, so copying through reading is real, but HR₁₀ (and R_c) overstate it. Unread uses are on average *more recent* than read ones within the window, which favours convergence, so the copying excess HR_seen5/HR_unread5 (median ≈ 1.8) is a conservative estimate.
- Unchanged: subcritical everywhere; no s^−3/2; τ_app is R̂ reparametrized; tails heavier than one branching law; P4 (activity gains) and P7 (pre-registered forecast) still fail; simple vs complex stays ambiguous.

### Natives (predictions in the period READMEs, written 16:50 UTC before running)
| Folder | Test | Result | Verdict |
| --- | --- | --- | --- |
| [G35](goalperiod-subhypotheses/G35/README.md) | DQ6 daily lead designers as idea seeders (6 room-days) | P(s ≥ 2) ratio 1.11 [0.82, 1.45] (227 vs 1,621 seeds). Negative control as written failed (49% of cross-room first uses exposed, because ideas spread inside the new room after crossing); post hoc, the crossing events are exposed in 6/235 (2.6%) | **mixed** (prediction > 1 failed) |
| [G26](goalperiod-subhypotheses/G26/README.md) | DQ6 elected leader (from 01-05 19:35) as idea seeder | ratio **0.36 [0.27, 0.46]**; it seeds 7.5× more new markers per message, each far less taken up | **failed** (leader is a high-volume, low-uptake source) |

Known idea origins (designated and elected leaders) are not visible as higher branching: authority does not raise R for the ideas a leader introduces.

### Scorecard changes
| Axis | Round 1 | 1b | Why |
| --- | --- | --- | --- |
| A mapping | 1 | 1 | Visibility is now the validated ledger; the regime dependence of HR₁₀ shrinks (×20 → ×7) but remains. |
| C adequacy | 1 | 1 | HR₁₀ beats the field null in 32/32; the forecast still loses to the beta-binomial. |
| D unfitted | 1 | 1 | Unchanged: both tail probabilities covered in only 9/32 (round 1: 7/32). |
| E interventional | 0 | 0 | No NE test; natives use ground truth, not a step change. |
| G ground truth | 1 | 1 | Known seeders (leaders) tested: no premium (#35), deficit (#26). Room crossings are unexposed (97%). |
| H comparative | 1 | 1 | New rival, contemporaneous convergence (H57): partly beaten (seen > unread 30/32) but explains about half the hazard ratio. |
| I transfer | 1 | 1 | 32/32 periods on both statistics. |

**Model- and style-dependence.** No embedding enters H34 (ideas are hashed markers), so nothing here depends on bge vs gte or on style. The results depend on the marker rule and, for regime I, on the visibility rule: the regime-I HR₁₀ values are ledger-dependent (2.3 under the old rule). Suggested ratings: completeness 50 (from 42), faithfulness 2.0, usefulness 2.5.

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **Where round 1 went sideways:** the hypothesis bet on power-law exponents and activity loop gains. Village cascades are short (s ≤ N), and the exponent is just the branching ratio reparametrized. The useful object is the branching ratio of ideas and its heterogeneity.
- **What the direction is really after:** how far does a new idea or claim spread in an agent swarm, and what sets it: exposure, salience or a shared field?
- **H34-R1.** Heterogeneous branching: fit a gamma mixture over idea-level R (one extra parameter) and test whether it removes the excess of trees with five or more agents and beats the beta-binomial on day-ahead log score.
- **H34-R2.** Natural experiments for idea spread: the NE15 room split and the 05-04 merge, with the branching ratio and the per-pair branching per room member predicted from room size before looking (axis E).
- **H34-R3.** Claims proper: label numeric claims as true or false (or corrected) with Jev and compare branching ratios of false claims and their corrections (the misinformation question).
- **H34-R4.** Semantic ideas: embedding-cluster novelty, so paraphrased ideas count, with the same trees and HR10.

## Round 2 (2026-10-05): R1, R4, R2 on non-reserved room changes
Round 2 runs H34-R1, R4 and R2. R3 is not run (it needs paid LLM labels). R2 does not use NE15 (reserved); it uses NE42 and the other non-reserved regime-III room changes. Non-reserved data only (`holdout_mask` on every period's days, as in rounds 1 and 1b).

### Pre-registration
*Written 2026-10-05 03:50 UTC (committed 03:50, 62577cc), before any round-2 statistic on real data.*

**Seen beforehand:**
- Everything on this card, including the round-1 and 1b period-level R̂ of every period (G36–G42 among them) and the round-1 forecast table.
- Design quantities only: the posting agents of each room in G36–G42 (modal room per agent; table below), weekly room sizes in G51, `rooms_timeline` for 2026-04-25 → 05-25, the agent message-length quantiles (median 403 characters; 0.4% under 40) and the DQ5 embedding file shapes.
- Not computed: any group-level or window-level R̂, any mixture fit, any semantic idea, any round-2 forecast score.

**Code switches.** All round-2 code is new (`analysis/r2_mixture.py`, `scheme/build_semantic.py`, `analysis/r2_semantic.py`, `analysis/r2_ne.py`, `analysis/r2_summarize.py`). Round-1 and 1b code is unchanged, so both reproduce. Outputs go to `data/processed/H34-idea-cascades/r2/`. Rows go to `per_period_estimates` under new method names (`H34.r2_*`).

#### R1: heterogeneous branching (gamma mixture over idea-level R)
**Model Γ-FN.** Idea i draws R0_i ~ Gamma(shape α, mean μ). Given R0_i, each tree of idea i is a finite-N Galton–Watson tree with Poisson offspring and depletion (FN-GW, A1), on N_fit = max(N_room, s_max). The trees of one idea share R0_i. R0 is integrated on a fixed log-spaced grid (0.002–8, 96 points) with gamma weights from CDF differences. Fit: maximum marginal likelihood over ideas, two parameters (μ, α). The homogeneous limit α → ∞ is FN-GW-Poisson (H0). Data: the round-1b trees (marker ideas, ledger visibility); the R4 semantic trees are a secondary input.

**Tests.**
- **R1-T1 tail.** Parametric band (90%) for P(s ≥ 3) and P(s ≥ 5): 1,000 multinomial draws of the period's tree count from the fitted marginal, with parameter uncertainty from 25 idea-cluster bootstrap refits (as in A1). Comparator: round-1b FN-GW (NB k̂, calibrated mean), which covers both in 9/32.
- **R1-T2 heterogeneity.** LR = 2(ℓ_Γ − ℓ_H0), referred to the chi-bar² mixture ½χ²₀ + ½χ²₁ (5% point 2.71).
- **R1-T3 forecast.** The round-1 day-ahead design (P7): train on trees rooted before day d, score the trees rooted on day d, same eligibility (≥ 30 training trees, ≥ 20 test trees). Per-tree log score, summed over a period's scored days. Γ-FN is refitted on each training set. Rivals: beta-binomial (N1, round-1 code), FN-GW (round-1 pre-registered law) and the empirical rival (N4). Secondary: the V3 window (previous two days only) for Γ-FN and the beta-binomial alike, without a drift term.
- **R1-T4 unfitted statistic.** The likelihood uses only tree sizes. The ratio of mean offspring of non-root to root nodes (observed 0.30 vs 0.18 in round 1) is not fitted. Band: 200 forests simulated from the fitted Γ-FN with the period's tree count.
- **R1-T5 skeleton null.** Heterogeneity can come from the skeleton: uneven agent activity, time of day and room traffic. The S2 simulator (real #20, #42 and #51 07-27 → 08-07 timelines) with homogeneous simple contagion and a field gives the α̂ that a homogeneous process produces on that skeleton. Real α̂ below the 5th percentile of that null counts as idea heterogeneity beyond the skeleton.

| # | Prediction | Counts against | Prior |
| --- | --- | --- | --- |
| R1-P1 | Γ-FN covers P(s ≥ 3) and P(s ≥ 5) in ≥ 2/3 of periods with ≥ 50 trees | coverage of both in < 1/2 of periods: the heavy tail is not a gamma mixture of subcritical processes (kill rule for that reading) | 0.5 |
| R1-P2 | LR > 2.71 in ≥ 2/3 of periods; median α̂ in [0.2, 2] | LR > 2.71 in < 1/3 | 0.65 |
| R1-P3 | Γ-FN beats the beta-binomial on summed day-ahead log score in ≥ 1/2 of scored periods, and beats FN-GW in ≥ 2/3 | beats the beta-binomial in < 1/3 | 0.45 |
| R1-P4 | the observed non-root/root offspring ratio lies inside the Γ-FN band in ≥ 2/3 of periods | inside in < 1/3 | 0.4 |
| R1-P5 | real α̂ below the homogeneous-skeleton 5th percentile in ≥ 2 of the 3 skeleton periods | 0 of 3: the heterogeneity is the skeleton's | 0.5 |

#### R4: semantic ideas (embedding-cluster novelty)
**Semantic idea (H34 embedding rule).**
- Corpus: every non-holdout chat message (any speaker kind) with ≥ 40 characters, in time order, with its DQ5 raw embedding (fp32, unit norm). Both models: bge-small (384-d) and gte-modernbert (768-d).
- Online leader clustering (first-story detection): message m becomes a *use* of every existing seed with cos(m, seed) ≥ θ. If there is none, m founds a new seed (a new idea first used at t_m). Seeds never move, so all seeds are pairwise below θ and drift is bounded.
- Novelty: an idea of period g is a seed founded in g (the baseline is all earlier non-holdout chat, as for markers). The same 32 periods.
- Thresholds: θ_bge = 0.90 (primary; 0.85 and 0.95 as sensitivity). θ_gte is rate-matched: among 20,000 random agent messages, the share whose most similar earlier message in the same period has cos ≥ θ_gte equals the bge share at its θ. This uses no cascade statistic.
- Secondary assignment: nearest seed only (one idea per message).
- The semantic uses then enter the round-1b assembler unchanged (ledger visibility, trees, HR₁₀, the H57 seen/unread placebo, the jitter table), with class code S.

**Synthetic check (S-R4, before real data).** On the real #42 and #51 07-27 → 08-07 skeletons with real embeddings, the S2 simulator plants ideas (simple contagion q = 0.015, and q = 0 with a field). Each planted use replaces its message's embedding by a paraphrase of the seed message: cos to the seed drawn from U[0.80, 1.00], with the residual direction taken from a random real message. The pipeline must recover R on the planted ideas within ±0.05 at cos ≥ θ (or report the recall bias), keep real messages from joining planted ideas (false adopters ≤ 10% of planted first uses), and give R_c ≈ 0 at q = 0.

| # | Prediction | Counts against | Prior |
| --- | --- | --- | --- |
| R4-P1 | semantic R̂ upper CI < 1 in 32/32 periods for both models | any period with lower CI ≥ 1: paraphrase spread is near-critical | 0.85 |
| R4-P2 | across periods, Spearman ρ(semantic R̂, marker R̂) > 0.4 for both models | ρ ≤ 0: the branching ratio is a property of the idea rule, not the period | 0.6 |
| R4-P3 | models agree: ρ(R̂_bge, R̂_gte) ≥ 0.7 and median R̂_gte/R̂_bge in [0.8, 1.25] | ρ < 0.4 | 0.6 |
| R4-P4 | HR₁₀ lower CI > 1 in ≥ 2/3 of periods, and HR_seen5 > HR_unread5 in ≥ 2/3, for both models | either below 1/3 | 0.6 |
| R4-P5 | semantic ideas carry more convergence than markers: median HR_unread5/HR_seen5 > 0.56 (the marker value) | median ≤ 0.4 | 0.6 |

#### R2: room changes as natural experiments (axis E)
**Prediction rule (fixed before looking).** The round-1 cross-period dilution fit gives per-pair branching r_pair ∝ (N − 1)^−0.549, so R̂ ∝ (N − 1)^0.451. A group whose room size goes from N_b to N_a is predicted to change its source-based branching ratio by Δ_pred = 0.451 · ln[(N_a − 1)/(N_b − 1)] and its per-pair branching by −0.549 · ln[(N_a − 1)/(N_b − 1)].

**Units.**
- Boundaries: the six regime-III goal boundaries with two working rooms and no reserved side: #36→#37, #37→#38, #38→#39 (the 04-27 re-cut), #39→#40 (NE42 merge, 05-04), #40→#41 (NE42 split, 05-11), #41→#42. #35 is not used: its first day holds the reserved NE15 split.
- Groups: agents present on both sides, grouped by (modal room before, modal room after). N is the number of agents whose modal room is that room in that period (Claude Code excluded). GPT-5 alone in #rest during #40 (N = 1) is excluded. Groups with < 50 agent first uses on either side are dropped.
- Source-based branching ratio of a group: R̂_src = (agent first uses whose parent is a group member) / (first uses by group members), from the round-1b trees of each period. Idea-cluster bootstrap CIs. Per-pair: r_pair = R̂_src / (N − 1).

| Boundary | Group (N before → after) | Δ_pred ln R̂_src | Predicted R̂ ratio | Predicted r_pair ratio |
| --- | --- | --- | --- | --- |
| #36→#37 | #rest stayers (9 → 7) | −0.130 | 0.88 | 1.17 |
| #36→#37 | #best stayers (3 → 3) | 0 | 1.00 | 1.00 |
| #37→#38 | #rest (7 → 8) | +0.070 | 1.07 | 0.92 |
| #37→#38 | #best (3 → 6) | +0.413 | 1.51 | 0.60 |
| #38→#39 | #rest stayers (8 → 11) | +0.161 | 1.17 | 0.82 |
| #38→#39 | #best stayers (6 → 4) | −0.230 | 0.79 | 1.32 |
| #38→#39 | movers #best → #rest (6 → 11) | +0.274 | 1.31 | 0.72 |
| #39→#40 merge | old #best (4 → 14) | +0.661 | 1.94 | 0.45 |
| #39→#40 merge | old #rest (11 → 14) | +0.118 | 1.13 | 0.87 |
| #40→#41 split | new #best (14 → 4) | −0.661 | 0.52 | 2.24 |
| #40→#41 split | new #rest (14 → 11) | −0.118 | 0.89 | 1.15 |
| #41→#42 | #best (4 → 5) | +0.130 | 1.14 | 0.85 |
| #41→#42 | #rest (11 → 10) | −0.048 | 0.95 | 1.06 |

**Estimator.** Every boundary is also a goal change (kickoff inflation, new topic), so the common shock is removed with boundary fixed effects. The primary statistic is the slope β of observed Δ ln R̂_src on Δ_pred, within boundaries (OLS with boundary fixed effects). Equivalently, β scales the within-boundary differences between groups. β = 1: the cross-period dilution law transfers to interventions. β = 0: full attention conservation (R̂ independent of N). β = 1/0.451 ≈ 2.2: no dilution (R̂ ∝ N − 1). CI: the wider of an idea-cluster bootstrap (within periods) and a residual t interval across boundaries. The exponent implied is b̂ = 0.451 β.

**NE42 A-B-A contrast.** D = DiD(merge) − DiD(split), where DiD = Δ ln R̂_src(#best) − Δ ln R̂_src(#rest). Predicted D = 2 × 0.543 = +1.09.

**Merged-week partition contrast (#40).** Per-pair transmission rate for old-same pairs (same room in #39) vs old-cross pairs: transmissions on such pairs divided by the opportunities (for every agent node, the old-same and old-cross agents present in #40 who had not yet used the idea at that node's first use). ρ = r_cross / r_same. Reading routes are equal inside one room, so "rooms couple only by routing reading" predicts ρ = 1.

**Secondary (descriptive).** G51 #focus (08-05 → 08-24, 3–7 hopping agents) vs #general (≈ 27): per-pair branching of nodes whose first use was posted in #focus vs #general, predicted ratio (5/26)^−0.549 = 2.47. Hoppers read both rooms, so this has no clean N.

| # | Prediction | Counts against | Prior |
| --- | --- | --- | --- |
| R2-P1 | β > 0 with lower CI > 0, and the CI includes 1 | upper CI < 0.3: the dilution law does not transfer to room changes | 0.45 |
| R2-P2 | NE42 D > 0 with lower CI > 0 (predicted +1.09) | D ≤ 0 | 0.5 |
| R2-P3 | merged week ρ ≥ 0.7 and its CI includes 1 | upper CI < 0.7: old room membership carries over (a project field or acquaintance channel beyond reading) | 0.5 |
| R2-P4 | per-pair branching per room member falls with room size inside each boundary in the direction predicted for ≥ 2/3 of groups with absolute Δ_pred ≥ 0.1 | < 1/2 | 0.55 |

**Verdict rules for the period READMEs (round 2).** G37–G42 get an "NE (round 2)" line with the group values. NE42 is written to `goalperiod-subhypotheses/NE42/`: supported if R2-P1 and R2-P2 pass, failed if β's upper CI < 0.3 and D ≤ 0, mixed otherwise. Replication rows (R1, R4) go to every period README as a short round-2 line; they do not change round-1b verdicts.

#### Synthetic validation, R1 (run 2026-10-05 04:05–04:15 UTC, before any real-data round-2 statistic)
*Code: `analysis/r2_mixture.py synth_a | synth_b`. Data: `r2/mixture/synth_a.parquet`, `synth_b.parquet`.* The FN-GW size law is computed exactly by dynamic programming; it matches 200,000 simulated trees to ±0.001 at N = 4, 14, 26.

**S-R1a, pure worlds** (N 8 / 14 / 25, μ 0.15 / 0.3, 1,000 and 5,000 trees, 8 replicates; 480 fits).
- α is recovered: true 0.5 / 1 / 3 → median α̂ 0.50 / 1.04 / 3.30 (1,000 trees), 0.50 / 1.01 / 3.01 (5,000). μ within 2%.
- LR size at α = ∞: 6% (1,000 trees) and 2% (5,000). Power at α ≤ 1: 100%; at α = 3: 73% / 100%.
- The tail band covers both tail probabilities in 98–100% of runs under the true model (slightly conservative).
- **The tail and the LR do not separate idea-level from node-level heterogeneity.** Homogeneous R with NB node offspring (k = 0.5) also gives finite α̂ (1.8–2.0), LR rejection 96–100% and a covered tail.
- **The non-root/root offspring ratio does separate them.** Idea-level mixing gives ratios 1.2–2.3, inside the Γ-FN band in 96–100% of runs. Node-level NB gives 0.78–0.83, inside the band in 0–10%.

**S-R1b, skeleton worlds** (S2 simulator on real #20, #42 and #51 07-27 → 08-07; q 0.005 / 0.015 / 0.04; field 0.0005 / 0.002; 54 homogeneous runs and 18 runs with idea-level q ~ Gamma(shape 1)).
- **The skeleton does not fake idea heterogeneity in Γ-FN:** α̂ sits at the bound (500) with LR = 0 in 54/54 homogeneous runs.
- With heterogeneous q, LR > 2.71 in 16/18 runs. α̂ (3–13; 30 and 58 where R̂ ≈ 0.92) understates the planted spread, because R depends on q and on exposure, not on q alone.
- The tail band is not specific on the skeleton: it covers homogeneous worlds in 11/27 runs with the weak field and 1/27 with the strong field (tails lighter than the band).
- The non-root/root ratio is biased up by the skeleton: homogeneous worlds give 0.56–0.91, often above the fitted band (active agents both adopt and spread). Heterogeneous worlds give 0.74–1.51.

#### Amendment R2-A1 (2026-10-05 04:20 UTC, after the R1 synthetic runs, before any real-data round-2 statistic)
- **R1-P2 and R1-P5 are kept,** but R1-P2's LR cannot tell idea-level from node-level heterogeneity (S-R1a). R1-P5's skeleton null is the boundary (α̂ = 500, LR = 0 in 54/54), so R1-P5 passes in a skeleton period exactly when its LR > 2.71.
- **R1-P4 becomes the discriminating test,** read two ways: (a) as written, inside the Γ-FN band; (b) against the reference values, homogeneous skeleton ≤ 0.91, node-level NB ≈ 0.8, idea-level mixing ≥ 1.2. A real ratio above 1.0 in a period counts as idea-level (or tree-level) shared R beyond the skeleton and beyond node-level overdispersion. Reading (a) is reported, but the skeleton bias makes its band too narrow.
- **R1-P1 is kept;** a tail miss now counts against the Γ-FN idealization, as for FN-GW in round 1 (S2), not against heterogeneity.

#### Synthetic validation, R2 (run 2026-10-05 04:35 UTC, before any real-data NE statistic)
*Code: `analysis/r2_ne.py synth`. Data: `r2/ne/synth.parquet`.* The S2 simulator runs on the real G36–G42 timelines and exposure rows (900 ideas per period, 3 replicates per world). Groups, room sizes and the estimator are the real ones.

| World | β̂ (3 replicates) | NE42 D̂ | ρ̂ (#40) | R2-P4 count |
| --- | --- | --- | --- | --- |
| constant per-exposure contagion, q 0.015 | 2.46, 1.71, 1.95 | 2.38, 1.80, 2.20 | 1.01, 0.94, 1.14 | 6/10, 7/10, 5/10 |
| constant per-exposure contagion, q 0.04 | 1.50, 1.63, 1.42 | 1.51, 1.50, 1.20 | 1.00, 0.99, 1.04 | 9–10/10 |
| field only (q 0, ε 0.002) | 2.37, 2.46, 2.57 | 2.38, 2.61, 2.51 | 0.83, 0.91, 0.94 | 5–6/10 |

- **The skeleton alone gives β > 1.** With a constant chance per read exposure, a larger room exposes each idea to more readers, so β̂ is 1.4–2.5. A pure field gives β̂ ≈ 2.5, close to the no-dilution value 1/0.451 = 2.2. CIs are wide (single replicates span 0.66 to 15).
- **ρ is calibrated:** 0.83–1.14 in worlds without old-room memory.
- **R2-P4 is not specific:** the per-pair direction holds in 5–10 of 10 groups in every world.

#### Amendment R2-A2 (2026-10-05 04:40 UTC, after the R2 synthetic runs, before any real-data NE statistic)
- **R2-P1 and R2-P2 are kept as written,** but they are not specific: worlds without dilution often pass them too.
- **The discriminating reading of β is against the skeleton references:** β ≈ 1 means that the chance per read falls with room size (dilution beyond the reading structure). β ≈ 1.4–2.5 means a constant chance per read. β ≈ 2.5 means field-like spread. Real β below 1.4 with its upper CI below 2.0 counts as per-read dilution. The same scale applies to D: skeleton references 1.2–2.6, law 1.09.
- **R2-P4 is reported as descriptive only.**

#### Rate matching and synthetic validation, R4 (run 2026-10-05 04:50–04:55 UTC, before any real semantic idea or tree)
*Code: `scheme/build_semantic.py ratematch | synth`. Data: `r2/semantic/ratematch.json`, `synth_r4.parquet`.*
- **Thresholds.** Among 20,000 random agent messages, 47% have an earlier message in the same period at bge cos ≥ 0.90 (84% at 0.85, 14% at 0.95). The rate-matched gte thresholds are 0.877 (primary), 0.820 and 0.937. The 0.95 match (0.937) agrees with DQ5's independent 0.938.
- **S-R4** (#42 and #51 07-27 → 08-07, both models, simple contagion q 0.015 and field-only worlds, 2 replicates; 16 runs):

| Check (pre-registered limit) | #51 segment | #42 |
| --- | --- | --- |
| planted ideas lost because their seed restates an earlier message | 18–23% | 15–23% |
| R̂ on recovered ideas vs truth at cos ≥ θ (±0.05) | +0.00 to +0.01 | bge +0.07 to +0.11; gte +0.03 to +0.07 |
| other messages joining planted ideas (≤ 10% of first uses) | 1–3% | bge 10–14%; gte 4–9% |
| R_c with no contagion (≈ 0) | 0.00–0.03 | 0.06–0.11 |

- Planted paraphrases below θ are missed by design (truth over all planted uses is 0.03–0.09 higher than at cos ≥ θ).
- The messages that join planted ideas are real replies to the real seed message, so they are partly genuine semantic adoptions. Their excess is exposure-locked, so HR₁₀ does not remove it.

#### Amendment R2-A3 (2026-10-05 04:58 UTC, after the R4 synthetic runs, before any real semantic statistic)
- **Guards.** The pipeline passes every guard on the dense #51 skeleton and fails two on #42 with bge (false adopters 10–14%, R̂ bias up to +0.11). Real semantic R̂ is therefore read with a bias bracket of [0, +0.1] in periods the size of #42 or smaller, and gte is the primary model where the two disagree.
- **Novelty loss.** About 20% of new ideas whose seed restates an earlier message are lost. This biases the idea count, not R̂ on recovered ideas.
- R4-P1 to R4-P5 are unchanged.

**Impostors.** Scheduler field: R̂ is per first use, R1 adds a skeleton null, R2 uses boundary fixed effects. Exogenous field: boundary fixed effects absorb each goal change (common to both groups); R4 reports HR₁₀. Shared priors: semantic paraphrases can be co-generated by genre; the seen/unread placebo and HR₁₀ bound it, and no style residualization is applied (stated as open). Convergence: the H57 placebo is reported for R4; R2's R̂_src is not net of convergence (stated as partly).

## Notes
- 2026-10-04: promoted from HH122 by Vivian (usefulness-first batch); wave 2.
- 2026-10-04 01:30 UTC: round-1 agent wrote definitions, observables, nulls and predictions before any real-data run.
- 2026-10-04 01:35–01:57 UTC: marker table built (counts only); synthetic S1 and S2 run. Amendments A1–A5 written before any real-data cascade statistic. G-card predictions at 02:00 UTC.
- 2026-10-04 02:03 UTC: cascades built for 32 periods (14 MB). `explore.py` run; post-hoc A6 forecast variants; H25 link added once H25's tables appeared.
- **Proposed for `physics-models/DEFINITIONS.md`** (not edited): *Idea (H34 marker rule)*; *Interaction (visible exposure)*, i.e. the exposure row plus the H18 call-start rule; *Adoption cascade (exposure tree)*; *Branching ratio (content, adopter-level)* R̂ and its contagion share R_c = R̂(1 − 1/HR₁₀).
- **Proposed for `physics-models/03-contagion` and `09-hawkes` pitfalls:**
  - In a shared room, a common field masquerades as branching (R̂ up to 0.5 with no contagion), and exposure-ordering tests have no power. Use a recency hazard ratio with idea-stratified conditional likelihood.
  - Idea-stratified dose-response is biased low (outcome-dependent exposure); pooled is biased high (heterogeneity).
  - At N ≤ 25, τ fitted with a cutoff does not estimate 3/2; τ_app is a monotone function of R.
